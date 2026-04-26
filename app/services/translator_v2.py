"""
영어 → 한국어 문장 번역 보강 모듈.

문제:
- 기존 ko_translate.translate_sentence() 는 사전(SENTENCE_KO) 완전 일치가 없으면
  PHRASE_REPLACEMENTS (단어 단위 치환)만 수행한다.
- 새로 수집된 영어 문장(Google News, GDELT)은 사전에 없으므로,
  결과가 영어와 한국어가 뒤섞인 부자연스러운 문장이 된다.

해결:
- 우선순위 기반 번역 파이프라인을 도입한다.
  1) 완전 일치 사전 (ko_sentences.SENTENCE_KO)
  2) 정규식 패턴(주어-동사-목적어 구조의 짧은 보도 문장) → 한국어 SOV 재구성
  3) 어휘 치환 (PHRASE_REPLACEMENTS) 후 어순 정리

이 모듈은 ko_translate.translate_sentence 를 *교체*하지 않고,
보조 패스(translate_sentence_better) 로 호출되어
기존 사전 시드(완전 일치)는 그대로 보존한다.
"""
from __future__ import annotations

import re
from typing import Optional

# ---------------------------------------------------------------------------
# 1) 보조 어휘 (translate_sentence 가 놓치는 흔한 영문 표현)
# ---------------------------------------------------------------------------

_REPORTING_VERBS = {
    "said": "발표함",
    "says": "발표함",
    "stated": "발표함",
    "announced": "발표함",
    "reported": "보도됨",
    "reports": "보도됨",
    "claimed": "주장함",
    "claims": "주장함",
    "denied": "부인함",
    "denies": "부인함",
    "confirmed": "확인함",
    "confirms": "확인함",
    "warned": "경고함",
    "warns": "경고함",
    "vowed": "공언함",
    "threatened": "위협함",
}

_ATTACK_VERBS = {
    "struck": "타격함",
    "strikes": "타격함",
    "hit": "타격함",
    "attacked": "공격함",
    "attacks": "공격함",
    "launched": "발사함",
    "fired": "발사함",
    "targeted": "표적으로 함",
    "bombed": "폭격함",
    "destroyed": "파괴함",
    "damaged": "손상시킴",
    "intercepted": "요격함",
    "downed": "격추함",
    "killed": "사망케 함",
    "wounded": "부상케 함",
    "captured": "나포함",
    "seized": "나포함",
}

_NOUN_FIX = {
    # 흔히 남는 영어 명사 — 어구 단위
    "missile strike": "미사일 공격",
    "missile attack": "미사일 공격",
    "drone strike": "무인기 공격",
    "drone attack": "무인기 공격",
    "drone": "드론",
    "drones": "드론",
    "airstrike": "공습",
    "air strike": "공습",
    "air strikes": "공습",
    "airstrikes": "공습",
    "rocket attack": "로켓 공격",
    "cyber attack": "사이버 공격",
    "cyberattack": "사이버 공격",
    "naval engagement": "해상 교전",
    "ground operation": "지상 작전",
    "military operation": "군사 작전",
    "ceasefire deal": "휴전 합의",
    "ceasefire": "휴전",
    "peace talks": "평화 회담",
    "nuclear deal": "핵 합의",
    "nuclear program": "핵 프로그램",
    "nuclear facility": "핵시설",
    "nuclear site": "핵시설",
    "nuclear sites": "핵시설들",
    "nuclear facilities": "핵시설들",
    "missile facility": "미사일 시설",
    "missile facilities": "미사일 시설",
    "ballistic missile": "탄도미사일",
    "ballistic missiles": "탄도미사일",
    "cruise missile": "순항미사일",
    "cruise missiles": "순항미사일",
    "oil tanker": "유조선",
    "oil tankers": "유조선",
    "oil refinery": "정유시설",
    "oil refineries": "정유시설",
    "oil facility": "석유 시설",
    "oil facilities": "석유 시설",
    "military base": "군사기지",
    "military bases": "군사기지",
    "air base": "공군기지",
    "air bases": "공군기지",
    "us air base": "미군 공군기지",
    "us base": "미군기지",
    "us bases": "미군기지",
    "naval base": "해군기지",
    "us forces": "미군",
    "us troops": "미군",
    "us military": "미군",
    "us navy": "미 해군",
    "us army": "미 육군",
    "us marines": "미 해병대",
    "iranian forces": "이란군",
    "iranian troops": "이란군",
    "iranian military": "이란군",
    "iranian officials": "이란 당국자",
    "iranian official": "이란 당국자",
    "us officials": "미 당국자",
    "us official": "미 당국자",
    "white house": "백악관",
    "pentagon": "국방부(펜타곤)",
    "state department": "미 국무부",
    "supreme leader": "최고지도자",
    "ayatollah": "아야톨라",
    "revolutionary guards": "혁명수비대",
    "revolutionary guard": "혁명수비대",
    "civilian infrastructure": "민간 인프라",
    "residential area": "주거 지역",
    "residential areas": "주거 지역",
    "residential building": "주거 건물",
    "residential buildings": "주거 건물",
    "hezbollah positions": "헤즈볼라 진지",
    "casualties reported": "사상자 보고됨",
    "casualties": "사상자",
    "deaths": "사망자",
    "fatalities": "사망자",
    "injured": "부상자",
    "wounded": "부상자",
    "civilians": "민간인",
    "civilian": "민간인",
    "soldiers": "장병",
    "soldier": "장병",
    "officers": "장교",
    "officer": "장교",
    "explosion": "폭발",
    "explosions": "폭발",
    "blast": "폭발",
    "fire": "화재",
    "fires": "화재",
    "smoke": "연기",
    "tensions": "긴장",
    "tension": "긴장",
    "escalation": "확전",
    "retaliation": "보복",
    "response": "대응",
    "warning": "경고",
    "threat": "위협",
    "deal": "합의",
    "agreement": "합의",
    "talks": "회담",
    "negotiations": "협상",
    "negotiation": "협상",
    "sanctions": "제재",
    "sanction": "제재",
    "embargo": "금수",
    "blockade": "봉쇄",
    "southern lebanon": "남부 레바논",
    "northern israel": "북부 이스라엘",
    "overnight": "야간",
    "late at night": "야간",
    "early morning": "이른 새벽",
    # 국가·도시
    "iran": "이란",
    "iraq": "이라크",
    "israel": "이스라엘",
    "us": "미국",
    "the us": "미국",
    "united states": "미국",
    "saudi arabia": "사우디아라비아",
    "houthis": "후티 반군",
    "houthi": "후티 반군",
    "hezbollah": "헤즈볼라",
    "missile": "미사일",
    "missiles": "미사일",
    "iranian": "이란의",
    "iran's": "이란의",
    "israeli": "이스라엘의",
    "israel's": "이스라엘의",
    "american": "미국의",
    "lebanese": "레바논의",
    "syrian": "시리아의",
    "iraqi": "이라크의",
    "saudi": "사우디의",
    "yemeni": "예멘의",
    "people": "사람",
    "person": "사람",
    "tehran": "테헤란",
    "washington": "워싱턴",
    "jerusalem": "예루살렘",
    "beirut": "베이루트",
    "damascus": "다마스쿠스",
    "baghdad": "바그다드",
    "riyadh": "리야드",
    "doha": "도하",
    "ankara": "앙카라",
    "moscow": "모스크바",
    "beijing": "베이징",
    "tel aviv": "텔아비브",
    "natanz": "나탄즈",
    "fordow": "포르도",
    "isfahan": "이스파한",
    "bandar abbas": "반다르아바스",
    "haifa": "하이파",
    "the gulf": "걸프 해역",
    "persian gulf": "페르시아만",
    "strait of hormuz": "호르무즈 해협",
    "red sea": "홍해",
    "middle east": "중동",
    "the region": "역내",
    "shipping": "상선",
    # 동사·동작
    "condemned": "비난함",
    "condemns": "비난함",
    "warned": "경고함",
    "vowed": "공언함",
    "threatened": "위협함",
    "intercepted": "요격함",
    "downed": "격추함",
    "shot down": "격추함",
    "captured": "나포함",
    "seized": "나포함",
    "destroyed": "파괴함",
    "damaged": "손상시킴",
    "killed": "사망",
    "wounded": "부상",
    "struck": "타격",
    "hit": "타격",
    "attacked": "공격",
    "bombed": "폭격",
    "fired": "발사",
    "launched": "발사",
    "targeted": "표적",
    "reported": "보도됨",
    "to close": "폐쇄",
    "close": "폐쇄",
    "reopens": "재개",
    # 잔존 형용사
    "at least": "최소",
    "at least 80": "최소 80",
    "at least 100": "최소 100",
    "over": "이상",
    "more than": "이상",
    "nearly": "약",
    "approximately": "약",
    "about": "약",
    "around": "약",
    "amid": "중",
    "during": "동안",
}

_PREP_LOC = {
    " in ": " ",
    " at ": " ",
    " near ": " 인근 ",
    " over ": " 상공 ",
    " inside ": " 내부 ",
    " around ": " 주변 ",
    " into ": " ",
}


# ---------------------------------------------------------------------------
# 2) 대표 패턴 — A struck B in/at C / A killed N people in B
# ---------------------------------------------------------------------------

# A killed N (people|civilians|soldiers) in/at B
_PAT_KILLED_N = re.compile(
    r"^([A-Z][A-Za-z\u00C0-\uFFFF\.\- ]+?)\s+"
    r"(killed|wounded|injured)\s+"
    r"(\d{1,5})\s+"
    r"(people|civilians?|soldiers?|troops?|officers?|militants?|fighters?|persons?)"
    r"(?:\s+in\s+([A-Za-z\u00C0-\uFFFF, \-']+?))?"
    r"\.?$",
    flags=re.IGNORECASE,
)

# A struck/hit/attacked B (in C)?
_PAT_ATTACK = re.compile(
    r"^([A-Z][A-Za-z\u00C0-\uFFFF\.\- ]+?)\s+"
    r"(struck|hit|attacked|targeted|bombed|launched\s+strikes\s+on)\s+"
    r"([A-Za-z\u00C0-\uFFFF \-,'’]+?)"
    r"(?:\s+in\s+([A-Za-z\u00C0-\uFFFF, \-']+?))?"
    r"\.?$",
    flags=re.IGNORECASE,
)

# A fired/launched WEAPON at/on TARGET (in LOC)?
_PAT_FIRE = re.compile(
    r"^([A-Z][A-Za-z\u00C0-\uFFFF\.\- ]+?)\s+"
    r"(fired|launched)\s+"
    r"([A-Za-z\u00C0-\uFFFF \-,'’]+?)\s+"
    r"(?:at|on|against|toward|towards)\s+"
    r"([A-Za-z\u00C0-\uFFFF \-,'’]+?)"
    r"(?:\s+in\s+([A-Za-z\u00C0-\uFFFF, \-']+?))?"
    r"\.?$",
    flags=re.IGNORECASE,
)

# N (people|civilians) (were)? killed/wounded in B
_PAT_PASSIVE_KILLED = re.compile(
    r"^(\d{1,5})\s+"
    r"(people|civilians?|soldiers?|troops?|officers?|militants?|fighters?|persons?)\s+"
    r"(?:were\s+|are\s+|have\s+been\s+)?"
    r"(killed|wounded|injured)"
    r"(?:\s+in\s+([A-Za-z\u00C0-\uFFFF, \-']+?))?"
    r"\.?$",
    flags=re.IGNORECASE,
)


_VERB_KO = {
    "killed": "사망함",
    "wounded": "부상함",
    "injured": "부상함",
    "struck": "타격",
    "hit": "타격",
    "attacked": "공격",
    "targeted": "표적 공격",
    "bombed": "폭격",
}


def _ko_actor(s: str) -> str:
    """작은 actor 어구를 한국어로."""
    s = s.strip().rstrip(".")
    low = s.lower()
    mapping = {
        "iran": "이란",
        "israel": "이스라엘",
        "the united states": "미국",
        "united states": "미국",
        "the us": "미국",
        "us": "미국",
        "hezbollah": "헤즈볼라",
        "houthis": "후티 반군",
        "houthi": "후티 반군",
        "irgc": "IRGC",
        "centcom": "미 중부사령부",
        "idf": "이스라엘방위군",
        "saudi arabia": "사우디",
        "uae": "UAE",
        "turkey": "튀르키예",
        "iraq": "이라크",
    }
    if low in mapping:
        return mapping[low]
    # 표제어 첫 글자 대문자 보존
    return s


def _ko_target(s: str) -> str:
    s = s.strip().rstrip(".").rstrip(",")
    low = s.lower()
    if low in _NOUN_FIX:
        return _NOUN_FIX[low]
    # 부분 치환
    out = s
    for en, ko in sorted(_NOUN_FIX.items(), key=lambda kv: -len(kv[0])):
        # 단어 경계 부분 치환 (대소문자 무시)
        out = re.sub(r"(?<!\w)" + re.escape(en) + r"(?!\w)", ko, out, flags=re.IGNORECASE)
    return out


def _ko_location(s: str | None) -> str:
    if not s:
        return ""
    out = s.strip().rstrip(".").rstrip(",")
    low = out.lower()
    if low in _NOUN_FIX:
        return _NOUN_FIX[low]
    for en, ko in sorted(_NOUN_FIX.items(), key=lambda kv: -len(kv[0])):
        out = re.sub(r"(?<!\w)" + re.escape(en) + r"(?!\w)", ko, out, flags=re.IGNORECASE)
    return out


# ---------------------------------------------------------------------------
# 3) 문장 단위 향상 번역
# ---------------------------------------------------------------------------

def _has_korean(text: str) -> bool:
    return bool(re.search(r"[\uAC00-\uD7A3\u1100-\u11FF]", text))


def _ratio_korean(text: str) -> float:
    if not text:
        return 0.0
    ko = sum(1 for c in text if "\uAC00" <= c <= "\uD7A3")
    total = sum(1 for c in text if c.isalpha() or "\uAC00" <= c <= "\uD7A3")
    if total == 0:
        return 0.0
    return ko / total


def translate_sentence_better(text: Optional[str]) -> str:
    """
    영어 문장을 자연스러운 한국어로 변환한다.
    1) 영어 톤 정제 (잔혹·자극적 표현 → 사실적 표현)
    2) 완전 일치 사전 → 그대로
    3) 패턴 매칭 → SOV 한국어 재구성
    4) 어휘 치환 + 정리
    """
    if not text:
        return "-"
    text = text.strip()

    # 1) 영어 잔혹 표현을 먼저 사실 표현으로 정제 (한국어 번역 전)
    try:
        from app.services.tone_softener import soften_english
        text = soften_english(text)
    except Exception:
        pass

    # 2) 완전 일치 사전
    try:
        from app.services.ko_sentences import SENTENCE_KO
        if text in SENTENCE_KO:
            return SENTENCE_KO[text]
        stripped = text.rstrip(".")
        if stripped in SENTENCE_KO:
            return SENTENCE_KO[stripped]
    except Exception:
        pass

    # 3) 패턴 매칭
    ko = _try_pattern_translate(text)
    if ko:
        return ko

    # 4) 기존 PHRASE 치환 + 어휘 보강
    try:
        from app.services.ko_translate import translate_sentence as _legacy
        legacy = _legacy(text)
    except Exception:
        legacy = text

    legacy = _enhance_lexical(legacy)
    legacy = _cleanup(legacy)
    return legacy


def _try_pattern_translate(text: str) -> Optional[str]:
    """대표 보도 문장 패턴 → SOV 한국어."""
    t = text.rstrip(".").strip()

    # passive: "120 people were killed in Tehran"
    m = _PAT_PASSIVE_KILLED.match(t)
    if m:
        n, what, verb, where = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
        what_ko = _ko_target(what.lower())
        verb_ko = _VERB_KO.get(verb, verb)
        where_ko = _ko_location(where) if where else ""
        if where_ko:
            return f"{where_ko}에서 {what_ko} {n}명 {verb_ko}."
        return f"{what_ko} {n}명 {verb_ko}."

    # "Israel killed 12 people in Beirut"
    m = _PAT_KILLED_N.match(t)
    if m:
        actor, verb, n, what, where = (
            m.group(1), m.group(2).lower(), m.group(3), m.group(4), m.group(5)
        )
        actor_ko = _ko_actor(actor)
        what_ko = _ko_target(what.lower())
        verb_ko = _VERB_KO.get(verb, verb)
        where_ko = _ko_location(where) if where else ""
        if where_ko:
            return f"{actor_ko}, {where_ko}에서 {what_ko} {n}명 {verb_ko}."
        return f"{actor_ko}, {what_ko} {n}명 {verb_ko}."

    # "Iran struck Tel Aviv" / "US attacked Iranian nuclear sites in Natanz"
    m = _PAT_ATTACK.match(t)
    if m:
        actor, verb, target, where = (
            m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        )
        actor_ko = _ko_actor(actor)
        verb_norm = re.sub(r"\s+", " ", verb)
        verb_ko = _VERB_KO.get(verb_norm, "공격")
        target_ko = _ko_target(target)
        where_ko = _ko_location(where) if where else ""
        if where_ko:
            return f"{actor_ko}, {where_ko}의 {target_ko}을(를) {verb_ko}."
        return f"{actor_ko}, {target_ko}을(를) {verb_ko}."

    return None


def _enhance_lexical(text: str) -> str:
    """남은 영어 어휘를 추가로 한국어로."""
    out = text
    # 흔한 어구 (먼저 어구 단위)
    phrase_map = {
        "no physical damage": "물리적 피해 없음",
        "no immediate damage": "즉각적 피해 없음",
        "no casualties reported": "인명 피해 보고 없음",
        "no casualties": "인명 피해 없음",
        "minor damage": "경미한 피해",
        "major damage": "주요 피해",
        "severe damage": "심각한 피해",
        "casualties reported": "사상자 보고됨",
        "first confirmed": "최초 확인된",
        "remains everywhere": "현장 내 다수의 잔해",
        "everywhere": "곳곳에",
        "nationwide": "전국",
        "in southern lebanon": "남부 레바논에서",
        "in northern israel": "북부 이스라엘에서",
        "early morning": "이른 새벽",
        "late at night": "야간",
    }
    for en, ko in sorted(phrase_map.items(), key=lambda kv: -len(kv[0])):
        out = re.sub(re.escape(en), ko, out, flags=re.IGNORECASE)
    # 큰 단위부터
    for en, ko in sorted(_NOUN_FIX.items(), key=lambda kv: -len(kv[0])):
        out = re.sub(r"(?<!\w)" + re.escape(en) + r"(?!\w)", ko, out, flags=re.IGNORECASE)
    for en, ko in _ATTACK_VERBS.items():
        out = re.sub(r"(?<!\w)" + re.escape(en) + r"(?!\w)", ko, out, flags=re.IGNORECASE)
    for en, ko in _REPORTING_VERBS.items():
        out = re.sub(r"(?<!\w)" + re.escape(en) + r"(?!\w)", ko, out, flags=re.IGNORECASE)
    # 전치사 컨텍스트
    for en, ko in _PREP_LOC.items():
        out = out.replace(en, ko)
    return out


def _cleanup(text: str) -> str:
    out = text
    # 잔존 영어 관사·be동사 정리
    out = re.sub(r"\b(the|a|an)\s+", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\b(is|are|was|were|be|been|being)\b", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\bof\b", "의", out, flags=re.IGNORECASE)
    out = re.sub(r"\band\b", "및", out, flags=re.IGNORECASE)
    # 전치사 — 한국어 조사 형태로
    out = re.sub(r"\bat\b", "에서", out, flags=re.IGNORECASE)
    out = re.sub(r"\bin\b", "에서", out, flags=re.IGNORECASE)
    out = re.sub(r"\bto\b", "에", out, flags=re.IGNORECASE)
    out = re.sub(r"\bon\b", "에", out, flags=re.IGNORECASE)
    out = re.sub(r"\bby\b", "에 의해", out, flags=re.IGNORECASE)
    out = re.sub(r"\bfor\b", "을 위한", out, flags=re.IGNORECASE)
    out = re.sub(r"\bwith\b", "와", out, flags=re.IGNORECASE)
    out = re.sub(r"\bfrom\b", "에서", out, flags=re.IGNORECASE)
    out = re.sub(r"\s+", " ", out)
    out = re.sub(r"\s+([,.;:?!])", r"\1", out)
    out = out.replace(" .", ".").replace(" ,", ",")
    # 한국어 조사 중복 제거
    out = re.sub(r"(에서)\s+(에서)", r"\1", out)
    out = re.sub(r"(에)\s+(에)", r"\1", out)
    out = out.strip()
    if out and out[-1] not in ".!?。":
        out += "."
    return out
