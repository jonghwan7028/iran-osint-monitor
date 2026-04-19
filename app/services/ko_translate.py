"""
English → Korean translation helpers for OSINT incidents.
Used by the mapper and dashboard to render Korean by default,
while keeping the original English available via a click-toggle.
"""
from __future__ import annotations

import re
from typing import Any


# ---------- 기본 용어 사전 ----------

ACTOR_KO: dict[str, str] = {
    "united states": "미국",
    "united states / israel": "미국/이스라엘",
    "united states/israel": "미국/이스라엘",
    "us": "미국",
    "us / israel": "미국/이스라엘",
    "israel": "이스라엘",
    "idf": "이스라엘방위군(IDF)",
    "centcom": "미 중부사령부(CENTCOM)",
    "iran": "이란",
    "irgc": "이란 혁명수비대(IRGC)",
    "iran revolutionary guard corps": "이란 혁명수비대(IRGC)",
    "hezbollah": "헤즈볼라",
    "hezbollah (iran proxy)": "헤즈볼라(이란 대리세력)",
    "houthis": "후티 반군",
    "houthi": "후티 반군",
    "houthi (iran proxy)": "후티 반군(이란 대리세력)",
    "saudi arabia": "사우디아라비아",
    "uae": "UAE(아랍에미리트)",
    "united arab emirates": "아랍에미리트(UAE)",
    "turkey (nato)": "튀르키예(NATO 회원국)",
    "turkey": "튀르키예",
    "bahrain": "바레인",
    "bahrain / saudi arabia": "바레인/사우디아라비아",
    "kuwait": "쿠웨이트",
    "iran (threat)": "이란(위협)",
    "unknown (likely iran-linked)": "미상(이란 연계 추정)",
    "unknown": "미상",
    "n/a": "해당 없음",
    "united states / gulf states": "미국/걸프 국가들",
    "united states / iran": "미국/이란",
    "iran / united states": "이란/미국",
    "united states / israel": "미국/이스라엘",
    "iran / united states / gulf states": "이란 → 미국/걸프국가",
    "china": "중국",
    "russia": "러시아",
    "china / russia": "중국/러시아",
    "oman": "오만",
    "oman (mediator)": "오만(중재국)",
    "united states / iran": "미국·이란",
    "iran (irgc navy)": "이란(IRGC 해군)",
    "iran (quds force)": "이란(쿠드스군)",
    "iran (iraqi proxies)": "이란(이라크 대리세력)",
    "iraqi shia militias (iran proxy)": "이라크 시아파 민병대(이란 대리세력)",
    "iraqi shia militias": "이라크 시아파 민병대",
    "houthi (iran proxy)": "후티 반군(이란 대리세력)",
    "yemen": "예멘",
    "commercial shipping": "상선(민간 선박)",
    "greece": "그리스",
    "iraq": "이라크",
    "syria": "시리아",
    "united nations": "국제연합(UN)",
    "nato": "NATO",
}

MEANS_KO: dict[str, str] = {
    "tomahawk missiles": "토마호크 순항미사일",
    "b-2/b-1/b-52 bombers": "B-2·B-1·B-52 전략폭격기",
    "himars": "HIMARS 다연장 로켓",
    "precision airstrike": "정밀 공습",
    "ballistic missiles": "탄도미사일",
    "ballistic missile": "탄도미사일",
    "drones": "무인기(드론)",
    "drone strike": "무인기 공격",
    "drone": "무인기(드론)",
    "missiles": "미사일",
    "missiles, drones": "미사일·무인기",
    "drones, ballistic missiles": "무인기·탄도미사일",
    "submarine torpedo": "잠수함 어뢰",
    "gbu-57 bunker buster bombs": "GBU-57 벙커버스터 폭탄",
    "airstrike": "공습",
    "airstrikes": "공중 공습",
    "cruise missiles": "순항미사일",
    "manpads (shoulder-fired missile)": "휴대용 지대공미사일(MANPADS)",
    "gunfire": "총격",
    "diplomatic ultimatum": "외교적 최후통첩",
    "succession / appointment": "승계·임명",
    "threat of attack": "공격 위협",
    "missile": "미사일",
    "rocket": "로켓",
    "cyberattack": "사이버 공격",
    "bombing": "폭격",
    "fighter jet": "전투기",
    "anti-ship ballistic missiles": "대함 탄도미사일",
    "suicide drones": "자살 무인기",
    "suicide boat swarm": "자살 고속정 군집공격",
    "armed mob assault": "무장 시위대 습격",
    "back-channel diplomacy": "비밀 외교 채널",
    "humanitarian pause (72 hours)": "72시간 인도적 휴전",
    "un security council resolution (vetoed)": "유엔 안보리 결의(거부권 행사)",
    "precision airstrike on convoy": "차량 호위대 정밀 공습",
    "fattah-2 hypersonic glide vehicle": "파타흐-2 극초음속 활공체",
    "gbu-57 mop bunker buster": "GBU-57 MOP 벙커버스터",
    "b-2 bomber strikes": "B-2 폭격기 공습",
    "gbu-31 jdam": "GBU-31 JDAM",
    "rockets": "로켓",
    "450 projectiles": "450발",
    "anti-ship ballistic missiles, suicide drones": "대함 탄도미사일·자살 무인기",
    "ground-to-air missiles": "공대지 미사일",
    "air-to-ground missiles": "지대공 미사일",
}

TARGET_TYPE_KO: dict[str, str] = {
    "military / leadership compound": "군사·지도부 시설",
    "leadership compound": "지도부 시설",
    "us military bases, embassies, oil infrastructure": "미군기지·대사관·석유 인프라",
    "civilian airport": "민간 공항",
    "naval vessel (frigate)": "해군 전투함(프리깃)",
    "israeli territory": "이스라엘 영토",
    "nuclear facility": "핵시설",
    "nuclear facility (heavy water)": "핵시설(중수 생산)",
    "airspace violation / debris impact": "영공 침범·잔해 낙하",
    "political leadership": "정치 지도부",
    "fighter aircraft (f-15e)": "전투기(F-15E)",
    "residential building / oil refinery": "주거 건물·정유시설",
    "university campus / fuel station": "대학 캠퍼스·주유소",
    "energy infrastructure": "에너지 인프라",
    "air base": "공군기지",
    "military base": "군사기지",
    "base": "군사기지",
    "oil facility": "석유 시설",
    "nuclear site": "핵시설",
    "port": "항만",
    "airport": "공항",
    "embassy": "대사관",
    "military targets on oil export island": "석유 수출섬 내 군사 목표",
    "bridges, railway infrastructure": "교량·철도 인프라",
    "diplomatic facility": "외교 시설",
    "civilian infrastructure (power plants, bridges)": "민간 인프라(발전소·교량)",
    "airports, military aircraft": "공항·군용기",
    "telecom infrastructure": "통신 인프라",
    "critical infrastructure (bridge)": "핵심 인프라(교량)",
}

EVENT_TYPE_KO: dict[str, str] = {
    "strike": "공격",
    "naval engagement": "해전",
    "missile intercept": "미사일 요격",
    "political event": "정치 이벤트",
    "shootdown / rescue": "격추·구조 작전",
    "strike / intercept": "공격/요격",
    "attack": "공격",
    "diplomatic / threat": "외교·위협",
    "security measure": "안보 조치",
    "military_event": "군사 이벤트",
    "security_event": "안보 이벤트",
}

VERIFIED_STATUS_KO: dict[str, str] = {
    "confirmed": "확인됨",
    "likely": "유력",
    "claimed": "주장",
    "disputed": "논쟁중",
    "retracted": "철회됨",
    "verified": "확인됨",
    "partially_verified": "부분 확인",
    "unverified": "미확인",
}

SEVERITY_KO: dict[str, str] = {
    "높음": "높음",
    "중간": "중간",
    "낮음": "낮음",
    "미상": "미상",
}

# 위치 이름 번역 (부분 일치) — 길이순 정렬해서 더 구체적 매칭 우선
LOCATION_KO: dict[str, str] = {
    "tehran — khamenei compound": "테헤란 — 하메네이 거주단지",
    "tehran airports, iran": "테헤란 공항들, 이란",
    "sharif university, tehran, iran": "샤리프공과대학교, 테헤란, 이란",
    "zagros mountains, isfahan province, iran": "자그로스 산맥, 이스파한주, 이란",
    "indian ocean, south of galle, sri lanka": "인도양(스리랑카 갈레 이남)",
    "dubai international airport, uae": "두바이 국제공항, UAE",
    "ali al salem air base, kuwait": "알리 알살렘 공군기지, 쿠웨이트",
    "kharg island, iran": "카르그섬, 이란",
    "king fahd causeway, bahrain-saudi arabia": "킹 파흐드 코즈웨이(바레인–사우디)",
    "israeli consulate, istanbul, turkey": "이스라엘 영사관, 이스탄불, 튀르키예",
    "fordow nuclear facility, iran": "포르도 핵시설, 이란",
    "khondab (arak), iran": "콘다브(아라크), 이란",
    "kashan / tabriz / karaj, iran": "카샨/타브리즈/카라지, 이란",
    "haifa, israel": "하이파, 이스라엘",
    "fujairah, uae": "푸자이라, UAE",
    "eastern province, saudi arabia": "동부주(東部州), 사우디아라비아",
    "dortyol, hatay province, turkey": "도르트욜, 하타이주, 튀르키예",
    "northern israel / southern lebanon": "이스라엘 북부·레바논 남부",
    "persian gulf region (multiple countries)": "페르시아만 일대(여러 국가)",
    "washington dc / tehran": "워싱턴 DC / 테헤란",
    "tehran, iran": "테헤란, 이란",
    "tehran": "테헤란",
    "iran": "이란",
    "israel": "이스라엘",
    "saudi arabia": "사우디아라비아",
    "kuwait": "쿠웨이트",
    "turkey": "튀르키예",
    "lebanon": "레바논",
    "uae": "UAE",
    "middle east": "중동 지역",
    "persian gulf": "페르시아만",
    "strait of hormuz": "호르무즈 해협",
    "northern israel (multi-city)": "북부 이스라엘(다중 도시)",
    "northern israel / southern lebanon": "이스라엘 북부·레바논 남부",
    "red sea, south of hodeidah, yemen": "홍해(예멘 호데이다 이남)",
    "mezzeh, damascus, syria": "메제, 다마스쿠스, 시리아",
    "hakirya military complex, tel aviv, israel": "하키르야 군사단지, 텔아비브, 이스라엘",
    "un headquarters, new york": "유엔 본부, 뉴욕",
    "gulf of oman": "오만만",
    "imam reza shrine, mashhad, iran": "이맘 레자 성지, 마슈하드, 이란",
    "us embassy, green zone, baghdad, iraq": "미 대사관, 그린존, 바그다드, 이라크",
    "muscat, oman": "무스카트, 오만",
    "bandar abbas, hormozgan, iran": "반다르아바스, 호르무즈간주, 이란",
    "washington dc / tehran": "워싱턴 DC / 테헤란",
    "mashhad": "마슈하드",
    "damascus": "다마스쿠스",
    "baghdad": "바그다드",
    "new york": "뉴욕",
    "oman": "오만",
}


# ---------- 문장 단위 치환 사전 (damage/tactical/strategic 요약용) ----------

PHRASE_REPLACEMENTS: list[tuple[str, str]] = [
    # 인명/직위
    ("supreme leader khamenei", "최고지도자 하메네이"),
    ("supreme leader ali khamenei", "최고지도자 알리 하메네이"),
    ("ali khamenei", "알리 하메네이"),
    ("mojtaba khamenei", "모즈타바 하메네이"),
    ("defense minister aziz nasirzadeh", "아지즈 나시르자데 국방장관"),
    ("irgc commander mohammad pakpour", "모하마드 파크푸르 IRGC 사령관"),
    ("ali shamkhani", "알리 샴카니"),
    ("defence council secretary", "국방위원회 서기"),
    ("bg masoud zare", "마수드 자레 준장"),
    ("netanyahu", "네타냐후"),
    ("trump", "트럼프"),
    # 장소·시설
    ("strait of hormuz", "호르무즈 해협"),
    ("indian ocean", "인도양"),
    ("dubai international airport", "두바이 국제공항"),
    ("raf akrotiri base in cyprus", "키프로스 RAF 아크로티리 기지"),
    ("raf akrotiri", "RAF 아크로티리"),
    ("iris dena", "IRIS 데나함"),
    ("uss charlotte", "미 해군 샬럿함(SSN)"),
    ("galle", "갈레"),
    ("sri lankan navy", "스리랑카 해군"),
    ("fordow", "포르도"),
    ("natanz", "나탄즈"),
    ("isfahan", "이스파한"),
    ("khondab", "콘다브"),
    ("arak", "아라크"),
    ("kharg island", "카르그섬"),
    ("hatay province", "하타이주"),
    ("kashan", "카샨"),
    ("tabriz", "타브리즈"),
    ("zanjan", "잔잔"),
    ("karaj", "카라지"),
    ("tehran", "테헤란"),
    ("haifa", "하이파"),
    ("tel aviv", "텔아비브"),
    ("baharestan county", "바하레스탄군"),
    ("sharif university of technology", "샤리프공과대학교"),
    ("eastern province", "동부주"),
    ("fujairah", "푸자이라"),
    ("abu dhabi", "아부다비"),
    ("king fahd causeway", "킹 파흐드 코즈웨이"),
    ("ali al salem airbase", "알리 알살렘 공군기지"),
    ("ali al salem air base", "알리 알살렘 공군기지"),
    # 조직·국가
    ("centcom", "미 중부사령부(CENTCOM)"),
    ("nato secretary general mark rutte", "마르크 뤼터 NATO 사무총장"),
    ("nato air defense", "NATO 방공"),
    ("nato", "NATO"),
    ("un ", "UN "),
    ("ghalibaf", "갈리바프"),
    ("larijani", "라리자니"),
    ("pezeshkian", "페제시키안"),
    ("dia", "美 국방정보국(DIA)"),
    ("atomic energy organisation of iran", "이란 원자력청"),
    ("nyt", "뉴욕타임스(NYT)"),
    ("israeli air force", "이스라엘 공군"),
    ("us navy submarine", "미 해군 잠수함"),
    ("us army", "미 육군"),
    ("us warships", "미 해군 함정"),
    ("us military", "미군"),
    ("us official", "미 당국자"),
    ("irgc", "IRGC"),
    # 무기/수단
    ("b-2 stealth bombers", "B-2 스텔스 폭격기"),
    ("b-1 lancers", "B-1 랜서"),
    ("b-52 stratofortresses", "B-52 전략폭격기"),
    ("tomahawk missiles", "토마호크 순항미사일"),
    ("himars launchers", "HIMARS 다연장 로켓"),
    ("gbu-57 bunker buster bombs", "GBU-57 벙커버스터 폭탄"),
    ("manpads", "휴대용 지대공미사일(MANPADS)"),
    ("shoulder-fired missile", "휴대용 지대공미사일"),
    ("f-15e strike eagle", "F-15E 스트라이크 이글"),
    ("a-10", "A-10"),
    ("drones", "드론"),
    ("drone", "드론"),
    ("ballistic missiles", "탄도미사일"),
    ("ballistic missile", "탄도미사일"),
    # 동사·표현
    ("were killed", "사망"),
    ("was killed", "사망"),
    ("were wounded", "부상"),
    ("was wounded", "부상"),
    ("wounded", "부상"),
    ("injured", "부상"),
    ("killed", "사망"),
    ("destroyed", "파괴"),
    ("damaged", "피해"),
    ("intercepted", "요격됨"),
    ("shot down", "격추"),
    ("sunk", "침몰"),
    ("eliminated", "제거"),
    ("inoperable", "가동 불능"),
    ("no casualties", "인명 피해 없음"),
    ("minor damage", "경미한 피해"),
    ("major damage", "주요 피해"),
    ("severe damage", "심각한 피해"),
    ("closed indefinitely", "무기한 폐쇄"),
    ("closed to shipping", "선박 통항 금지"),
    # 기타 명사
    ("residential building", "주거 건물"),
    ("residential area", "주거 지역"),
    ("oil refinery", "정유시설"),
    ("oil facilities", "석유 시설"),
    ("oil export hub", "석유 수출 거점"),
    ("nuclear weapons capability", "핵무기 역량"),
    ("command structure", "지휘 구조"),
    ("leadership", "지도부"),
    ("regime change", "정권 교체"),
    ("ceasefire", "휴전"),
    ("civilian infrastructure", "민간 인프라"),
    ("power plants", "발전소"),
    ("synagogue", "유대교 회당"),
    ("consulate", "영사관"),
    ("embassy", "대사관"),
    ("fighter aircraft", "전투기"),
    ("transport aircraft", "수송기"),
    ("helicopters", "헬기"),
    ("air defenses", "방공망"),
    ("air defense", "방공망"),
    ("deterrence", "억제"),
    ("escalation", "확전"),
    ("negotiation", "협상"),
    ("proxy", "대리세력"),
    # 관용구
    ("we got him", "'우리가 잡았다(WE GOT HIM)'"),
    # 자주 남는 잔존 영어
    ("attackers", "공격자"),
    ("attacker", "공격자"),
    ("police officers", "경찰관"),
    ("was unstaffed", "인원이 없던 상태"),
    ("railway segments", "철도 구간"),
    ("railway bridges", "철도 교량"),
    ("railway tracks", "철도 선로"),
    ("bridges", "교량"),
    ("bridge strike", "교량 타격"),
    ("bridge", "교량"),
    ("air defense systems", "방공 시스템"),
    ("crew members", "승무원"),
    ("crewmen", "승조원"),
    ("service members", "장병"),
    ("both us crew", "미군 승무원 2명"),
    ("ministry of defence", "국방부"),
    ("interior ministry", "내무부"),
    ("fire in", "화재 발생, "),
    ("fires in", "화재 발생, "),
    ("hits on", "타격"),
    ("struck", "타격됨"),
    ("hit ", "타격 "),
    ("hit by", "피격"),
    ("hit", "타격"),
    ("impacts", "피격"),
    ("facility", "시설"),
    ("facilities", "시설"),
    ("airport", "공항"),
    ("airports", "공항"),
    ("aircraft", "항공기"),
    ("planes", "항공기"),
    ("military targets", "군사 목표"),
    ("targets", "목표물"),
    ("vehicles", "차량"),
    ("no immediate damage", "즉각적 피해 없음"),
    ("no physical damage", "물리적 피해 없음"),
    ("reopened in limited capacity", "제한적 재개"),
    ("temporarily halted", "일시 중단"),
    ("indefinitely", "무기한"),
    ("precautionary measure", "예방 조치"),
    ("debris fell", "잔해 낙하"),
    ("debris landed", "잔해 낙하"),
    ("dozens of", "수십 대의 "),
    ("multiple", "다수의 "),
    ("several", "여러 "),
    ("killed along with", "함께 사망,"),
    ("targeting", "타격 목표 ")
    ,
    # 숫자+단위 부사
    (" during the rescue", " 구조 작전 중"),
    (" overnight", " 야간에"),
    (" reportedly", " 보도됨"),
    (" as a precaution", " 예방 차원"),
    (" as a precautionary measure", " 예방 조치"),
    # 전술/전략 평가에 자주 쓰이는 표현
    ("broad retaliatory strikes", "광범위한 보복 공격"),
    ("retaliatory strikes", "보복 공격"),
    ("coordinated surprise airstrikes", "조율된 기습 공습"),
    ("opening salvo", "개전 초기 일제 공격"),
    ("massive opening salvo", "대규모 개전 초기 공격"),
    ("decapitation strike", "참수 작전"),
    ("decapitation of senior leadership", "최고 지도부 제거"),
    ("to exact costs on", "에 대한 응징 비용 부과"),
    ("to disrupt", "을 교란하기 위함"),
    ("to paralyze", "마비시키기 위함"),
    ("to eliminate", "제거하기 위함"),
    ("to pressure", "에 압박을 가하기 위함"),
    ("to degrade", "약화시키기 위함"),
    ("to destroy", "파괴하기 위함"),
    ("to demonstrate", "과시하기 위함"),
    ("to deny", "저지하기 위함"),
    ("to target", "목표로 삼기 위함"),
    ("designed to", "하기 위해 설계됨,"),
    ("aimed at", "을 목적으로 함,"),
    ("intended to", "의도됨,"),
    ("part of", "~의 일환"),
    ("core us war objective", "미국의 핵심 전쟁 목표"),
    ("core war objective", "핵심 전쟁 목표"),
    ("c2 infrastructure", "지휘통제(C2) 인프라"),
    ("command structure", "지휘 구조"),
    ("regime collapse", "정권 붕괴"),
    ("regime change", "정권 교체"),
    ("nuclear breakout capability", "핵 돌파 역량"),
    ("nuclear fuel cycle infrastructure", "핵연료 주기 인프라"),
    ("nuclear program", "핵 프로그램"),
    ("systematic campaign", "체계적 작전"),
    ("systematic degradation", "체계적 약화"),
    ("economic warfare", "경제 전쟁"),
    ("global oil supply chain", "세계 석유 공급망"),
    ("air superiority", "제공권"),
    ("air dominance", "제공권"),
    ("air mobility", "항공 기동"),
    ("transport capability", "수송 역량"),
    ("military logistics", "군수/로지스틱스"),
    ("weapons transport", "무기 수송"),
    ("rail network", "철도망"),
    ("civilian toll", "민간인 피해"),
    ("war crimes concerns", "전쟁범죄 우려"),
    ("international pressure", "국제적 압박"),
    ("force projection capability", "전력 투사 역량"),
    ("proxy escalation", "대리세력 에스컬레이션"),
    ("second front", "제2전선"),
    ("second front against", "에 대한 제2전선"),
    ("axis of resistance", "저항의 축"),
    ("multi-front pressure", "다전선 압박"),
    ("maximum pressure tactic", "최대 압박 전술"),
    ("infrastructure destruction threats", "인프라 파괴 위협"),
    ("critical inflection point", "핵심 변곡점"),
    ("potential escalation", "잠재적 확전"),
    ("civilian power grid", "민간 전력망"),
    ("coercive diplomacy", "강압 외교"),
    ("deterrence signaling", "억제 신호"),
    ("escalation management", "확전 관리"),
    ("asymmetric attack", "비대칭 공격"),
    ("asymmetric threat", "비대칭 위협"),
    ("diplomatic target", "외교 표적"),
    ("neutral nato country", "중립 NATO 국가"),
    ("widening of conflict", "분쟁 확대"),
    ("terrorism nexus", "테러리즘 연계"),
    ("dynastic succession", "세습 승계"),
    ("hardliner control", "강경파 지배"),
    ("partial success only", "부분적 성공에 그침"),
    ("persistent strikes", "지속적 공격"),
    ("persistent attacks", "지속적 공격"),
    ("sustained retaliatory capability", "지속적 보복 역량"),
    ("economic lifeline", "경제적 생명선"),
    ("direct iran-israel kinetic exchange", "이란·이스라엘 직접 무력충돌"),
    ("escalation costs", "확전 비용"),
    ("propaganda event", "선전 이벤트"),
    ("high-profile shootdown", "고강도 격추 사건"),
    ("political succession event", "정치 승계 이벤트"),
    ("amid ongoing war", "전쟁 진행 중"),
    ("leadership remains fragmented", "지도부 분열 지속"),
    # 접속사·전치사 — 기계적 치환 비활성화 (translate_sentence에서 skip됨)
    # (" and ", " 및 "),
    # (" or ", " 또는 "),
    # (" near ", " 인근 "),
    # (" in ", " — "),
    # (" at ", " — "),
    # (" on ", " — "),
    # (" to ", " → "),
    # (" of ", " / "),
    # 자주 쓰이는 동사·표현
    ("iran rejects", "이란 거부"),
    ("iran said", "이란 측 발표"),
    ("iran says", "이란 측 발표"),
    ("iran has", "이란은"),
    ("israel said", "이스라엘 측 발표"),
    ("us said", "미국 측 발표"),
    ("us official", "미 당국자"),
    ("causeway", "코즈웨이"),
    ("energy", "에너지"),
    ("proposals", "제안"),
    ("proposal", "제안"),
    ("deadline", "최후통첩"),
    ("ultimatum", "최후통첩"),
    ("ceasefire", "휴전"),
    ("officials", "당국자"),
    ("official", "당국자"),
    ("children", "어린이"),
    ("women", "여성"),
    ("men", "남성"),
    ("civilians", "민간인"),
    ("civilian", "민간인"),
    # be동사/관사 — 기계적 치환 비활성화 (부자연스러운 번역 방지)
    # (" was ", " "),
    # (" were ", " "),
    # (" the ", " "),
    # 숫자 뒤 단위 보조 (최소)
    ("day 38 of us-israeli attacks", "美·이스라엘 공격 개시 38일차"),
    ("day 39 of us-israeli attacks", "美·이스라엘 공격 개시 39일차"),
]


def _dict_translate(value: str | None, table: dict[str, str]) -> str:
    """대소문자 무시 전체 일치 → 단어 경계 부분 치환(짧거나 약어 키) → 긴 키 부분 치환.
    원본 대소문자는 보존하고, 매치되지 않는 부분은 그대로 둔다.
    """
    if not value:
        return value or ""
    lower = value.strip().lower()
    # 1) 정확 일치
    if lower in table:
        return table[lower]
    # 2) 길이 순으로 부분 치환. 짧거나 순수 알파벳(약어) 키는 단어 경계를 강제해
    #    "Russia" 안의 "us" 같은 부분 매칭을 방지한다.
    result = value
    for k, v in sorted(table.items(), key=lambda kv: -len(kv[0])):
        if not k:
            continue
        use_boundary = len(k) <= 4 or re.fullmatch(r"[A-Za-z\-]+", k) is not None
        if use_boundary:
            pattern = re.compile(r"(?<!\w)" + re.escape(k) + r"(?!\w)", flags=re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(k), flags=re.IGNORECASE)
        if pattern.search(result):
            result = pattern.sub(v, result)
    return result


def translate_actor(actor: str | None) -> str:
    return _dict_translate(actor, ACTOR_KO) or "미상"


def translate_means(means: str | None) -> str:
    if not means:
        return "미상"
    # 복합 수단(쉼표 구분) 처리
    parts = [p.strip() for p in re.split(r"[,/]", means) if p.strip()]
    translated = [_dict_translate(p, MEANS_KO) for p in parts]
    return " · ".join(translated) if translated else (means or "미상")


def translate_target_type(target_type: str | None) -> str:
    return _dict_translate(target_type, TARGET_TYPE_KO) or "미상"


def translate_event_type(event_type: str | None) -> str:
    return _dict_translate(event_type, EVENT_TYPE_KO) or "이벤트"


def translate_verified_status(status: str | None) -> str:
    return VERIFIED_STATUS_KO.get((status or "").lower(), status or "미상")


def translate_location(location_name: str | None) -> str:
    if not location_name:
        return "미상"
    key = location_name.strip().lower()
    if key in LOCATION_KO:
        return LOCATION_KO[key]
    # 길이 긴 키 우선 매칭
    result = location_name
    for k, v in sorted(LOCATION_KO.items(), key=lambda kv: -len(kv[0])):
        if k in result.lower():
            # 대소문자 무시 치환
            result = re.sub(re.escape(k), v, result, flags=re.IGNORECASE)
    return result


def translate_sentence(text: str | None) -> str:
    """긴 영어 문장을 한국어로 번역. 사전에 완전 일치가 있으면 바로 반환하고,
    없으면 주요 고유명사·용어를 한국어로 바꿉니다."""
    if not text:
        return "-"

    # 1) 완전 일치 사전 — 시드 데이터의 모든 문장이 자연스러운 한국어로 등록됨
    from app.services.ko_sentences import SENTENCE_KO
    if text in SENTENCE_KO:
        return SENTENCE_KO[text]
    # 앞뒤 공백/마침표 제거 후 재시도
    stripped = text.strip().rstrip(".")
    if stripped in SENTENCE_KO:
        return SENTENCE_KO[stripped]

    # 2) 미등록 문장: 고유명사/군사용어만 치환 (전치사·관사는 치환하지 않음)
    result = text
    for en, ko in sorted(PHRASE_REPLACEMENTS, key=lambda kv: -len(kv[0])):
        if not en:
            continue
        # 전치사·관사·be동사 등 일반 단어는 건너뜀 — 부자연스러운 번역 방지
        if en.strip() in (" and ", " or ", " near ", " in ", " at ", " on ", " to ", " of ",
                          " was ", " were ", " the ", " a ", " an "):
            continue
        use_boundary = len(en) <= 4 or re.fullmatch(r"[A-Za-z\-]+", en) is not None
        if use_boundary:
            pattern = re.compile(r"(?<!\w)" + re.escape(en) + r"(?!\w)", flags=re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(en), flags=re.IGNORECASE)
        result = pattern.sub(ko, result)
    # 기본 어미/공백 정리
    result = result.replace(";", "; ").replace("  ", " ").strip()
    result = re.sub(r"\s+([,.;])", r"\1", result)
    return result


def translate_title(title: str | None) -> str:
    return translate_sentence(title)


def build_bilingual_incident(inc: Any, doc: Any, actor_side: str) -> dict[str, Any]:
    """지도 팝업·대시보드에서 바로 쓸 수 있는 KO/EN 이중 dict 반환."""
    pub_date = ""
    if doc and getattr(doc, "published_at", None):
        pub_date = doc.published_at.strftime("%Y-%m-%d %H:%M UTC")
    elif getattr(inc, "created_at", None):
        pub_date = inc.created_at.strftime("%Y-%m-%d %H:%M UTC")

    side_label_ko = {
        "iran": "🔴 이란측 공격",
        "us_israel": "🔵 미국/이스라엘 공격",
        "other": "🟡 기타 이벤트",
    }.get(actor_side, "🟡 기타 이벤트")
    side_label_en = {
        "iran": "🔴 Iran-side attack",
        "us_israel": "🔵 US/Israel strike",
        "other": "🟡 Other event",
    }.get(actor_side, "🟡 Other event")

    return {
        "id": inc.id,
        "actor_side": actor_side,
        "pub_date": pub_date,
        "side_label_ko": side_label_ko,
        "side_label_en": side_label_en,
        # 영문 원본
        "en": {
            "title": doc.title if doc else "",
            "publisher": doc.publisher if doc else "",
            "url": doc.url if doc else "#",
            "actor": inc.actor or "Unknown",
            "target_actor": inc.target_actor or "-",
            "location_name": inc.location_name or "-",
            "event_type": inc.event_type or "-",
            "means": inc.means or "-",
            "target_type": inc.target_type or "-",
            "damage_summary": inc.damage_summary or "-",
            "tactical_assessment": inc.tactical_assessment or "-",
            "strategic_assessment": inc.strategic_assessment or "-",
            "verified_status": inc.verified_status or "-",
        },
        # 한국어 번역
        "ko": {
            "title": translate_title(doc.title) if doc else "",
            "publisher": doc.publisher if doc else "",
            "url": doc.url if doc else "#",
            "actor": translate_actor(inc.actor),
            "target_actor": translate_actor(inc.target_actor),
            "location_name": translate_location(inc.location_name),
            "event_type": translate_event_type(inc.event_type),
            "means": translate_means(inc.means),
            "target_type": translate_target_type(inc.target_type),
            "damage_summary": translate_sentence(inc.damage_summary),
            "tactical_assessment": translate_sentence(inc.tactical_assessment),
            "strategic_assessment": translate_sentence(inc.strategic_assessment),
            "verified_status": translate_verified_status(inc.verified_status),
        },
        "latitude": inc.latitude,
        "longitude": inc.longitude,
        "confidence": float(inc.confidence or 0.0),
    }
