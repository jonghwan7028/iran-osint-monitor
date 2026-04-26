"""
피해요약(damage_summary) 텍스트의 톤을 사실 보고 형식으로 정돈한다.

목적:
- 사건목록 표(셀)에 자극적 표현(시신 묘사, 사지절단, 잔혹한 형용사, 큰 사상자 수의 강조 등)이
  그대로 노출되는 것을 방지한다.
- 데이터 자체(원본 영문 등)는 보존하고 표·팝업·브리핑에 표시하기 위한
  정제된(softened) 변형만 따로 제공한다.

설계 원칙:
- 사실(숫자, 위치, 무기, 결과)은 유지한다.
- 잔혹·선정적 어휘만 중성적/사실적 표현으로 바꾼다.
- 셀 길이 제한(하이라이트 모드)은 별도 함수로 제공한다.
- 한·영 모두 처리한다.
"""
from __future__ import annotations

import re
from typing import Optional

# ---------------------------------------------------------------------------
# 1) 영어 원문 정제
# ---------------------------------------------------------------------------

# 잔혹·선정적 형용사·구문 → 중립적 표현
_EN_SOFTEN: list[tuple[str, str]] = [
    # 시신·신체 묘사
    (r"\bcharred\s+bodies?\b", "casualties"),
    (r"\bdismembered\b", "killed"),
    (r"\bmutilated\b", "killed"),
    (r"\bdecapitated\b", "killed"),
    (r"\bbody parts?\b", "remains"),
    (r"\bcorpses?\b", "deceased"),
    (r"\bblood-?soaked\b", "damaged"),
    (r"\bgore\b", ""),
    (r"\bgrisly\b", ""),
    (r"\bgruesome\b", ""),
    (r"\bgraphic\b", ""),
    (r"\bhorrific\b", "severe"),
    (r"\bhorrendous\b", "severe"),
    (r"\bbrutal(?:ly)?\b", ""),
    (r"\bsavage(?:ly)?\b", ""),
    (r"\bmassacred?\b", "killed"),
    (r"\bslaughtered?\b", "killed"),
    (r"\bcarnage\b", "casualties"),
    (r"\bbloodshed\b", "casualties"),
    (r"\bblood\s+everywhere\b", "casualties reported"),
    # 강조·과장 부사
    (r"\bhorribly\b", ""),
    (r"\bterribly\b", ""),
    (r"\bdevastatingly\b", "severely"),
    (r"\bcatastrophic(?:ally)?\b", "severe"),
    (r"\bapocalyptic\b", "extensive"),
    # 자극적 동사
    (r"\btore\s+apart\b", "destroyed"),
    (r"\bripped\s+apart\b", "destroyed"),
    (r"\bblown\s+to\s+pieces\b", "destroyed"),
    (r"\bobliterated\b", "destroyed"),
    (r"\bvaporized\b", "destroyed"),
    (r"\bannihilated\b", "destroyed"),
    (r"\bwiped\s+out\b", "destroyed"),
    (r"\bexterminated\b", "killed"),
    (r"\bexecutions?\b", "killings"),
    (r"\bbeheaded?\b", "killed"),
    # 군중 표현
    (r"\bbloodbath\b", "heavy casualties"),
    (r"\bdeath toll soared\b", "casualties rose"),
    (r"\bdeath toll skyrocketed\b", "casualties rose"),
    # 어린이·여성 강조 (사실은 유지하되 선정적 강조 제거)
    (r"\b(innocent|defenseless)\s+(children|women|civilians)\b", r"\2"),
    (r"\bbabies?\s+killed\b", "children killed"),
]

# 한국어 정제
_KO_SOFTEN: list[tuple[str, str]] = [
    # 잔혹 묘사 — 단어보다 어구 단위로 치환
    (r"불에\s*탄\s*시신(?:들|이|을|은|들이|들을)?", "사상자"),
    (r"훼손된?\s*시신(?:들|이|을|은|들이|들을)?", "사망자"),
    (r"절단된?\s*시신(?:들|이|을|은|들이|들을)?", "사망자"),
    (r"산산조각\s*난?", "파괴된"),
    (r"갈기갈기\s*", ""),
    (r"형체를\s*알아볼\s*수\s*없는", "심각하게 손상된"),
    # "잔혹한 학살로" 같은 어구 → 자연스러운 수동형
    (r"잔혹한?\s*학살(?:로|이|을|은)?", "다수 사망 사건"),
    (r"피바다(?:로|가|를|는)?", "다수 사상"),
    (r"피로\s*물든", "피해 입은"),
    # 형용사 단독 — 문장 의미 손상 최소화
    (r"잔혹한?\s+", ""),
    (r"끔찍한?\s+", ""),
    (r"처참한?\s+", "심각한 "),
    (r"잔악한?\s+", ""),
    (r"무참한?\s+", ""),
    # 부사
    (r"끔찍하게", "심각하게"),
    (r"무자비하게", ""),
    (r"잔혹하게", ""),
    # 관행적 표현 정리 — 동사 보존
    (r"학살(?:했|당했)", "다수 살해"),
    (r"참수(?:했|당했|되었)", "사망"),
    (r"사지\s*절단(?:되었|당했|했)", "사망"),
    # 시체 → 사망자 (수량 단위 보존)
    (r"시체\s+(\d+)\s*구(?:가|는|를|이|은)?", r"사망자 \1명이"),
    (r"시신\s+(\d+)\s*구(?:가|는|를|이|은)?", r"사망자 \1명이"),
    (r"시체(?:가|는|를|들)", "사망자"),
    (r"시체", "사망자"),
    # 조사 정리 — 숫자+명 다음 잘못된 조사
    (r"(\d+)\s*명가\b", r"\1명이"),
    (r"(\d+)\s*명을\b", r"\1명을"),  # 보존
]

_PUNCT_FIX = [
    (r"\s+([,.;:])", r"\1"),
    (r"\(\s*\)", ""),
    (r"\s{2,}", " "),
]


def soften_english(text: str) -> str:
    """영어 피해요약을 사실 보고 형식으로 정제."""
    if not text:
        return text or ""
    out = text
    for pat, repl in _EN_SOFTEN:
        out = re.sub(pat, repl, out, flags=re.IGNORECASE)
    for pat, repl in _PUNCT_FIX:
        out = re.sub(pat, repl, out)
    return out.strip()


def soften_korean(text: str) -> str:
    """한국어 피해요약을 사실 보고 형식으로 정제."""
    if not text:
        return text or ""
    out = text
    for pat, repl in _KO_SOFTEN:
        out = re.sub(pat, repl, out)
    for pat, repl in _PUNCT_FIX:
        out = re.sub(pat, repl, out)
    return out.strip()


# ---------------------------------------------------------------------------
# 2) 표 셀용 짧은 요약 (긴 본문은 팝업·브리핑에서 보도록)
# ---------------------------------------------------------------------------

def _truncate_at_sentence(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    # 문장 끝(., 。, ;, !) 우선
    end_marks = [m.end() for m in re.finditer(r"[.;!。][\s$]", text[:max_len + 5])]
    if end_marks:
        cut = max(e for e in end_marks if e <= max_len + 1)
        return text[:cut].rstrip() + " …"
    # 콤마 단위로
    comma = text.rfind(",", 0, max_len)
    if comma > max_len // 2:
        return text[:comma].rstrip() + " …"
    # 공백 단위로
    sp = text.rfind(" ", 0, max_len)
    if sp > 0:
        return text[:sp].rstrip() + " …"
    return text[:max_len].rstrip() + "…"


def short_cell_korean(text: str | None, max_len: int = 80) -> str:
    """표 셀 표시용: 정제 + 길이 컷."""
    if not text or text == "-":
        return "-"
    softened = soften_korean(text)
    return _truncate_at_sentence(softened, max_len)


def short_cell_english(text: str | None, max_len: int = 90) -> str:
    """Table cell display (English): soften + truncate."""
    if not text or text == "-":
        return "-"
    softened = soften_english(text)
    return _truncate_at_sentence(softened, max_len)


# ---------------------------------------------------------------------------
# 3) 사상자 수가 큰 경우의 추가 안전장치
# ---------------------------------------------------------------------------

_NUMBER_NEAR_KILLED_RE = re.compile(
    r"(\d{2,5})\s*(?:명|people|persons?|civilians?|soldiers?)?\s*"
    r"(killed|사망|deceased|dead)",
    flags=re.IGNORECASE,
)


def has_high_casualty_signal(text: Optional[str]) -> bool:
    """수치적으로 큰 사상자 신호가 있는지(표 표시 시 경고 마커용)."""
    if not text:
        return False
    for m in _NUMBER_NEAR_KILLED_RE.finditer(text):
        try:
            if int(m.group(1)) >= 50:
                return True
        except ValueError:
            continue
    return False
