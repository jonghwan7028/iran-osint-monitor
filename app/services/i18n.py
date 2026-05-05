"""Multi-lingual translation service with persistent file cache.

지원 언어: ko, en(원문), es, zh-CN, ja, fr, de.

전략:
  1) 캐시(app/data/translations.json) 조회 — hit 즉시 반환
  2) 한국어:
        a. 큐레이션 사전(SENTENCE_KO/PHRASE_REPLACEMENTS) 적용
        b. 한국어 비율이 50% 미만이면 Google MT 호출 후 사전 재적용
  3) 그 외 언어: Google MT 직호출
  4) MT 실패 시 영어 원문 반환 (절대 크래시하지 않음)
  5) 캐시는 호출자가 save_cache()로 명시 저장 (브리핑/지도 빌드 끝에서 1회)

이 모듈은 IO 안전: import 자체로는 디스크 IO/네트워크 IO를 발생시키지 않는다.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
from pathlib import Path
from typing import Iterable

from app.core.config import BASE_DIR

logger = logging.getLogger("osint.i18n")

CACHE_FILE: Path = BASE_DIR / "app" / "data" / "translations.json"

# UI에서 선택 가능한 언어 코드 (briefer/mapper와 일치)
SUPPORTED_LANGS: tuple[str, ...] = ("ko", "en", "es", "zh", "ja", "fr", "de")

# UI 코드 → deep-translator(Google) 코드. 'zh'는 Google이 'zh-CN'을 요구.
_GOOGLE_CODE: dict[str, str] = {
    "ko": "ko",
    "es": "es",
    "zh": "zh-CN",
    "ja": "ja",
    "fr": "fr",
    "de": "de",
}

# ── 캐시 상태 (메모리) ──
_cache: dict[str, str] | None = None
_cache_dirty: bool = False
_lock = threading.Lock()


def _load_cache() -> dict[str, str]:
    global _cache
    if _cache is not None:
        return _cache
    with _lock:
        if _cache is not None:
            return _cache
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, encoding="utf-8") as f:
                    _cache = json.load(f)
                    if not isinstance(_cache, dict):
                        _cache = {}
            except Exception as e:
                logger.warning("Translation cache load failed (%s) — starting empty", e)
                _cache = {}
        else:
            _cache = {}
    return _cache


def _cache_key(text: str, lang: str) -> str:
    h = hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:16]
    return f"{lang}:{h}"


def save_cache() -> None:
    """캐시를 디스크에 저장. 빌드 작업 끝에 한 번 호출하는 용도."""
    global _cache_dirty
    if _cache is None or not _cache_dirty:
        return
    with _lock:
        if not _cache_dirty:
            return
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            tmp = CACHE_FILE.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(_cache, f, ensure_ascii=False, indent=2)
            tmp.replace(CACHE_FILE)
            _cache_dirty = False
            logger.info("Translation cache saved: %d entries → %s", len(_cache), CACHE_FILE)
        except Exception as e:
            logger.warning("Translation cache save failed: %s", e)


# ── 언어별 본문 길이 휴리스틱 ──

_KO_RE = re.compile(r"[가-힣]")  # 한글 음절


def _korean_coverage_ratio(text: str) -> float:
    """비공백 문자 중 한글 음절 비율."""
    if not text:
        return 1.0
    significant = sum(1 for c in text if not c.isspace() and c not in ",.;:?!()[]{}'\"-/")
    if significant == 0:
        return 1.0
    korean = sum(1 for c in text if _KO_RE.match(c))
    return korean / significant


# ── 외부 API: 핵심 entry point ──


def translate(text: str | None, lang: str) -> str:
    """영어 원문 → 대상 언어 번역.
    `lang`이 'en' 또는 미지원 코드면 원문 반환.
    """
    if text is None:
        return ""
    text = str(text).strip()
    if not text or text == "-":
        return text or "-"

    lang = (lang or "").lower()
    if lang in ("", "en"):
        return text
    if lang not in _GOOGLE_CODE:
        return text  # 미지원 — 영어 폴백

    cache = _load_cache()
    key = _cache_key(text, lang)
    cached = cache.get(key)
    if cached is not None:
        return cached

    if lang == "ko":
        result = _translate_korean(text)
    else:
        mt = _google_translate(text, lang)
        result = mt if mt else text  # 실패 시 영어 폴백

    # 캐시 저장 가드:
    #  - 영어 원문이 그대로 반환된 경우(=실패)는 저장하지 않아 다음 빌드에서 재시도
    #  - 한국어인데 한국어 비율이 50% 미만(=사전 부분치환만 성공, MT 실패한 상태)도
    #    캐시하지 않음 → 네트워크가 회복된 다음 빌드에서 자연스레 MT 재시도
    should_cache = bool(result) and result != text
    if should_cache and lang == "ko" and _korean_coverage_ratio(result) < 0.50:
        should_cache = False
    if should_cache:
        global _cache_dirty
        with _lock:
            cache[key] = result
            _cache_dirty = True

    return result


def translate_many(texts: Iterable[str | None], lang: str) -> list[str]:
    """텍스트 묶음 번역. 호출 끝에 save_cache()는 별도 호출 필요."""
    return [translate(t, lang) for t in texts]


def warmup_cache() -> int:
    """캐시 파일을 미리 메모리로 로드. 반환: 엔트리 수."""
    return len(_load_cache())


# ── 내부 헬퍼 ──


def _translate_korean(text: str) -> str:
    """한국어 번역: 큐레이션 사전 → 부족 시 Google MT → 사전 재적용."""
    # 1) 정확 일치 큐레이션
    try:
        from app.services.ko_sentences import SENTENCE_KO
        if text in SENTENCE_KO:
            return SENTENCE_KO[text]
        stripped = text.rstrip(".")
        if stripped in SENTENCE_KO:
            return SENTENCE_KO[stripped]
    except Exception:
        pass

    # 2) 사전 기반 phrase 치환 (기존 ko_translate.translate_sentence)
    try:
        from app.services.ko_translate import translate_sentence as _dict_translate_sentence
        dict_result = _dict_translate_sentence(text)
    except Exception as e:
        logger.warning("Korean dict translate raised: %s", e)
        dict_result = text

    # 한국어 비율이 충분하면 그대로 사용
    if _korean_coverage_ratio(dict_result) >= 0.50:
        return dict_result

    # 3) Google MT 폴백
    mt_result = _google_translate(text, "ko")
    if not mt_result:
        # MT 실패 — 사전 결과(영어가 섞여있어도)라도 반환
        return dict_result if dict_result != text else text

    # 4) MT 결과에 사전 재적용 (Google이 놓친 군사·고유명사 보정).
    #    영어 잔존이 있을 때만 의미가 있으므로 한국어 비율 체크 후 적용.
    if _korean_coverage_ratio(mt_result) < 0.95:
        try:
            from app.services.ko_translate import translate_sentence as _dict_translate_sentence
            mt_result = _dict_translate_sentence(mt_result)
        except Exception:
            pass

    return mt_result


_translator_cache: dict[str, object] = {}


def _get_google_translator(lang: str):
    """deep-translator 인스턴스 캐싱 (재사용 안전)."""
    code = _GOOGLE_CODE.get(lang)
    if not code:
        return None
    if lang in _translator_cache:
        return _translator_cache[lang]
    try:
        from deep_translator import GoogleTranslator
        t = GoogleTranslator(source="en", target=code)
        _translator_cache[lang] = t
        return t
    except Exception as e:
        logger.warning("GoogleTranslator init failed (lang=%s): %s", lang, e)
        return None


def _google_translate(text: str, lang: str) -> str | None:
    """Google 번역 호출. 실패 시 None 반환 (절대 raise 하지 않음).
    deep-translator는 5000자 제한이 있어 긴 텍스트는 청크 단위 분할.
    """
    if not text:
        return None
    translator = _get_google_translator(lang)
    if translator is None:
        return None

    # 5000자 미만이면 일괄 처리
    if len(text) <= 4500:
        try:
            result = translator.translate(text)
            return result if isinstance(result, str) and result.strip() else None
        except Exception as e:
            logger.info("Google translate failed (lang=%s, len=%d): %s", lang, len(text), e)
            return None

    # 긴 텍스트: 문장 단위 분할
    chunks: list[str] = []
    buf: list[str] = []
    cur_len = 0
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if cur_len + len(sentence) > 4500 and buf:
            chunks.append(" ".join(buf))
            buf = [sentence]
            cur_len = len(sentence)
        else:
            buf.append(sentence)
            cur_len += len(sentence) + 1
    if buf:
        chunks.append(" ".join(buf))

    out_parts: list[str] = []
    for c in chunks:
        try:
            r = translator.translate(c)
            if isinstance(r, str) and r.strip():
                out_parts.append(r)
            else:
                return None  # 부분 실패면 전체 폴백
        except Exception as e:
            logger.info("Google translate chunk failed (lang=%s): %s", lang, e)
            return None
    return " ".join(out_parts) if out_parts else None
