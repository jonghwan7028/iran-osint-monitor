"""
사건 데이터 필드(피해요약/전술평가/전략평가/위치/행위자/수단)를
한국어 외 언어(es / zh / ja / fr / de) 로 번역한다.

기존 시스템은 UI 라벨만 다국어이고, 데이터 콘텐츠는 영어 원문이 그대로 노출되었다.
이 모듈은 시드 사건의 한국어 번역을 기반으로 다른 언어 매핑을 제공하고,
새로 수집된 사건은 영어 원문에 어휘 치환만 가볍게 적용한다.

- 시드 데이터(검증 이벤트)는 SENTENCE_ML 에 직접 등록.
- 미등록 문장은 영어 원문(soften 후) 을 fallback 으로 표시한다.
- "한국어/영어 외 언어" 를 선택해도 최소한 어색한 한·영 혼용은 발생하지 않는다.

설계 메모:
- 모든 시드 문장을 7개 언어로 손번역하기엔 비용이 크므로,
  *고빈도 키워드와 동사*만 다국어 매핑으로 갖추고,
  나머지 사실 부분(숫자·고유명사)은 그대로 둔다.
- 결과는 "혼용이지만 일관된 톤"이며, 영어/한국어 모드는 기존대로 자연스럽게 유지된다.
"""
from __future__ import annotations

import re
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# 1) 행위자(actor) — 7개 언어
# ---------------------------------------------------------------------------

ACTOR_ML: Dict[str, Dict[str, str]] = {
    # key = lower(en)
    "iran":         {"en": "Iran", "ko": "이란", "es": "Irán", "zh": "伊朗", "ja": "イラン", "fr": "Iran", "de": "Iran"},
    "united states":{"en": "United States", "ko": "미국", "es": "Estados Unidos", "zh": "美国", "ja": "アメリカ", "fr": "États-Unis", "de": "Vereinigte Staaten"},
    "us":           {"en": "US", "ko": "미국", "es": "EE.UU.", "zh": "美国", "ja": "米国", "fr": "É.-U.", "de": "USA"},
    "israel":       {"en": "Israel", "ko": "이스라엘", "es": "Israel", "zh": "以色列", "ja": "イスラエル", "fr": "Israël", "de": "Israel"},
    "idf":          {"en": "IDF", "ko": "이스라엘방위군", "es": "FDI", "zh": "以色列国防军", "ja": "イスラエル国防軍", "fr": "Tsahal", "de": "IDF"},
    "irgc":         {"en": "IRGC", "ko": "이란 혁명수비대", "es": "CGRI", "zh": "伊朗革命卫队", "ja": "イラン革命防衛隊", "fr": "Pasdaran (CGRI)", "de": "IRGC"},
    "hezbollah":    {"en": "Hezbollah", "ko": "헤즈볼라", "es": "Hezbolá", "zh": "真主党", "ja": "ヒズボラ", "fr": "Hezbollah", "de": "Hisbollah"},
    "houthis":      {"en": "Houthis", "ko": "후티 반군", "es": "Hutíes", "zh": "胡塞武装", "ja": "フーシ派", "fr": "Houthis", "de": "Huthi"},
    "houthi":       {"en": "Houthi", "ko": "후티 반군", "es": "Hutí", "zh": "胡塞武装", "ja": "フーシ派", "fr": "Houthi", "de": "Huthi"},
    "saudi arabia": {"en": "Saudi Arabia", "ko": "사우디아라비아", "es": "Arabia Saudí", "zh": "沙特阿拉伯", "ja": "サウジアラビア", "fr": "Arabie saoudite", "de": "Saudi-Arabien"},
    "uae":          {"en": "UAE", "ko": "UAE", "es": "EAU", "zh": "阿联酋", "ja": "UAE", "fr": "EAU", "de": "VAE"},
    "turkey":       {"en": "Turkey", "ko": "튀르키예", "es": "Turquía", "zh": "土耳其", "ja": "トルコ", "fr": "Turquie", "de": "Türkei"},
    "iraq":         {"en": "Iraq", "ko": "이라크", "es": "Irak", "zh": "伊拉克", "ja": "イラク", "fr": "Irak", "de": "Irak"},
    "syria":        {"en": "Syria", "ko": "시리아", "es": "Siria", "zh": "叙利亚", "ja": "シリア", "fr": "Syrie", "de": "Syrien"},
    "centcom":      {"en": "CENTCOM", "ko": "미 중부사령부", "es": "CENTCOM", "zh": "美国中央司令部", "ja": "米中央軍", "fr": "CENTCOM", "de": "CENTCOM"},
    "nato":         {"en": "NATO", "ko": "NATO", "es": "OTAN", "zh": "北约", "ja": "NATO", "fr": "OTAN", "de": "NATO"},
    "unknown":      {"en": "Unknown", "ko": "미상", "es": "Desconocido", "zh": "未知", "ja": "不明", "fr": "Inconnu", "de": "Unbekannt"},
    "n/a":          {"en": "N/A", "ko": "해당 없음", "es": "N/D", "zh": "无", "ja": "該当なし", "fr": "N/D", "de": "k.A."},
}


# ---------------------------------------------------------------------------
# 2) 수단(means) — 자주 등장하는 무기·전술
# ---------------------------------------------------------------------------

MEANS_ML: Dict[str, Dict[str, str]] = {
    "missile":           {"en": "missile", "ko": "미사일", "es": "misil", "zh": "导弹", "ja": "ミサイル", "fr": "missile", "de": "Rakete"},
    "missiles":          {"en": "missiles", "ko": "미사일", "es": "misiles", "zh": "导弹", "ja": "ミサイル", "fr": "missiles", "de": "Raketen"},
    "ballistic missile": {"en": "ballistic missile", "ko": "탄도미사일", "es": "misil balístico", "zh": "弹道导弹", "ja": "弾道ミサイル", "fr": "missile balistique", "de": "ballistische Rakete"},
    "ballistic missiles":{"en": "ballistic missiles", "ko": "탄도미사일", "es": "misiles balísticos", "zh": "弹道导弹", "ja": "弾道ミサイル", "fr": "missiles balistiques", "de": "ballistische Raketen"},
    "cruise missile":    {"en": "cruise missile", "ko": "순항미사일", "es": "misil de crucero", "zh": "巡航导弹", "ja": "巡航ミサイル", "fr": "missile de croisière", "de": "Marschflugkörper"},
    "drone":             {"en": "drone", "ko": "무인기(드론)", "es": "dron", "zh": "无人机", "ja": "無人機", "fr": "drone", "de": "Drohne"},
    "drones":            {"en": "drones", "ko": "무인기(드론)", "es": "drones", "zh": "无人机", "ja": "無人機", "fr": "drones", "de": "Drohnen"},
    "airstrike":         {"en": "airstrike", "ko": "공습", "es": "ataque aéreo", "zh": "空袭", "ja": "空爆", "fr": "frappe aérienne", "de": "Luftangriff"},
    "airstrikes":        {"en": "airstrikes", "ko": "공습", "es": "ataques aéreos", "zh": "空袭", "ja": "空爆", "fr": "frappes aériennes", "de": "Luftangriffe"},
    "rocket":            {"en": "rocket", "ko": "로켓", "es": "cohete", "zh": "火箭弹", "ja": "ロケット弾", "fr": "roquette", "de": "Rakete"},
    "rockets":           {"en": "rockets", "ko": "로켓", "es": "cohetes", "zh": "火箭弹", "ja": "ロケット弾", "fr": "roquettes", "de": "Raketen"},
    "cyberattack":       {"en": "cyberattack", "ko": "사이버 공격", "es": "ciberataque", "zh": "网络攻击", "ja": "サイバー攻撃", "fr": "cyberattaque", "de": "Cyberangriff"},
    "bombing":           {"en": "bombing", "ko": "폭격", "es": "bombardeo", "zh": "轰炸", "ja": "爆撃", "fr": "bombardement", "de": "Bombardierung"},
    "fighter jet":       {"en": "fighter jet", "ko": "전투기", "es": "caza", "zh": "战斗机", "ja": "戦闘機", "fr": "chasseur", "de": "Kampfjet"},
    "naval engagement":  {"en": "naval engagement", "ko": "해상 교전", "es": "combate naval", "zh": "海上交战", "ja": "海上戦闘", "fr": "combat naval", "de": "Seegefecht"},
    "diplomatic ultimatum": {"en": "diplomatic ultimatum", "ko": "외교적 최후통첩", "es": "ultimátum diplomático", "zh": "外交最后通牒", "ja": "外交最後通牒", "fr": "ultimatum diplomatique", "de": "diplomatisches Ultimatum"},
}


# ---------------------------------------------------------------------------
# 3) 검증 상태(verified_status)
# ---------------------------------------------------------------------------

STATUS_ML: Dict[str, Dict[str, str]] = {
    "verified":            {"en": "verified", "ko": "확인됨", "es": "verificado", "zh": "已核实", "ja": "確認済み", "fr": "vérifié", "de": "verifiziert"},
    "partially_verified":  {"en": "partially verified", "ko": "부분 확인", "es": "parcialmente verificado", "zh": "部分核实", "ja": "部分確認", "fr": "partiellement vérifié", "de": "teilweise verifiziert"},
    "unverified":          {"en": "unverified", "ko": "미확인", "es": "no verificado", "zh": "未核实", "ja": "未確認", "fr": "non vérifié", "de": "unverifiziert"},
    "confirmed":           {"en": "confirmed", "ko": "확인됨", "es": "confirmado", "zh": "已确认", "ja": "確認済み", "fr": "confirmé", "de": "bestätigt"},
    "claimed":             {"en": "claimed", "ko": "주장", "es": "reclamado", "zh": "宣称", "ja": "主張", "fr": "revendiqué", "de": "behauptet"},
    "disputed":            {"en": "disputed", "ko": "논쟁중", "es": "en disputa", "zh": "存在争议", "ja": "係争中", "fr": "contesté", "de": "umstritten"},
}


SEVERITY_ML: Dict[str, Dict[str, str]] = {
    "높음": {"en": "High", "ko": "높음", "es": "Alto", "zh": "高", "ja": "高", "fr": "Élevé", "de": "Hoch"},
    "중간": {"en": "Medium", "ko": "중간", "es": "Medio", "zh": "中", "ja": "中", "fr": "Moyen", "de": "Mittel"},
    "낮음": {"en": "Low", "ko": "낮음", "es": "Bajo", "zh": "低", "ja": "低", "fr": "Faible", "de": "Niedrig"},
    "미상": {"en": "Unknown", "ko": "미상", "es": "Desconocido", "zh": "未知", "ja": "不明", "fr": "Inconnu", "de": "Unbekannt"},
}


# ---------------------------------------------------------------------------
# 4) 위치(location) — 흔한 도시·지역만
# ---------------------------------------------------------------------------

LOCATION_ML: Dict[str, Dict[str, str]] = {
    "tehran":     {"en": "Tehran", "ko": "테헤란", "es": "Teherán", "zh": "德黑兰", "ja": "テヘラン", "fr": "Téhéran", "de": "Teheran"},
    "tel aviv":   {"en": "Tel Aviv", "ko": "텔아비브", "es": "Tel Aviv", "zh": "特拉维夫", "ja": "テルアビブ", "fr": "Tel-Aviv", "de": "Tel Aviv"},
    "jerusalem":  {"en": "Jerusalem", "ko": "예루살렘", "es": "Jerusalén", "zh": "耶路撒冷", "ja": "エルサレム", "fr": "Jérusalem", "de": "Jerusalem"},
    "isfahan":    {"en": "Isfahan", "ko": "이스파한", "es": "Isfahán", "zh": "伊斯法罕", "ja": "エスファハーン", "fr": "Ispahan", "de": "Isfahan"},
    "fordow":     {"en": "Fordow", "ko": "포르도", "es": "Fordow", "zh": "福尔多", "ja": "フォルドゥ", "fr": "Fordow", "de": "Fordo"},
    "natanz":     {"en": "Natanz", "ko": "나탄즈", "es": "Natanz", "zh": "纳坦兹", "ja": "ナタンズ", "fr": "Natanz", "de": "Natans"},
    "haifa":      {"en": "Haifa", "ko": "하이파", "es": "Haifa", "zh": "海法", "ja": "ハイファ", "fr": "Haïfa", "de": "Haifa"},
    "beirut":     {"en": "Beirut", "ko": "베이루트", "es": "Beirut", "zh": "贝鲁特", "ja": "ベイルート", "fr": "Beyrouth", "de": "Beirut"},
    "damascus":   {"en": "Damascus", "ko": "다마스쿠스", "es": "Damasco", "zh": "大马士革", "ja": "ダマスカス", "fr": "Damas", "de": "Damaskus"},
    "baghdad":    {"en": "Baghdad", "ko": "바그다드", "es": "Bagdad", "zh": "巴格达", "ja": "バグダッド", "fr": "Bagdad", "de": "Bagdad"},
    "muscat":     {"en": "Muscat", "ko": "무스카트", "es": "Mascate", "zh": "马斯喀特", "ja": "マスカット", "fr": "Mascate", "de": "Maskat"},
    "dubai":      {"en": "Dubai", "ko": "두바이", "es": "Dubái", "zh": "迪拜", "ja": "ドバイ", "fr": "Dubaï", "de": "Dubai"},
    "doha":       {"en": "Doha", "ko": "도하", "es": "Doha", "zh": "多哈", "ja": "ドーハ", "fr": "Doha", "de": "Doha"},
    "strait of hormuz": {"en": "Strait of Hormuz", "ko": "호르무즈 해협", "es": "Estrecho de Ormuz", "zh": "霍尔木兹海峡", "ja": "ホルムズ海峡", "fr": "Détroit d'Ormuz", "de": "Straße von Hormus"},
    "persian gulf":     {"en": "Persian Gulf", "ko": "페르시아만", "es": "Golfo Pérsico", "zh": "波斯湾", "ja": "ペルシャ湾", "fr": "Golfe Persique", "de": "Persischer Golf"},
    "red sea":          {"en": "Red Sea", "ko": "홍해", "es": "Mar Rojo", "zh": "红海", "ja": "紅海", "fr": "Mer Rouge", "de": "Rotes Meer"},
    "middle east":      {"en": "Middle East", "ko": "중동", "es": "Oriente Medio", "zh": "中东", "ja": "中東", "fr": "Moyen-Orient", "de": "Naher Osten"},
}


# ---------------------------------------------------------------------------
# 5) 다국어 사건 묘사 — 시드 이벤트의 핵심 카테고리만
# ---------------------------------------------------------------------------

# damage / tactical / strategic 의 흔한 한 줄 요약을 다국어로 직접 매핑
SUMMARY_ML: Dict[str, Dict[str, str]] = {
    # 사상자·피해
    "no casualties":      {"en": "No casualties.", "ko": "인명 피해 없음.", "es": "Sin víctimas.", "zh": "无人员伤亡。", "ja": "人的被害なし。", "fr": "Aucune victime.", "de": "Keine Opfer."},
    "minor damage":       {"en": "Minor damage.", "ko": "경미한 피해.", "es": "Daños menores.", "zh": "轻微损伤。", "ja": "軽微な損傷。", "fr": "Dégâts mineurs.", "de": "Geringe Schäden."},
    "major damage":       {"en": "Major damage.", "ko": "주요 피해.", "es": "Daños importantes.", "zh": "重大损伤。", "ja": "重大な損傷。", "fr": "Dégâts importants.", "de": "Erhebliche Schäden."},
    "severe damage":      {"en": "Severe damage.", "ko": "심각한 피해.", "es": "Daños graves.", "zh": "严重损伤。", "ja": "深刻な損傷。", "fr": "Dégâts sévères.", "de": "Schwere Schäden."},
    "casualties reported":{"en": "Casualties reported.", "ko": "사상자 보고됨.", "es": "Se reportaron víctimas.", "zh": "已报告人员伤亡。", "ja": "死傷者が報告された。", "fr": "Victimes signalées.", "de": "Opfer gemeldet."},
    # 전술·전략 평가 빈출 표현
    "deterrence signaling":   {"en": "Deterrence signaling.", "ko": "억제 신호 발신.", "es": "Señalización de disuasión.", "zh": "威慑信号。", "ja": "抑止のシグナル発信。", "fr": "Signalement de dissuasion.", "de": "Abschreckungssignal."},
    "escalation management":  {"en": "Escalation management.", "ko": "확전 관리.", "es": "Gestión de la escalada.", "zh": "升级管控。", "ja": "エスカレーション管理。", "fr": "Gestion de l'escalade.", "de": "Eskalationssteuerung."},
    "coercive diplomacy":     {"en": "Coercive diplomacy.", "ko": "강압 외교.", "es": "Diplomacia coercitiva.", "zh": "强制外交。", "ja": "強制外交。", "fr": "Diplomatie coercitive.", "de": "Zwangsdiplomatie."},
    "regime change pressure": {"en": "Regime change pressure.", "ko": "정권 교체 압박.", "es": "Presión de cambio de régimen.", "zh": "政权更迭施压。", "ja": "政権交代圧力。", "fr": "Pression pour un changement de régime.", "de": "Druck zum Regimewechsel."},
    "proxy escalation":       {"en": "Proxy escalation.", "ko": "대리세력 확전.", "es": "Escalada por proxy.", "zh": "代理人升级。", "ja": "代理勢力によるエスカレーション。", "fr": "Escalade par procuration.", "de": "Eskalation durch Stellvertreter."},
    "asymmetric attack":      {"en": "Asymmetric attack.", "ko": "비대칭 공격.", "es": "Ataque asimétrico.", "zh": "非对称攻击。", "ja": "非対称攻撃。", "fr": "Attaque asymétrique.", "de": "Asymmetrischer Angriff."},
}


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

ALL_LANGS = ["ko", "en", "es", "zh", "ja", "fr", "de"]


def _lookup(table: Dict[str, Dict[str, str]], value: Optional[str], lang: str) -> Optional[str]:
    if not value:
        return None
    key = value.strip().lower()
    if key in table:
        return table[key].get(lang)
    return None


def actor_in(lang: str, value: Optional[str]) -> str:
    return _lookup(ACTOR_ML, value, lang) or value or "-"


def means_in(lang: str, value: Optional[str]) -> str:
    if not value:
        return "-"
    # 콤마/슬래시 구분 처리
    parts = [p.strip() for p in re.split(r"[,/]", value) if p.strip()]
    out = []
    for p in parts:
        translated = _lookup(MEANS_ML, p, lang)
        out.append(translated if translated else p)
    sep = " · " if lang in ("ko", "ja", "zh") else ", "
    return sep.join(out)


def status_in(lang: str, value: Optional[str]) -> str:
    return _lookup(STATUS_ML, value, lang) or value or "-"


def severity_in(lang: str, value: Optional[str]) -> str:
    if not value:
        return "-"
    return SEVERITY_ML.get(value, {}).get(lang, value)


def location_in(lang: str, value: Optional[str]) -> str:
    if not value:
        return "-"
    # 여러 도시·지역이 섞인 위치명도 부분 치환
    out = value
    for key, mp in sorted(LOCATION_ML.items(), key=lambda kv: -len(kv[0])):
        if key in out.lower():
            target = mp.get(lang, mp["en"])
            out = re.sub(re.escape(key), target, out, flags=re.IGNORECASE)
    return out


def summary_in(lang: str, value: Optional[str]) -> str:
    """피해/전술/전략 요약. 매핑이 있으면 다국어, 없으면 영어 fallback."""
    if not value or value == "-":
        return "-"
    direct = _lookup(SUMMARY_ML, value, lang)
    if direct:
        return direct
    # fallback: 영문 원문 + soften
    if lang == "ko":
        return value  # 호출부에서 별도 처리
    if lang == "en":
        return value
    # 다른 언어는 짧은 핵심 키워드만 매핑
    out = value
    for key, mp in SUMMARY_ML.items():
        if key in out.lower():
            target = mp.get(lang, mp["en"])
            out = re.sub(re.escape(key), target, out, flags=re.IGNORECASE)
    return out
