"""DB 영구 번역 캐시 + 기계번역(Google).

문제 배경
─────────
Render의 파일시스템은 휘발성이라 JSON 파일 캐시는 재배포·재시작 때마다 사라진다.
또한 브리핑을 만들 때마다 수백 건의 Google 번역을 즉석 호출하면 느리고
속도 제한에 걸려 실패(→ 영어로 폴백)한다.

해결
────
번역 결과를 PostgreSQL `translations` 테이블에 저장한다.
  1) 메모리 캐시(_MEM) 조회  — 가장 빠름
  2) 미스 시 DB 조회         — 프로세스 시작 시 전체를 _MEM 으로 1회 선로딩
  3) 그래도 없으면 Google 번역 → DB + _MEM 에 저장
한 번 번역한 (문장, 언어) 쌍은 재배포·재시작 후에도 영구히 재사용된다.
"""
from __future__ import annotations

import hashlib
import logging
import threading
import time
from typing import Iterable

log = logging.getLogger("osint.translation")

# Google Translate 언어 코드 매핑 (내부 코드 → deep-translator 코드)
_GOOGLE_CODE = {
    "ko": "ko",
    "es": "es",
    "zh": "zh-CN",
    "ja": "ja",
    "fr": "fr",
    "de": "de",
    "en": "en",
}

# 번역 캐시를 적용할 언어 (영어 원문 제외)
TARGET_LANGS = ("ko", "es", "zh", "ja", "fr", "de")

# 프로세스 내 메모리 캐시: {(source_hash, lang): translated_text}
_MEM: dict[tuple[str, str], str] = {}
_LOADED = False
_LOCK = threading.RLock()

# ── 회로 차단기 ──
# Google 번역이 연속 실패하면(네트워크 다운·속도 제한) 일정 시간 호출을 멈춰
# 브리핑 빌드가 재시도로 수십 분 멈추는 것을 방지한다.
_FAIL_STREAK = 0
_FAIL_THRESHOLD = 6        # 연속 6회 실패 시 회로 개방
_COOLDOWN_SEC = 600       # 10분간 번역 호출 중단
_CIRCUIT_OPEN_UNTIL = 0.0


# ──────────────────────────────────────────────────────────────────
# 내부 유틸
# ──────────────────────────────────────────────────────────────────
def _hash(text: str) -> str:
    """원문을 정규화(앞뒤 공백 제거)한 뒤 SHA1 해시."""
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()


def _preload() -> None:
    """translations 테이블 전체를 메모리 캐시로 1회 선로딩."""
    global _LOADED
    if _LOADED:
        return
    with _LOCK:
        if _LOADED:
            return
        try:
            from app.core.database import SessionLocal
            from app.models.entities import Translation
            db = SessionLocal()
            try:
                rows = db.query(
                    Translation.source_hash,
                    Translation.lang,
                    Translation.translated_text,
                ).all()
                for h, lang, txt in rows:
                    if txt:
                        _MEM[(h, lang)] = txt
                log.info("번역 캐시 선로딩 완료: %d개 항목", len(_MEM))
            finally:
                db.close()
        except Exception as e:  # 테이블 미생성 등 — 캐시 없이 계속 진행
            log.warning("번역 캐시 선로딩 실패(무시): %s", e)
        _LOADED = True


def get_cached(text: str | None, lang: str) -> str | None:
    """캐시에서만 조회. 없으면 None (번역 호출 안 함)."""
    if not text or not text.strip():
        return None
    _preload()
    return _MEM.get((_hash(text), lang))


def _store(items: list[tuple[str, str, str]]) -> None:
    """items: [(원문, 언어, 번역결과), ...] → 메모리 + DB 저장."""
    if not items:
        return
    # 1) 메모리 캐시 먼저 갱신 (DB 실패해도 이번 세션에서는 재사용 가능)
    for src, lang, tr in items:
        _MEM[(_hash(src), lang)] = tr
    # 2) DB 영구 저장
    try:
        from app.core.database import SessionLocal
        from app.models.entities import Translation
        db = SessionLocal()
        try:
            for src, lang, tr in items:
                h = _hash(src)
                exists = (
                    db.query(Translation)
                    .filter(Translation.source_hash == h, Translation.lang == lang)
                    .first()
                )
                if exists:
                    exists.translated_text = tr
                else:
                    db.add(
                        Translation(
                            source_hash=h,
                            lang=lang,
                            source_text=src[:4000],
                            translated_text=tr,
                            engine="google",
                        )
                    )
            db.commit()
        except Exception as e:
            db.rollback()
            log.warning("번역 DB 저장 실패(%d건, 무시): %s", len(items), e)
        finally:
            db.close()
    except Exception as e:
        log.warning("번역 DB 세션 오류(무시): %s", e)


def _google(text: str, lang: str) -> str | None:
    """단일 문장 Google 번역. 2회 시도. 실패 시 None.

    연속 실패가 임계치를 넘으면 회로를 개방해 일정 시간 호출 자체를 건너뛴다.
    """
    global _FAIL_STREAK, _CIRCUIT_OPEN_UNTIL

    # 회로 개방 중이면 즉시 None (재시도로 빌드가 멈추는 것 방지)
    if time.time() < _CIRCUIT_OPEN_UNTIL:
        return None

    try:
        from deep_translator import GoogleTranslator
    except Exception as e:
        log.warning("deep-translator 임포트 실패: %s", e)
        return None

    target = _GOOGLE_CODE.get(lang, lang)
    for attempt in range(1, 3):
        try:
            out = GoogleTranslator(source="auto", target=target).translate(text)
            _FAIL_STREAK = 0  # 성공 — 실패 카운터 초기화
            if out and out.strip():
                return out.strip()
            return None
        except Exception as e:
            log.warning("Google 번역 실패 %d/2 (%s): %s", attempt, lang, e)
            if attempt < 2:
                time.sleep(1.0)

    # 2회 모두 실패
    _FAIL_STREAK += 1
    if _FAIL_STREAK >= _FAIL_THRESHOLD:
        _CIRCUIT_OPEN_UNTIL = time.time() + _COOLDOWN_SEC
        _FAIL_STREAK = 0
        log.warning("번역 회로 개방 — %d초간 Google 번역 호출을 중단합니다.", _COOLDOWN_SEC)
    return None


# ──────────────────────────────────────────────────────────────────
# 공개 API
# ──────────────────────────────────────────────────────────────────
def translate(text: str | None, lang: str) -> str:
    """캐시 우선 번역.

    캐시에 있으면 즉시 반환, 없으면 Google 번역 후 저장한다.
    번역이 완전히 실패하면 원문(영어)을 그대로 반환한다.
    """
    if not text or not text.strip():
        return text or ""
    if lang == "en":
        return text
    cached = get_cached(text, lang)
    if cached is not None:
        return cached
    out = _google(text, lang)
    if out and out.strip() and out.strip() != text.strip():
        _store([(text, lang, out)])
        return out
    return text


def warmup(
    texts: Iterable[str | None],
    langs: Iterable[str] = TARGET_LANGS,
    *,
    batch: int = 20,
) -> dict:
    """여러 문장 × 언어를 미리 번역해 캐시를 채운다.

    배치마다 DB에 커밋하므로 중간에 실패해도 진행분은 보존되고
    다음 호출에서 이어서 채운다. 이미 캐시에 있으면 건너뛴다.
    """
    _preload()

    # 중복 제거
    uniq: list[str] = []
    seen: set[str] = set()
    for t in texts:
        if t and t.strip() and t.strip() not in seen:
            seen.add(t.strip())
            uniq.append(t)

    stats = {"unique_texts": len(uniq), "cached_hit": 0, "translated": 0, "failed": 0}
    pending: list[tuple[str, str, str]] = []

    for lang in langs:
        if lang == "en":
            continue
        for text in uniq:
            if get_cached(text, lang) is not None:
                stats["cached_hit"] += 1
                continue
            out = _google(text, lang)
            if out and out.strip() and out.strip() != text.strip():
                pending.append((text, lang, out))
                stats["translated"] += 1
            else:
                stats["failed"] += 1
            if len(pending) >= batch:
                _store(pending)
                pending = []
    if pending:
        _store(pending)

    log.info("번역 워밍업 완료: %s", stats)
    return stats


def cache_size() -> int:
    """현재 메모리 캐시 항목 수."""
    _preload()
    return len(_MEM)
