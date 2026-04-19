"""용어 사전 (Glossary) 서비스.

사용자가 사건 목록/타임라인에서 공격수단(미사일 종류 등) 또는 표적을 클릭할 때
간단한 한국어 설명과 위키피디아 링크를 제공한다.

- 사전에 등록된 용어는 짧은 설명(2-3문장)과 한/영 위키 링크를 리턴
- 없는 용어는 위키피디아 검색 URL로 폴백한다 (한/영 둘 다)
- 용어 매칭은 "부분 일치 (case-insensitive)" 로 수행한다
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

# key: 정규화된 소문자 키 (영/한 모두), value: 설명+위키링크
# NOTE: 이 사전은 점진적으로 확장하여 미래 학술/보고서 인용 시 활용한다.
_GLOSSARY: dict[str, dict[str, str]] = {
    # ──────────── 이란측 공격 수단 ────────────
    "shahed-136": {
        "category": "weapon",
        "name_ko": "샤헤드-136 자폭드론",
        "name_en": "Shahed-136",
        "desc_ko": "이란이 개발한 일회용 자폭 무인기(배회탄약)로, 약 2,000~2,500km 사거리와 40~50kg의 탄두를 가진다. 저고도로 군집 비행하며 방공망을 포화 공격하는 전술에 사용된다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/샤헤드_136",
        "wiki_en": "https://en.wikipedia.org/wiki/HESA_Shahed_136",
    },
    "shahed": {
        "category": "weapon",
        "name_ko": "샤헤드 계열 무인기",
        "name_en": "Shahed family UAVs",
        "desc_ko": "이란 HESA사가 운용/개발한 무인기 계열로 정찰·자폭·공격 임무를 수행한다. 대표 모델은 샤헤드-129, 샤헤드-136 등이다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/샤헤드_136",
        "wiki_en": "https://en.wikipedia.org/wiki/HESA_Shahed_136",
    },
    "fattah": {
        "category": "weapon",
        "name_ko": "파타흐 극초음속 미사일",
        "name_en": "Fattah hypersonic missile",
        "desc_ko": "이란이 2023년 공개한 극초음속 준중거리 탄도미사일로, 사거리 약 1,400km·속도 마하 13~15를 주장한다. 활강 재돌입체(HGV)로 요격 회피를 표방한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/파타흐_(미사일)",
        "wiki_en": "https://en.wikipedia.org/wiki/Fattah_(missile)",
    },
    "khorramshahr": {
        "category": "weapon",
        "name_ko": "호람샤흐르 탄도미사일",
        "name_en": "Khorramshahr MRBM",
        "desc_ko": "이란의 액체연료 중거리 탄도미사일로 사거리는 약 2,000km, 탄두중량 1,500~1,800kg 수준이다. 분리형 탄두(MIRV 유사)를 일부 채택한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/호람샤흐르_(미사일)",
        "wiki_en": "https://en.wikipedia.org/wiki/Khorramshahr_(missile)",
    },
    "sejjil": {
        "category": "weapon",
        "name_ko": "세질 고체연료 탄도미사일",
        "name_en": "Sejjil",
        "desc_ko": "이란 최초의 고체연료 2단 중거리 탄도미사일로, 사거리 약 2,000km. 발사 준비시간이 짧아 선제 타격에 취약도가 낮다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/세질_(미사일)",
        "wiki_en": "https://en.wikipedia.org/wiki/Sejjil",
    },
    "kheibar": {
        "category": "weapon",
        "name_ko": "카이바르 탄도미사일",
        "name_en": "Kheibar",
        "desc_ko": "호람샤흐르-4로도 불리는 이란의 액체연료 중거리 탄도미사일 개량형. 사거리 2,000km, 탄두중량 약 1,500kg을 주장한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/호람샤흐르_(미사일)",
        "wiki_en": "https://en.wikipedia.org/wiki/Khorramshahr_(missile)",
    },
    "qassem": {
        "category": "weapon",
        "name_ko": "카셈 솔레이마니 미사일",
        "name_en": "Qassem Soleimani missile",
        "desc_ko": "이란이 2023년 공개한 중거리 순항미사일 또는 탄도미사일로, 명명은 2020년 피살된 혁명수비대 쿠드스군 사령관을 기린 것이다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/카셈_솔레이마니",
        "wiki_en": "https://en.wikipedia.org/wiki/Qassem_Soleimani",
    },
    # ──────────── 미국/이스라엘측 공격 수단 ────────────
    "tomahawk": {
        "category": "weapon",
        "name_ko": "토마호크 순항미사일",
        "name_en": "Tomahawk cruise missile",
        "desc_ko": "미 해군의 장거리 지상공격 순항미사일(BGM-109)로 사거리 약 1,600km. 이지스함·잠수함에서 발사되며 정밀 지상공격에 사용된다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/BGM-109_토마호크",
        "wiki_en": "https://en.wikipedia.org/wiki/Tomahawk_(missile_family)",
    },
    "jdam": {
        "category": "weapon",
        "name_ko": "JDAM 정밀유도폭탄",
        "name_en": "Joint Direct Attack Munition",
        "desc_ko": "재래식 무유도 폭탄에 GPS/INS 유도키트를 장착한 정밀유도탄. 주로 미 공군의 F-15/16, B-2, F-35 등에서 투하된다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/JDAM",
        "wiki_en": "https://en.wikipedia.org/wiki/Joint_Direct_Attack_Munition",
    },
    "gbu-57": {
        "category": "weapon",
        "name_ko": "GBU-57 벙커버스터(MOP)",
        "name_en": "GBU-57 Massive Ordnance Penetrator",
        "desc_ko": "미국의 14톤급 관통폭탄으로 지하 60m 강화 벙커 파괴를 목표로 설계. B-2 스텔스 폭격기에서만 운용 가능하며 이란 지하 핵시설 타격 시나리오에서 자주 거론된다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/GBU-57",
        "wiki_en": "https://en.wikipedia.org/wiki/GBU-57A/B_MOP",
    },
    "f-35": {
        "category": "weapon",
        "name_ko": "F-35 라이트닝 II 스텔스 전투기",
        "name_en": "F-35 Lightning II",
        "desc_ko": "록히드마틴의 5세대 스텔스 다목적 전투기. 이스라엘은 F-35I '아디르' 버전을 운용한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/F-35_라이트닝_II",
        "wiki_en": "https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II",
    },
    "f-15": {
        "category": "weapon",
        "name_ko": "F-15 이글 전투기",
        "name_en": "F-15 Eagle",
        "desc_ko": "맥도넬더글러스(현 보잉)의 제공권 장악용 4세대 전투기. 이스라엘 공군은 F-15I '라암' 공격형을 이란 본토 타격 옵션으로 운용한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/F-15_이글",
        "wiki_en": "https://en.wikipedia.org/wiki/McDonnell_Douglas_F-15_Eagle",
    },
    "patriot": {
        "category": "weapon",
        "name_ko": "패트리어트 방공미사일",
        "name_en": "MIM-104 Patriot",
        "desc_ko": "레이시온의 지대공 미사일 시스템(PAC-2/PAC-3). 중고도 항공기, 순항·탄도미사일 요격이 가능하며 미 및 걸프 동맹국이 주력으로 운용한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/MIM-104_패트리어트",
        "wiki_en": "https://en.wikipedia.org/wiki/MIM-104_Patriot",
    },
    "thaad": {
        "category": "weapon",
        "name_ko": "사드 고고도 미사일 방어체계",
        "name_en": "THAAD",
        "desc_ko": "미 육군의 종말단계 고고도 요격체계로 중·단거리 탄도미사일 방어용. UAE·사우디 배치가 알려져 있다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/사드_(미사일)",
        "wiki_en": "https://en.wikipedia.org/wiki/Terminal_High_Altitude_Area_Defense",
    },
    "iron dome": {
        "category": "weapon",
        "name_ko": "아이언돔 요격체계",
        "name_en": "Iron Dome",
        "desc_ko": "이스라엘 라파엘의 단거리 로켓·박격포·무인기 방어 체계. 4~70km 사거리 위협을 타미르 요격탄으로 무력화한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/아이언_돔",
        "wiki_en": "https://en.wikipedia.org/wiki/Iron_Dome",
    },
    "harop": {
        "category": "weapon",
        "name_ko": "하롭 자폭드론",
        "name_en": "IAI Harop",
        "desc_ko": "이스라엘 IAI의 배회탄약(Loitering munition)으로 방공 레이더를 표적으로 한다. 9시간 체공·1,000km 작전반경을 표방한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/IAI_하롭",
        "wiki_en": "https://en.wikipedia.org/wiki/IAI_Harop",
    },
    "delilah": {
        "category": "weapon",
        "name_ko": "델라일라 순항미사일",
        "name_en": "Delilah missile",
        "desc_ko": "이스라엘 IMI의 공중발사 순항미사일로 사거리 약 250km. 재사용 가능한 정찰/공격 임무도 수행.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/델라일라_(미사일)",
        "wiki_en": "https://en.wikipedia.org/wiki/Delilah_(missile)",
    },
    # ──────────── 일반 공격수단 (범주 설명) ────────────
    "missile": {
        "category": "weapon",
        "name_ko": "미사일 (일반)",
        "name_en": "Missile (general)",
        "desc_ko": "자체 추진으로 목표를 공격하는 유도무기의 총칭. 궤도 및 용도에 따라 탄도미사일, 순항미사일, 대공미사일 등으로 구분된다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/미사일",
        "wiki_en": "https://en.wikipedia.org/wiki/Missile",
    },
    "drone": {
        "category": "weapon",
        "name_ko": "무인기 / 드론",
        "name_en": "Drone / UAV",
        "desc_ko": "조종사가 탑승하지 않는 항공기로, 정찰·공격·자폭 등 다양한 임무에 사용된다. 이란-미 분쟁에서는 샤헤드 계열 자폭드론이 대표적으로 등장한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/무인_항공기",
        "wiki_en": "https://en.wikipedia.org/wiki/Unmanned_aerial_vehicle",
    },
    "airstrike": {
        "category": "weapon",
        "name_ko": "공습",
        "name_en": "Airstrike",
        "desc_ko": "유인/무인 항공기로부터 투하된 폭탄 또는 발사된 미사일에 의한 지상 목표 타격. 현대전에서는 정밀유도탄을 활용한 표적 타격을 뜻하는 경우가 많다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/공습",
        "wiki_en": "https://en.wikipedia.org/wiki/Airstrike",
    },
    "cyberattack": {
        "category": "weapon",
        "name_ko": "사이버 공격",
        "name_en": "Cyberattack",
        "desc_ko": "산업제어시스템, 정부·군 네트워크, 통신 인프라를 대상으로 한 디지털 공격. 이란-미/이스라엘 분쟁에서 Stuxnet 등 핵시설·에너지 인프라 대상 공격 사례가 있다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/사이버_공격",
        "wiki_en": "https://en.wikipedia.org/wiki/Cyberattack",
    },
    # ──────────── 표적 (인프라/기지) ────────────
    "natanz": {
        "category": "target",
        "name_ko": "나탄즈 핵시설",
        "name_en": "Natanz nuclear facility",
        "desc_ko": "이란 중부 이스파한주에 위치한 우라늄 농축 시설. 지하 수십 미터에 위치하며 2010년 Stuxnet 사이버공격, 2021년 전력계통 사보타주 등 반복적인 타격 대상이다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/나탄즈",
        "wiki_en": "https://en.wikipedia.org/wiki/Natanz",
    },
    "fordow": {
        "category": "target",
        "name_ko": "포르도 핵시설",
        "name_en": "Fordow Fuel Enrichment Plant",
        "desc_ko": "이란 콤 인근 산악 지하에 위치한 우라늄 농축시설. 지하 약 80~90m에 위치해 재래식 공격으로는 파괴가 어려워 GBU-57 같은 벙커버스터가 논의된다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/포르도_농축시설",
        "wiki_en": "https://en.wikipedia.org/wiki/Fordow_Fuel_Enrichment_Plant",
    },
    "bushehr": {
        "category": "target",
        "name_ko": "부셰르 원자력발전소",
        "name_en": "Bushehr Nuclear Power Plant",
        "desc_ko": "이란 남부 페르시아만 연안의 러시아 기술 기반 원전. VVER-1000 방식 1호기가 가동 중이며, 상업 발전용으로 민감 시설로 분류된다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/부셰르_원자력_발전소",
        "wiki_en": "https://en.wikipedia.org/wiki/Bushehr_Nuclear_Power_Plant",
    },
    "al-udeid": {
        "category": "target",
        "name_ko": "알우데이드 공군기지",
        "name_en": "Al Udeid Air Base",
        "desc_ko": "카타르 도하 인근의 미 중부사령부(CENTCOM) 전방 본부. 이란 미사일 사거리 내에 있으며, 2020년 솔레이마니 피살 보복으로 인접 이라크 아인 알아사드가 타격된 바 있다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/알우데이드_공군기지",
        "wiki_en": "https://en.wikipedia.org/wiki/Al_Udeid_Air_Base",
    },
    "ain al-asad": {
        "category": "target",
        "name_ko": "아인 알아사드 공군기지",
        "name_en": "Al Asad Airbase",
        "desc_ko": "이라크 안바르주에 위치한 미군 주요 거점. 2020년 이란이 솔레이마니 피살 보복으로 탄도미사일 16발을 발사한 표적이다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/알_아사드_공군기지",
        "wiki_en": "https://en.wikipedia.org/wiki/Al_Asad_Airbase",
    },
    "kharg": {
        "category": "target",
        "name_ko": "하르그 섬 석유 수출터미널",
        "name_en": "Kharg Island oil terminal",
        "desc_ko": "이란 석유 수출의 약 90%가 처리되는 페르시아만 하르그 섬의 주요 터미널. 수출 차단 시 이란 경제에 직접적 타격.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/하르그섬",
        "wiki_en": "https://en.wikipedia.org/wiki/Kharg_Island",
    },
    "hormuz": {
        "category": "target",
        "name_ko": "호르무즈 해협",
        "name_en": "Strait of Hormuz",
        "desc_ko": "페르시아만과 오만만을 잇는 폭 33km의 전략 해협. 전세계 해상 원유 수송의 약 20%가 통과해 봉쇄 위협은 즉시 유가 급등을 유발한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/호르무즈_해협",
        "wiki_en": "https://en.wikipedia.org/wiki/Strait_of_Hormuz",
    },
    "bandar abbas": {
        "category": "target",
        "name_ko": "반다르아바스 해군기지",
        "name_en": "Bandar Abbas naval base",
        "desc_ko": "이란 남부 호르무즈간주의 최대 항만이자 이란 해군 주요 기지. 호르무즈 해협 인접으로 해상 봉쇄 작전 중심지다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/반다르아바스",
        "wiki_en": "https://en.wikipedia.org/wiki/Bandar_Abbas",
    },
    "parchin": {
        "category": "target",
        "name_ko": "파르친 군사 시설",
        "name_en": "Parchin military complex",
        "desc_ko": "테헤란 남동쪽의 방대한 탄약·로켓 연구단지. 과거 핵무기 관련 고폭 실험 의혹이 IAEA로부터 제기된 바 있다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/파르친_군사단지",
        "wiki_en": "https://en.wikipedia.org/wiki/Parchin",
    },
    "isfahan": {
        "category": "target",
        "name_ko": "이스파한 핵단지",
        "name_en": "Isfahan nuclear technology center",
        "desc_ko": "이란 중부 이스파한주의 핵연료 변환(UF6) 시설. 나탄즈로 공급되는 가스상 우라늄이 가공되는 핵심 거점이다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/이스파한",
        "wiki_en": "https://en.wikipedia.org/wiki/Isfahan",
    },
    # ──────────── 행위자 (조직/국가) ────────────
    "irgc": {
        "category": "actor",
        "name_ko": "이란 혁명수비대(IRGC)",
        "name_en": "Islamic Revolutionary Guard Corps",
        "desc_ko": "이란 정규군과 별개로 최고지도자에 직접 보고하는 엘리트 군사·정보 조직. 쿠드스군(해외작전), 항공우주군(미사일·드론 운용) 등 분과를 보유한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/이슬람_혁명_수비대",
        "wiki_en": "https://en.wikipedia.org/wiki/Islamic_Revolutionary_Guard_Corps",
    },
    "houthis": {
        "category": "actor",
        "name_ko": "후티 반군 (안사르 알라)",
        "name_en": "Houthis / Ansar Allah",
        "desc_ko": "예멘 북부의 자이드파 시아 정치·무장 조직. 이란의 지원을 받는다고 평가되며 홍해에서 상선 공격을 수행한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/후티",
        "wiki_en": "https://en.wikipedia.org/wiki/Houthi_movement",
    },
    "hezbollah": {
        "category": "actor",
        "name_ko": "헤즈볼라",
        "name_en": "Hezbollah",
        "desc_ko": "레바논 시아파 정치·무장 조직으로 이란의 대리세력 네트워크(Axis of Resistance)의 핵심. 미국/EU는 테러단체로 지정.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/헤즈볼라",
        "wiki_en": "https://en.wikipedia.org/wiki/Hezbollah",
    },
    "iran": {
        "category": "actor",
        "name_ko": "이란 이슬람 공화국",
        "name_en": "Iran",
        "desc_ko": "1979년 이슬람 혁명 이후 신정공화국 체제. 최고지도자(현 하메네이)·대통령·혁명수비대의 삼각 권력 구조를 가진다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/이란",
        "wiki_en": "https://en.wikipedia.org/wiki/Iran",
    },
    "united states": {
        "category": "actor",
        "name_ko": "미국",
        "name_en": "United States",
        "desc_ko": "중동에서는 제5함대(바레인)·CENTCOM(플로리다 본부·카타르 전방)을 통해 군사력을 투사한다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/미국",
        "wiki_en": "https://en.wikipedia.org/wiki/United_States",
    },
    "israel": {
        "category": "actor",
        "name_ko": "이스라엘",
        "name_en": "Israel",
        "desc_ko": "지중해 동부의 유대 국가. 이란 핵·미사일 프로그램에 대한 '그림자 전쟁(shadow war)'을 수십 년간 수행해왔다.",
        "wiki_ko": "https://ko.wikipedia.org/wiki/이스라엘",
        "wiki_en": "https://en.wikipedia.org/wiki/Israel",
    },
}


def _normalize(term: str) -> str:
    return (term or "").strip().lower()


def lookup(term: str) -> dict[str, Any]:
    """용어를 검색한다. 부분일치로 매칭하고, 실패 시 위키 검색 URL 폴백."""
    if not term:
        return _not_found("")
    key = _normalize(term)

    # 1) 정확 매치
    if key in _GLOSSARY:
        entry = _GLOSSARY[key]
        return {"found": True, "query": term, **entry}

    # 2) 포함 매치 (긴 키가 우선하도록 길이순)
    for k in sorted(_GLOSSARY.keys(), key=lambda s: -len(s)):
        if k in key or key in k:
            return {"found": True, "query": term, "matched_key": k, **_GLOSSARY[k]}

    # 3) 한글 이름 부분 매치
    for k, v in _GLOSSARY.items():
        nko = _normalize(v.get("name_ko", ""))
        nen = _normalize(v.get("name_en", ""))
        if nko and (nko in key or key in nko):
            return {"found": True, "query": term, "matched_key": k, **v}
        if nen and (nen in key or key in nen):
            return {"found": True, "query": term, "matched_key": k, **v}

    return _not_found(term)


def _not_found(term: str) -> dict[str, Any]:
    q = quote_plus(term) if term else ""
    return {
        "found": False,
        "query": term,
        "category": "unknown",
        "name_ko": term or "-",
        "name_en": term or "-",
        "desc_ko": "내장 사전에 등록된 정보가 없어 위키피디아 검색 결과로 연결합니다.",
        "wiki_ko": f"https://ko.wikipedia.org/wiki/Special:Search?search={q}" if q else "https://ko.wikipedia.org",
        "wiki_en": f"https://en.wikipedia.org/wiki/Special:Search?search={q}" if q else "https://en.wikipedia.org",
    }
