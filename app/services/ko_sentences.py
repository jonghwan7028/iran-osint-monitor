"""
Korean translations of military/OSINT incident descriptions from 2026 US-Iran war dashboard.
Maps English sentences to natural, fluent Korean translations.

Guidelines applied:
- Natural Korean sentence structure (SOV word order)
- Proper military/defense terminology
- Correct transliteration of proper nouns
- Accurate numbers and statistics
- Appropriate Korean sentence endings for brief assessments
"""

SENTENCE_KO: dict[str, str] = {
    # Event 1: US and Israel launch Operation Epic Fury
    "Supreme Leader Khamenei killed; defense minister, IRGC commander, and multiple senior officials eliminated; ~2,000 targets struck in first days": "최고지도자 하메네이 사망; 국방장관, IRGC 사령관 및 다수 고위 관리 제거; 개전 초기 약 2,000개 표적 타격",
    "Massive opening salvo targeting C2 infrastructure and leadership to paralyze Iranian command structure.": "지휘통제(C2) 인프라와 지도부를 마비시키기 위한 대규모 개전 일제타격.",
    "US-Israel aim to induce regime change and permanently destroy Iran nuclear and ballistic missile programs.": "미국-이스라엘의 목표: 정권 교체 유도 및 이란 핵·탄도미사일 프로그램의 영구적 파괴.",

    # Event 2: Israel assassinates Supreme Leader Khamenei
    "Supreme Leader Khamenei killed along with family members and 7+ senior military/intelligence officials": "최고지도자 하메네이 가족들과 함께 피살; 7명 이상의 고위 군부·정보기관 관리 제거",
    "Decapitation strike designed to eliminate top-tier leadership and disrupt C2.": "최상위 지도부 제거 및 지휘통제 마비를 의도한 참수 작전.",
    "Aimed at catalyzing regime collapse and preventing coordinated Iranian retaliation.": "정권 붕괴 유도 및 이란의 조직적 보복 방지를 겨냥함.",

    # Event 3: Iran launches retaliatory missile and drone strikes
    "Multiple US bases hit; Dubai International Airport damaged; Strait of Hormuz closed to shipping": "다수 미국 기지 피격; 두바이 국제공항 손상; 호르무즈 해협 해운 폐쇄",
    "Broad retaliatory strikes to exact costs on US and regional allies simultaneously.": "미국 및 지역 동맹국에 동시에 대가를 강요하기 위한 광범위한 보복 공격.",
    "Iran uses Hormuz closure as strategic leverage to pressure ceasefire negotiations.": "호르무즈 폐쇄를 전략적 지렛대로 활용하여 휴전 협상 압박.",

    # Event 4: Iranian drones strike Dubai International Airport
    "Airport damaged, all flights halted temporarily, reopened in limited capacity": "공항 손상, 모든 항공편 일시 중단, 제한된 용량으로 재개항",
    "Targeted critical civilian hub to demonstrate reach and disrupt regional operations.": "민간 핵심 거점을 표적으로 삼아 타격 범위를 시위하고 지역 작전 교란.",
    "Economic warfare disrupting aviation and commerce to pressure Gulf states.": "항공·상업 교란을 통한 경제 전쟁으로 걸프 국가들 압박.",

    # Event 5: US submarine sinks Iranian frigate
    "IRIS Dena sunk; 87 killed, 32 rescued by Sri Lankan navy": "IRIS 데나호 침몰; 87명 사망, 32명 스리랑카 해군에 의해 구조",
    "Eliminated Iranian naval asset far from theater to deny force projection capability.": "작전 지역 원거리에서 이란 해군 자산을 제거하여 전력 투사 능력 차단.",
    "Demonstrates US willingness to strike Iranian assets globally.": "미국의 이란 자산 글로벌 타격 의지 입증.",

    # Event 6: Hezbollah launches missiles and drones into Israel
    "Multiple strikes on northern Israel; Hezbollah drone struck RAF Akrotiri base in Cyprus": "북부 이스라엘에 다중 타격; 헤즈볼라 무인기, 사이프러스 RAF 아크로티리 기지 타격",
    "Proxy escalation opening a second front against Israel from Lebanon.": "레바논에서 이스라엘 대항 제2전선을 여는 대리 전쟁 확대.",
    "Part of Irans Axis of Resistance strategy multi-front pressure on Israel.": "이란의 저항 축 전략의 일부, 이스라엘 대항 다중 전선 압박.",

    # Event 7: US strikes Fordow Natanz and Isfahan underground nuclear facilities
    "Underground nuclear facilities at Fordow Natanz and Isfahan struck; did not fully collapse facilities per DIA assessment": "포르도, 나탄즈, 이스파한의 지하 핵시설 타격; DIA 평가에 따르면 시설 완전 붕괴되지 않음",
    "Attempted to destroy deeply buried nuclear enrichment infrastructure.": "깊이 묻혀있는 핵 농축 인프라 파괴 시도.",
    "Core US war objective eliminating Irans nuclear breakout capability. Partial success only.": "이란의 핵 보유 능력 제거라는 미국의 핵심 전쟁 목표. 부분적 성공만 달성.",

    # Event 8: Iranian missile intercepted over Turkey
    "Missile intercepted by NATO air defense; debris fell in Hatay Province": "NATO 방공 체계에 의해 미사일 요격됨; 잔해는 하타이 주에 추락",
    "Likely not intentionally aimed at Turkey missile overflew en route to other targets.": "터키를 의도적으로 겨냥한 것이 아니라 다른 표적으로 향하는 도중 통과한 것으로 보임.",
    "Significant escalation NATO territory affected alliance invoked Article 5 language.": "NATO 영토 피해를 포함한 심각한 확대, 동맹이 5조 발동 언급.",

    # Event 9: Mojtaba Khamenei elected as new Supreme Leader
    "No physical damage political succession event amid ongoing war": "진행 중인 전쟁 중 물리적 피해 없음, 정치적 권력 승계 사건",
    "Attempt to reconstitute command authority after decapitation of senior leadership.": "고위 지도부 참수 후 지휘권 재구성 시도.",
    "Dynastic succession may consolidate hardliner control but leadership remains fragmented.": "왕조적 권력 승계가 강경파 통제를 공고히 할 수 있으나 지도부는 여전히 분열 상태.",

    # Event 10: US-Israeli strike on Khondab heavy water facility
    "Khondab heavy water production plant destroyed rendered inoperable": "콘다브 중수 생산 시설 파괴, 가동 불능 상태로 변함",
    "Targeted key component of nuclear fuel cycle infrastructure.": "핵연료 주기 인프라의 핵심 요소 표적.",
    "Part of systematic campaign to dismantle Irans nuclear program.": "이란 핵 프로그램 해체를 위한 체계적 캠페인의 일부.",

    # Event 11: US F-15E Strike Eagle shot down
    "F-15E shot down; A-10 lost during rescue; 4 Iranian soldiers killed including BG Masoud Zare; both US crew rescued": "F-15E 격추; 구조 작전 중 A-10 손실; 준장 마수드 자레 포함 이란군 4명 사망; 미군 승무원 2명 모두 구조",
    "Asymmetric threat MANPADS remain effective against low-flying aircraft despite US air superiority.": "미국의 공중 우위에도 불구하고 MANPADS는 저공 비행 항공기에 대한 비대칭 위협으로 유효함.",
    "High-profile shootdown tested limits of US air dominance; rescue became propaganda event for both sides.": "고위급 격추 사건이 미국의 공중 우위 한계를 시험했고, 구조 작전은 양측 모두의 선전 이벤트가 됨.",

    # Event 12: Iranian ballistic missiles kill 4 in Haifa
    "4 killed in residential building strike; fires in residential area; multiple impacts across central and northern Israel": "주거용 건물 피격으로 4명 사망; 주거 지역 화재; 중앙 및 북부 이스라엘 전역 다중 타격",
    "Targeted mixed military-civilian infrastructure in northern Israel to maximize pressure.": "압박을 극대화하기 위해 북부 이스라엘의 혼합 군민 인프라 표적.",
    "Direct Iran-Israel kinetic exchange signals willingness to accept escalation costs.": "직접적인 이란-이스라엘 무력 교환이 확대 비용 감수 의지를 신호함.",

    # Event 13: US-Israeli airstrike damages Sharif University
    "University mosque and fuel station damaged; 6 children killed in nearby residential area": "대학 모스크와 휘발유 충전소 손상; 인근 주거 지역에서 6명의 어린이 사망",
    "Collateral damage to civilian and educational infrastructure near military targets.": "군사 표적 근처의 민간 및 교육 인프라에 대한 부수 피해.",
    "Growing civilian toll raising international pressure and war crimes concerns.": "증가하는 민간 피해가 국제적 압박과 전쟁범죄 우려를 야기함.",

    # Event 14: Saudi Arabia intercepts 18 Iranian drones and 7 ballistic missiles
    "18 drones and 7 missiles intercepted; debris fell near energy facilities": "18개 무인기와 7개 미사일 요격; 잔해는 에너지 시설 근처에 추락",
    "Persistent attacks on Saudi energy sector to pressure Riyadh and disrupt oil exports.": "사우디 에너지 부문에 대한 지속적 공격으로 리야드 압박 및 석유 수출 교란.",
    "Economic warfare targeting global oil supply chain as leverage.": "글로벌 석유 공급망을 지렛대로 한 경제 전쟁.",

    # Event 15: Iranian drone strike wounds 15 Americans at Ali Al Salem airbase
    "15 US service members wounded": "미군 15명 부상",
    "Targeted key US air operations hub in Kuwait to degrade forward operations.": "전진 작전 능력을 저하시키기 위해 쿠웨이트의 핵심 미국 항공 작전 거점 표적.",
    "Persistent strikes on US bases demonstrate Irans sustained retaliatory capability.": "미국 기지에 대한 지속적 공격이 이란의 지속적 보복 능력을 입증함.",

    # Event 16: US strikes military targets on Kharg Island
    "Dozens of military targets destroyed; oil facilities reportedly not hit": "수십 개의 군사 표적 파괴; 석유 시설은 보도상 타격 받지 않음",
    "Degrading military assets on strategic island while avoiding oil infrastructure escalation.": "전략적 섬의 군사 자산 저하시키면서 석유 인프라 확대 회피.",
    "Pressure on Irans economic lifeline; Iran responded by removing restraint on regional oil targets.": "이란의 경제 생명선에 대한 압박; 이란이 지역 석유 표적에 대한 제약 제거로 대응.",

    # Event 17: Israel attacks 8 bridges and railway infrastructure
    "8 bridges destroyed; ~10 railway segments hit; 2 killed in Kashan bridge strike": "8개 다리 파괴; 약 10개 철도 구간 타격; 카샨 다리 공격으로 2명 사망",
    "Disrupting military logistics and weapons transport via rail network.": "철도망을 통한 군사 물자 및 무기 수송 교란.",
    "Infrastructure targeting escalation crossing into dual-use civilian targets.": "민간 겸용 표적을 포함하는 인프라 표적 확대.",

    # Event 18: Shootout at Israeli consulate in Istanbul
    "2 attackers killed; 2 police officers injured; consulate was unstaffed": "2명의 공격자 사살; 경찰관 2명 부상; 영사관은 직원 없는 상태였음",
    "Asymmetric attack on diplomatic target in neutral NATO country.": "중립적 NATO 국가의 외교 표적에 대한 비대칭 공격.",
    "Widening of conflict beyond Middle East theater terrorism nexus.": "중동 전구를 넘어선 분쟁 확대 및 테러리즘 연계 위험.",

    # Event 19: Trump threatens complete demolition
    "No immediate damage deadline/ultimatum; Iran rejects ceasefire proposals": "즉각적 피해 없음, 기한/최후통첩; 이란이 휴전 제안 거절",
    "Maximum pressure tactic using infrastructure destruction threats.": "인프라 파괴 위협을 이용한 최대 압박 전술.",
    "Critical inflection point potential escalation to targeting civilian power grid.": "민간 전력망 표적으로의 확대 가능성이 있는 중대한 전환점.",

    # Event 20: Israel strikes three airports in Tehran
    "3 airports struck; multiple planes and dozens of helicopters destroyed; synagogue destroyed": "3개 공항 타격; 다수 항공기 및 수십 대의 헬리콥터 파괴; 시나고그 파괴",
    "Targeting aviation assets to deny Iran air mobility and transport capability.": "이란의 항공 이동성 및 수송 능력을 차단하기 위해 항공 자산 표적.",
    "Systematic degradation of Iranian military logistics and air transport.": "이란군 물자 보급 및 항공 수송의 체계적 저하.",

    # Event 21: UAE air defenses intercept Iranian missiles and drones
    "Telecom building hit by drone; 1 injured by shrapnel in Abu Dhabi": "무인기에 의해 통신 건물 타격; 아부다비에서 파편에 의해 1명 부상",
    "Targeting critical civilian communications infrastructure in Gulf states.": "걸프 국가의 민간 통신 인프라 표적.",
    "Iran expanding target set to non-military infrastructure to increase pressure on neighbors.": "이웃 국가들의 압박을 증가시키기 위해 이란이 비군사 인프라로 표적 확대.",

    # Event 22: King Fahd Causeway closed
    "No physical damage causeway closed indefinitely as precaution": "물리적 피해 없음, 방호 조치로 인해 도로 무기한 폐쇄",
    "Iranian threats causing disruption without direct kinetic action.": "직접적 무력 행동 없이 이란 위협이 교란 야기.",
    "Demonstrates how conflict disrupts civilian life and commerce across Gulf region.": "분쟁이 걸프 지역 전역의 민간 생활과 상업을 어떻게 교란하는지 입증.",

    # Event 23: US B-2 bombers destroy Bandar Abbas power generation complex
    "Bandar Abbas power complex destroyed; ~2.5M residents without electricity; strategic port C2 degraded": "반다르아바스 전력 복합시설 파괴; 약 250만 주민 정전; 전략적 항구 지휘통제 저하",
    "Escalation to civilian-adjacent critical infrastructure per presidential directive.": "대통령 지시에 따라 민간 인접 중요 인프라로 확대.",
    "Crossing threshold into systematic civilian infrastructure targeting risks wider international condemnation.": "체계적인 민간 인프라 표적으로의 경계 통과는 더 광범위한 국제적 비난 위험.",

    # Event 24: Houthi forces sink MV Olympic Spirit
    "MV Olympic Spirit sunk; 3 crew killed, 17 rescued; Brent crude surges 11% to $142/bbl": "MV 올림픽 스피릿 침몰; 승무원 3명 사망, 17명 구조; 브렌트유 11% 급등해 배럴당 142달러",
    "Coordinated saturation attack overwhelming tankers defensive measures.": "유조선의 방어 조치를 압도하는 조직적 포화 공격.",
    "Irans asymmetric economic warfare via proxies pressuring global energy markets.": "대리세력을 통한 이란의 비대칭 경제전이 글로벌 에너지 시장을 압박.",

    # Event 25: Israel assassinates Esmail Ghaani
    "Quds Force commander Ghaani killed; 5 IRGC officers + 2 Hezbollah liaisons killed": "꾸드스군 사령관 가아니 사망; IRGC 장교 5명 + 헤즈볼라 연락관 2명 사망",
    "Surgical decapitation strike against proxy coordination hub in permissive airspace.": "작전 자유가 보장된 영공 내 대리세력 조율 거점에 대한 정밀 참수 타격.",
    "Removes key architect of Axis of Resistance operations degrading command of proxy war effort.": "저항의 축 작전의 핵심 설계자를 제거하여 대리전 지휘 체계를 약화.",

    # Event 26: Fattah-2 missile strikes Tel Aviv
    "HaKirya command complex struck; 23 IDF killed incl. BG; first confirmed hypersonic target penetration": "하키르야 사령부 복합시설 타격; IDF 23명 사망 중 준장 포함; 첫 확인된 극초음속 표적 관통",
    "Hypersonic glide vehicle defeated Israels layered defense demonstrating defense gap.": "극초음속 활공체가 이스라엘의 다층 방어를 돌파해 방어 공백 입증.",
    "Strategic shock to Israeli deterrence posture and invalidates assumptions of air defense supremacy.": "이스라엘의 억제력에 대한 전략적 충격, 공중 방어 우위 가정을 무효화.",

    # Event 27: China calls UN Security Council session
    "UNSC ceasefire resolution vetoed by US/UK; China announces naval deployment to Iran": "UNSC 휴전 결의안이 미국/영국에 의해 거부권 행사됨; 중국이 이란에 대한 해군 전개 발표",
    "Chinese naval deployment signals willingness to tie broader power competition to the conflict.": "중국 해군 전개가 분쟁에 강대국 경쟁을 연계하려는 의지를 시사함.",
    "Risk of great power entanglement rising sharply; global alignment crystallizing around war.": "강대국 개입 위험이 급격히 상승; 전쟁을 중심으로 글로벌 진영 구도 형성.",

    # Event 28: USS Thomas Hudner damaged
    "USS Thomas Hudner damaged; 7 sailors killed, 12 wounded; ship transits to Fujairah": "USS 토머스 허드너 호 손상; 선원 7명 사망, 12명 부상; 함선이 후자이라로 이동",
    "Asymmetric swarm tactic successfully penetrated layered ship defenses demonstrating CIWS saturation vulnerability.": "비대칭 군집 전술이 함선의 다층 방어를 성공적으로 관통해 CIWS 포화 취약성 입증.",
    "First significant US Navy surface combatant damage challenging US freedom-of-navigation posture.": "미국 해군 수상 전투함의 첫 중대 손상으로 미국의 해상 자유 항행 태세에 도전.",

    # Event 29: Mojtaba Khamenei killed in Mashhad
    "Supreme Leader Mojtaba Khamenei killed; ~40 senior clerics/IRGC officers killed; partial damage to Imam Reza shrine": "최고지도자 모즈타바 하메네이 사망; 약 40명의 고위 성직자/IRGC 장교 사망; 이맘 레자 성지 부분 손상",
    "Second successful decapitation strike removing recently-installed leadership.": "최근 설치된 지도부를 제거한 두 번째 성공적 참수 공격.",
    "Destruction near Shia holiest site triggers unprecedented protests; risks binding Shia populations worldwide to Iran cause.": "시아파 최고 성지 근처의 파괴가 사상 초유의 항의를 야기함; 전 세계 시아파 인구를 이란 대의에 결속시킬 위험.",

    # Event 30: Iraqi Shia militias storm US Embassy
    "Embassy compound breached; 14 attackers killed; staff evacuated; Iraqi PM orders US troop withdrawal": "대사관 구역 침입; 공격자 14명 사살; 직원 대피; 이라크 총리 미군 철수 명령",
    "Political-kinetic pressure forcing US retreat from Iraq an Iranian strategic objective since 2003.": "이라크에서의 미국 철수를 강요하는 정치-무력 압박은 2003년 이래 이란의 전략적 목표.",
    "Collapse of US position in Iraq hands Iran major strategic win reshaping regional balance.": "이라크에서의 미국 지위 붕괴가 이란에 지역 균형을 재편하는 주요 전략적 승리를 제공.",

    # Event 31: Oman mediates Iran-US back-channel talks
    "No physical damage; first confirmed direct Iran-US contact since February 28 war start": "물리적 피해 없음; 2월 28일 전쟁 시작 이후 첫 확인된 직접적 이란-미국 접촉",
    "Omani mediation channel offers face-saving de-escalation path for both sides.": "오만의 중재 채널이 양측 모두에게 체면을 살리는 완화 경로 제공.",
    "After 45 days of war exhaustion and domestic political costs may enable phased ceasefire.": "45일의 전쟁 소모와 국내 정치적 비용 이후 단계적 휴전이 가능할 수 있음.",

    # Event 32: Hezbollah launches largest salvo
    "11 Israeli civilians killed, 68 wounded; 47 Hezbollah operatives killed in retaliatory IDF strikes": "이스라엘 민간인 11명 사망, 68명 부상; IDF 보복 공격으로 헤즈볼라 대원 47명 사망",
    "Saturation attack nearly exhausted northern Iron Dome battery magazines.": "포화 공격이 북부 아이언돔 배터리 탄약고를 거의 소진함.",
    "Hezbollah signals ability to sustain high-intensity strikes indefinitely complicating Israeli strategic calculus.": "헤즈볼라가 고강도 공격의 무기한 지속 능력을 과시하며 이스라엘의 전략적 판단을 복잡하게 만듦.",

    # Event 33: Iran reopens Strait of Hormuz
    "Hormuz reopens; oil prices fall 8% to $118/bbl; first offensive pause since Feb 28": "호르무즈 재개항; 유가 8% 하락해 배럴당 118달러; 2월 28일 이후 첫 공격 중단",
    "Short pause allows both sides to rearm reconstitute and evaluate ceasefire framework.": "단기 중단이 양측이 재무장, 재정비하고 휴전 체계를 평가할 수 있게 함.",
    "First concrete de-escalation of the war; could become foundation for permanent ceasefire or collapse if any party breaks pause.": "전쟁의 첫 구체적 완화; 어떤 당사자가 휴전을 위반하면 항구적 휴전의 토대가 되거나 붕괴될 수 있음.",

    # Event 34: Israeli strikes in southern Lebanon (April 25, 2026)
    "6 killed, 17 injured in southern Lebanon strikes; Hezbollah downed one Israeli drone in retaliation; ceasefire violations cited by Lebanese Health Ministry": "남부 레바논 공습으로 6명 사망, 17명 부상; 헤즈볼라가 보복으로 이스라엘 무인기 1대 격추; 레바논 보건부가 휴전 위반 지적",
    "Targeted vehicles assessed by IDF as weapons-laden; Hezbollah retaliation localized to Israeli army vehicles in south Lebanon.": "IDF는 표적 차량을 무기 적재 차량으로 평가; 헤즈볼라의 보복은 남부 레바논 내 이스라엘군 차량으로 한정됨.",
    "Repeated strikes during the extended ceasefire test the durability of the April 17 truce and signal Israel's policy of acting against perceived imminent threats irrespective of pause terms.": "연장된 휴전 기간 중 반복된 공습이 4월 17일 휴전의 지속성을 시험하며, 이스라엘이 휴전 조건과 무관하게 임박한 위협으로 판단되는 표적에 대해 행동한다는 정책을 시사함.",

    # Event 35: Trump cancels Pakistan envoy trip (April 25, 2026)
    "Witkoff-Kushner Pakistan trip canceled; Iranian FM Araghchi had already left Islamabad; talks downgraded to telephone-only; ceasefire and US naval blockade continue": "위트코프·쿠슈너 특사의 파키스탄 방문 취소; 이란 외무장관 아락치는 이미 이슬라마바드 출국; 협상은 전화 통화로 축소; 휴전과 미 해상 봉쇄는 계속",
    "Last-minute cancellation reflects breakdown of in-person diplomatic format after Iranian side declined direct meeting; both governments shift to phone-based exchanges.": "막판 취소는 이란 측이 직접 회담을 거부한 이후 대면 외교 형식의 붕괴를 반영하며, 양국 정부 모두 전화 기반 교환으로 전환.",
    "Stalled negotiations sustain pressure-track diplomacy alongside the US naval blockade; raises risk of ceasefire collapse if no diplomatic breakthrough emerges in coming days.": "교착된 협상은 미 해상 봉쇄와 병행되는 압박 외교 기조를 유지시키며, 향후 며칠 내 외교적 돌파구가 나오지 않으면 휴전 붕괴 위험을 높임.",

    # Event 36: Araghchi departs to Oman (April 25, 2026)
    "Araghchi exits Islamabad after Pakistani round; arrives in Muscat for continued mediated regional talks; conditional on US diplomatic seriousness": "아락치, 파키스탄 회담 후 이슬라마바드 출국; 무스카트 도착해 중재 회담 계속; 미국의 외교적 진정성 여부에 조건부",
    "Iran consolidates around the Omani mediation channel after the Pakistani round failed to produce direct US contact.": "파키스탄 회담이 미국과의 직접 접촉을 만들어내지 못하자, 이란은 오만 중재 채널을 중심으로 외교 노선을 정비함.",
    "Reinforces Oman's role as the durable back-channel established earlier in the war; preserves diplomatic optionality without conceding to US pressure on the blockade.": "전쟁 초반에 자리잡은 오만의 비밀 외교 채널 역할을 강화; 봉쇄에 대한 미국의 압박에 굴복하지 않으면서 외교적 선택지를 보존.",

    # Event 37: US Navy intercepts M/V Sevan tanker (April 25, 2026)
    "M/V Sevan intercepted and redirected toward Iran; cumulative blockade redirects since April 13 reach 37 ships; three vessels previously seized for non-compliance": "M/V 세반호 차단 후 이란 방향으로 회항 조치; 4월 13일 봉쇄 개시 이후 누적 회항 조치 선박 37척 도달; 미준수 선박 3척은 사전 나포됨",
    "Successful interception of a newly sanctioned tanker demonstrates intelligence-driven blockade enforcement; non-kinetic redirect remained the standard outcome.": "새로 제재된 유조선의 성공적 차단은 정보 기반 봉쇄 집행 능력을 보여주며, 비물리적 회항 조치가 표준 결과로 유지됨.",
    "Sustained US naval blockade is the principal coercive instrument keeping Iran's oil exports near zero; Iran cites the blockade as a ceasefire violation while diplomatic channels remain open via Oman.": "지속되는 미 해상 봉쇄는 이란 원유 수출을 0에 가깝게 묶어두는 핵심 강압 수단이며, 이란은 봉쇄를 휴전 위반으로 규정하는 한편 오만 채널을 통한 외교 통로는 열어둠.",
}
