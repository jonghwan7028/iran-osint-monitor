"""
Multilingual translation service for OSINT incidents.
Provides contextually accurate translations following 5W1H principle
(Who, What, When, Where, Why, How) for all 7 supported languages.

Languages: KO (한국어), EN (English), ES (Español), ZH (中文), JA (日本語), FR (Français), DE (Deutsch)
"""
from __future__ import annotations

from app.services.ko_translate import (
    translate_actor as _ko_actor,
    translate_means as _ko_means,
    translate_location as _ko_location,
    translate_sentence as _ko_sentence,
)


# ─── Actor translations (WHO) ───
ACTOR_TRANSLATIONS: dict[str, dict[str, str]] = {
    "United States": {"ko": "미국", "es": "Estados Unidos", "zh": "美国", "ja": "米国", "fr": "États-Unis", "de": "USA"},
    "United States / Israel": {"ko": "미국/이스라엘", "es": "EE.UU./Israel", "zh": "美国/以色列", "ja": "米国/イスラエル", "fr": "États-Unis/Israël", "de": "USA/Israel"},
    "Israel": {"ko": "이스라엘", "es": "Israel", "zh": "以色列", "ja": "イスラエル", "fr": "Israël", "de": "Israel"},
    "Iran": {"ko": "이란", "es": "Irán", "zh": "伊朗", "ja": "イラン", "fr": "Iran", "de": "Iran"},
    "IRGC": {"ko": "이란 혁명수비대(IRGC)", "es": "Guardia Revolucionaria (CGRI)", "zh": "伊朗革命卫队(IRGC)", "ja": "イラン革命防衛隊(IRGC)", "fr": "Corps des Gardiens (CGRI)", "de": "Revolutionsgarde (IRGC)"},
    "Hezbollah": {"ko": "헤즈볼라", "es": "Hezbolá", "zh": "真主党", "ja": "ヒズボラ", "fr": "Hezbollah", "de": "Hisbollah"},
    "Hezbollah (Iran proxy)": {"ko": "헤즈볼라(이란 대리세력)", "es": "Hezbolá (aliado de Irán)", "zh": "真主党(伊朗代理人)", "ja": "ヒズボラ(イラン代理勢力)", "fr": "Hezbollah (proxy iranien)", "de": "Hisbollah (Iran-Stellvertreter)"},
    "Houthis": {"ko": "후티 반군", "es": "Hutíes", "zh": "胡塞武装", "ja": "フーシ派", "fr": "Houthis", "de": "Huthi-Rebellen"},
    "Houthi (Iran proxy)": {"ko": "후티 반군(이란 대리세력)", "es": "Hutíes (aliado de Irán)", "zh": "胡塞武装(伊朗代理人)", "ja": "フーシ派(イラン代理勢力)", "fr": "Houthis (proxy iranien)", "de": "Huthi-Rebellen (Iran-Stellvertreter)"},
    "Saudi Arabia": {"ko": "사우디아라비아", "es": "Arabia Saudita", "zh": "沙特阿拉伯", "ja": "サウジアラビア", "fr": "Arabie saoudite", "de": "Saudi-Arabien"},
    "Turkey": {"ko": "튀르키예", "es": "Turquía", "zh": "土耳其", "ja": "トルコ", "fr": "Turquie", "de": "Türkei"},
    "Turkey (NATO)": {"ko": "튀르키예(NATO 회원국)", "es": "Turquía (OTAN)", "zh": "土耳其(北约成员)", "ja": "トルコ(NATO加盟国)", "fr": "Turquie (OTAN)", "de": "Türkei (NATO)"},
    "China / Russia": {"ko": "중국/러시아", "es": "China/Rusia", "zh": "中国/俄罗斯", "ja": "中国/ロシア", "fr": "Chine/Russie", "de": "China/Russland"},
    "Oman (mediator)": {"ko": "오만(중재국)", "es": "Omán (mediador)", "zh": "阿曼(调解方)", "ja": "オマーン(仲介国)", "fr": "Oman (médiateur)", "de": "Oman (Vermittler)"},
    "Iraqi Shia Militias (Iran proxy)": {"ko": "이라크 시아파 민병대(이란 대리세력)", "es": "Milicias chiitas iraquíes (aliado de Irán)", "zh": "伊拉克什叶派民兵(伊朗代理人)", "ja": "イラク・シーア派民兵(イラン代理勢力)", "fr": "Milices chiites irakiennes (proxy iranien)", "de": "Irakische Schiitenmilizen (Iran-Stellvertreter)"},
    "Unknown": {"ko": "미상", "es": "Desconocido", "zh": "未知", "ja": "不明", "fr": "Inconnu", "de": "Unbekannt"},
}

# ─── Means translations (HOW) ───
MEANS_TRANSLATIONS: dict[str, dict[str, str]] = {
    "missile": {"ko": "미사일", "es": "misil", "zh": "导弹", "ja": "ミサイル", "fr": "missile", "de": "Rakete"},
    "ballistic missiles": {"ko": "탄도미사일", "es": "misiles balísticos", "zh": "弹道导弹", "ja": "弾道ミサイル", "fr": "missiles balistiques", "de": "Ballistikraketen"},
    "cruise missiles": {"ko": "순항미사일", "es": "misiles de crucero", "zh": "巡航导弹", "ja": "巡航ミサイル", "fr": "missiles de croisière", "de": "Marschflugkörper"},
    "tomahawk missiles": {"ko": "토마호크 순항미사일", "es": "misiles Tomahawk", "zh": "战斧巡航导弹", "ja": "トマホークミサイル", "fr": "missiles Tomahawk", "de": "Tomahawk-Raketen"},
    "drone": {"ko": "무인기(드론)", "es": "dron", "zh": "无人机", "ja": "ドローン", "fr": "drone", "de": "Drohne"},
    "drones": {"ko": "무인기(드론)", "es": "drones", "zh": "无人机", "ja": "ドローン", "fr": "drones", "de": "Drohnen"},
    "airstrike": {"ko": "공습", "es": "ataque aéreo", "zh": "空袭", "ja": "空爆", "fr": "frappe aérienne", "de": "Luftangriff"},
    "precision airstrike": {"ko": "정밀 공습", "es": "ataque aéreo de precisión", "zh": "精确空袭", "ja": "精密空爆", "fr": "frappe aérienne de précision", "de": "Präzisionsluftangriff"},
    "rocket": {"ko": "로켓", "es": "cohete", "zh": "火箭弹", "ja": "ロケット弾", "fr": "roquette", "de": "Rakete"},
    "fighter jet": {"ko": "전투기", "es": "caza", "zh": "战斗机", "ja": "戦闘機", "fr": "avion de chasse", "de": "Kampfjet"},
    "cyberattack": {"ko": "사이버 공격", "es": "ciberataque", "zh": "网络攻击", "ja": "サイバー攻撃", "fr": "cyberattaque", "de": "Cyberangriff"},
    "bombing": {"ko": "폭격", "es": "bombardeo", "zh": "轰炸", "ja": "爆撃", "fr": "bombardement", "de": "Bombardierung"},
    "submarine torpedo": {"ko": "잠수함 어뢰", "es": "torpedo submarino", "zh": "潜艇鱼雷", "ja": "潜水艦魚雷", "fr": "torpille sous-marine", "de": "U-Boot-Torpedo"},
    "gbu-57 bunker buster bombs": {"ko": "GBU-57 벙커버스터 폭탄", "es": "bombas antiúnker GBU-57", "zh": "GBU-57钻地弹", "ja": "GBU-57バンカーバスター", "fr": "bombes anti-bunker GBU-57", "de": "GBU-57 Bunkerbrecher"},
    "fattah-2 hypersonic glide vehicle": {"ko": "파타흐-2 극초음속 활공체", "es": "vehículo hipersónico Fattah-2", "zh": "法塔赫-2高超音速滑翔飞行器", "ja": "ファッターハ2極超音速滑空体", "fr": "planeur hypersonique Fattah-2", "de": "Fattah-2 Hyperschallgleitflugkörper"},
    "anti-ship ballistic missiles": {"ko": "대함 탄도미사일", "es": "misiles balísticos antibuque", "zh": "反舰弹道导弹", "ja": "対艦弾道ミサイル", "fr": "missiles balistiques antinavire", "de": "Anti-Schiff-Ballistikraketen"},
    "suicide drones": {"ko": "자살 무인기", "es": "drones suicidas", "zh": "自杀式无人机", "ja": "自爆型ドローン", "fr": "drones kamikazes", "de": "Kamikazedrohnen"},
    "back-channel diplomacy": {"ko": "비밀 외교 채널", "es": "diplomacia secreta", "zh": "秘密外交渠道", "ja": "裏チャンネル外交", "fr": "diplomatie secrète", "de": "Geheimdiplomatie"},
    "diplomatic ultimatum": {"ko": "외교적 최후통첩", "es": "ultimátum diplomático", "zh": "外交最后通牒", "ja": "外交的最後通牒", "fr": "ultimatum diplomatique", "de": "diplomatisches Ultimatum"},
    "strike": {"ko": "타격", "es": "ataque", "zh": "打击", "ja": "攻撃", "fr": "frappe", "de": "Angriff"},
}

# ─── Location translations (WHERE) ───
LOCATION_TRANSLATIONS: dict[str, dict[str, str]] = {
    "Tehran": {"ko": "테헤란", "es": "Teherán", "zh": "德黑兰", "ja": "テヘラン", "fr": "Téhéran", "de": "Teheran"},
    "Strait of Hormuz": {"ko": "호르무즈 해협", "es": "Estrecho de Ormuz", "zh": "霍尔木兹海峡", "ja": "ホルムズ海峡", "fr": "Détroit d'Ormuz", "de": "Straße von Hormus"},
    "Persian Gulf": {"ko": "페르시아만", "es": "Golfo Pérsico", "zh": "波斯湾", "ja": "ペルシャ湾", "fr": "Golfe Persique", "de": "Persischer Golf"},
    "Red Sea": {"ko": "홍해", "es": "Mar Rojo", "zh": "红海", "ja": "紅海", "fr": "Mer Rouge", "de": "Rotes Meer"},
    "Tel Aviv": {"ko": "텔아비브", "es": "Tel Aviv", "zh": "特拉维夫", "ja": "テルアビブ", "fr": "Tel Aviv", "de": "Tel Aviv"},
    "Haifa": {"ko": "하이파", "es": "Haifa", "zh": "海法", "ja": "ハイファ", "fr": "Haïfa", "de": "Haifa"},
    "Damascus": {"ko": "다마스쿠스", "es": "Damasco", "zh": "大马士革", "ja": "ダマスカス", "fr": "Damas", "de": "Damaskus"},
    "Baghdad": {"ko": "바그다드", "es": "Bagdad", "zh": "巴格达", "ja": "バグダッド", "fr": "Bagdad", "de": "Bagdad"},
    "Fordow": {"ko": "포르도", "es": "Fordow", "zh": "福尔多", "ja": "フォルドゥ", "fr": "Fordo", "de": "Fordo"},
    "Natanz": {"ko": "나탄즈", "es": "Natanz", "zh": "纳坦兹", "ja": "ナタンズ", "fr": "Natanz", "de": "Natans"},
    "Isfahan": {"ko": "이스파한", "es": "Isfahán", "zh": "伊斯法罕", "ja": "イスファハーン", "fr": "Ispahan", "de": "Isfahan"},
    "Northern Israel / Southern Lebanon": {"ko": "이스라엘 북부/레바논 남부", "es": "Norte de Israel / Sur del Líbano", "zh": "以色列北部/黎巴嫩南部", "ja": "イスラエル北部/レバノン南部", "fr": "Nord d'Israël / Sud du Liban", "de": "Nordisrael / Südlibanon"},
    "Kharg Island": {"ko": "카르그섬", "es": "Isla de Jarg", "zh": "哈尔克岛", "ja": "ハールク島", "fr": "Île de Kharg", "de": "Charg-Insel"},
}

# ─── Verified status translations ───
STATUS_TRANSLATIONS: dict[str, dict[str, str]] = {
    "confirmed": {"ko": "확인됨", "en": "Confirmed", "es": "Confirmado", "zh": "已确认", "ja": "確認済み", "fr": "Confirmé", "de": "Bestätigt"},
    "likely": {"ko": "유력", "en": "Likely", "es": "Probable", "zh": "可能", "ja": "有力", "fr": "Probable", "de": "Wahrscheinlich"},
    "claimed": {"ko": "주장", "en": "Claimed", "es": "Reclamado", "zh": "声称", "ja": "主張", "fr": "Revendiqué", "de": "Behauptet"},
    "disputed": {"ko": "논쟁중", "en": "Disputed", "es": "Disputado", "zh": "存争议", "ja": "論争中", "fr": "Contesté", "de": "Umstritten"},
    "retracted": {"ko": "철회됨", "en": "Retracted", "es": "Retirado", "zh": "已撤回", "ja": "撤回済み", "fr": "Rétracté", "de": "Zurückgezogen"},
    "partially_verified": {"ko": "부분 확인", "en": "Partially verified", "es": "Parcialmente verificado", "zh": "部分确认", "ja": "部分確認", "fr": "Partiellement vérifié", "de": "Teilweise bestätigt"},
}

# ─── Severity translations ───
SEVERITY_TRANSLATIONS: dict[str, dict[str, str]] = {
    "높음": {"ko": "높음", "en": "High", "es": "Alta", "zh": "高", "ja": "高", "fr": "Élevée", "de": "Hoch"},
    "중간": {"ko": "중간", "en": "Medium", "es": "Media", "zh": "中", "ja": "中", "fr": "Moyenne", "de": "Mittel"},
    "낮음": {"ko": "낮음", "en": "Low", "es": "Baja", "zh": "低", "ja": "低", "fr": "Faible", "de": "Niedrig"},
    "미상": {"ko": "미상", "en": "Unknown", "es": "Desconocido", "zh": "未知", "ja": "不明", "fr": "Inconnu", "de": "Unbekannt"},
}


def translate_actor_ml(actor: str | None, lang: str) -> str:
    """Translate actor name to specified language."""
    if not actor:
        return {"ko": "미상", "es": "Desconocido", "zh": "未知", "ja": "不明", "fr": "Inconnu", "de": "Unbekannt"}.get(lang, "Unknown")
    if lang == "en":
        return actor
    if lang == "ko":
        return _ko_actor(actor)
    # Check exact match first
    for key, translations in ACTOR_TRANSLATIONS.items():
        if actor.lower() == key.lower():
            return translations.get(lang, actor)
    # Check partial match
    for key, translations in sorted(ACTOR_TRANSLATIONS.items(), key=lambda kv: -len(kv[0])):
        if key.lower() in actor.lower():
            return translations.get(lang, actor)
    return actor


def translate_means_ml(means: str | None, lang: str) -> str:
    """Translate military means to specified language."""
    if not means:
        return {"ko": "미상", "es": "Desconocido", "zh": "未知", "ja": "不明", "fr": "Inconnu", "de": "Unbekannt"}.get(lang, "Unknown")
    if lang == "en":
        return means
    if lang == "ko":
        return _ko_means(means)
    lower = means.lower().strip()
    if lower in MEANS_TRANSLATIONS:
        return MEANS_TRANSLATIONS[lower].get(lang, means)
    # Try partial matching for compound means
    for key, translations in sorted(MEANS_TRANSLATIONS.items(), key=lambda kv: -len(kv[0])):
        if key in lower:
            return translations.get(lang, means)
    return means


def translate_location_ml(location: str | None, lang: str) -> str:
    """Translate location name to specified language."""
    if not location:
        return {"ko": "미상", "es": "Desconocido", "zh": "未知", "ja": "不明", "fr": "Inconnu", "de": "Unbekannt"}.get(lang, "Unknown")
    if lang == "en":
        return location
    if lang == "ko":
        return _ko_location(location)
    # Check exact and partial matches
    for key, translations in sorted(LOCATION_TRANSLATIONS.items(), key=lambda kv: -len(kv[0])):
        if key.lower() in location.lower():
            result = location
            import re
            result = re.sub(re.escape(key), translations.get(lang, key), result, flags=re.IGNORECASE)
            return result
    return location


def translate_status_ml(status: str | None, lang: str) -> str:
    """Translate verification status."""
    if not status:
        return "-"
    lower = status.lower().strip()
    if lower in STATUS_TRANSLATIONS:
        return STATUS_TRANSLATIONS[lower].get(lang, status)
    return status


def translate_severity_ml(severity: str | None, lang: str) -> str:
    """Translate severity level."""
    if not severity:
        return "-"
    if severity in SEVERITY_TRANSLATIONS:
        return SEVERITY_TRANSLATIONS[severity].get(lang, severity)
    return severity


# ─── 5W1H sentence translation (contextual) ───
# These provide full contextual translations for key incident descriptions

SENTENCE_TRANSLATIONS: dict[str, dict[str, str]] = {
    # === Damage summaries (WHAT happened) ===
    "Supreme Leader Khamenei killed; defense minister, IRGC commander, and multiple senior officials eliminated; ~2,000 targets struck in first days": {
        "es": "Líder supremo Jamenei muerto; ministro de defensa, comandante de la CGRI y múltiples altos funcionarios eliminados; ~2.000 objetivos alcanzados en los primeros días",
        "zh": "最高领袖哈梅内伊被击毙；国防部长、革命卫队指挥官及多名高级官员被消灭；开战初期约2000个目标被打击",
        "ja": "最高指導者ハメネイ殺害；国防大臣、IRGC司令官、複数の高官が排除；開戦初期に約2000の標的を攻撃",
        "fr": "Guide suprême Khamenei tué ; ministre de la défense, commandant du CGRI et de nombreux hauts responsables éliminés ; ~2 000 cibles frappées dans les premiers jours",
        "de": "Oberster Führer Chamenei getötet; Verteidigungsminister, IRGC-Kommandeur und zahlreiche Spitzenfunktionäre eliminiert; ~2.000 Ziele in den ersten Tagen getroffen",
    },
    "Multiple US bases hit; Dubai International Airport damaged; Strait of Hormuz closed to shipping": {
        "es": "Múltiples bases de EE.UU. atacadas; Aeropuerto Internacional de Dubái dañado; Estrecho de Ormuz cerrado al tráfico marítimo",
        "zh": "多处美军基地被击中；迪拜国际机场受损；霍尔木兹海峡航运被封锁",
        "ja": "複数の米軍基地に被弾；ドバイ国際空港が損傷；ホルムズ海峡の航行が封鎖",
        "fr": "Plusieurs bases américaines touchées ; Aéroport international de Dubaï endommagé ; Détroit d'Ormuz fermé à la navigation",
        "de": "Mehrere US-Stützpunkte getroffen; Internationaler Flughafen Dubai beschädigt; Straße von Hormus für Schifffahrt gesperrt",
    },
    "Airport damaged, all flights halted temporarily, reopened in limited capacity": {
        "es": "Aeropuerto dañado, todos los vuelos suspendidos temporalmente, reabierto con capacidad limitada",
        "zh": "机场受损，所有航班暂时停飞，以有限运力恢复运营",
        "ja": "空港損傷、全便一時停止、限定的に再開",
        "fr": "Aéroport endommagé, tous les vols suspendus temporairement, rouvert en capacité limitée",
        "de": "Flughafen beschädigt, alle Flüge vorübergehend eingestellt, eingeschränkt wiedereröffnet",
    },
    "IRIS Dena sunk; 87 killed, 32 rescued by Sri Lankan navy": {
        "es": "IRIS Dena hundido; 87 muertos, 32 rescatados por la Armada de Sri Lanka",
        "zh": "IRIS德纳号沉没；87人死亡，32人被斯里兰卡海军救起",
        "ja": "IRIS デナ号沈没；87名死亡、32名がスリランカ海軍により救助",
        "fr": "IRIS Dena coulé ; 87 tués, 32 secourus par la marine sri-lankaise",
        "de": "IRIS Dena versenkt; 87 Tote, 32 von der Marine Sri Lankas gerettet",
    },
    "Supreme Leader Khamenei killed along with family members and 7+ senior military/intelligence officials": {
        "es": "Líder supremo Jamenei muerto junto con familiares y más de 7 altos funcionarios militares/de inteligencia",
        "zh": "最高领袖哈梅内伊连同家人及7名以上高级军事/情报官员被击毙",
        "ja": "最高指導者ハメネイが家族および7名以上の軍事・情報高官とともに殺害",
        "fr": "Guide suprême Khamenei tué avec des membres de sa famille et plus de 7 hauts responsables militaires/du renseignement",
        "de": "Oberster Führer Chamenei zusammen mit Familienmitgliedern und 7+ hochrangigen Militär-/Geheimdienstbeamten getötet",
    },
    "Underground nuclear facilities at Fordow Natanz and Isfahan struck; did not fully collapse facilities per DIA assessment": {
        "es": "Instalaciones nucleares subterráneas de Fordow, Natanz e Isfahán atacadas; no colapsaron completamente según evaluación de la DIA",
        "zh": "福尔多、纳坦兹和伊斯法罕地下核设施被打击；根据DIA评估设施未完全坍塌",
        "ja": "フォルドゥ、ナタンズ、イスファハーンの地下核施設を攻撃；DIA評価によれば施設は完全には崩壊せず",
        "fr": "Installations nucléaires souterraines de Fordo, Natanz et Ispahan frappées ; pas entièrement détruites selon l'évaluation de la DIA",
        "de": "Unterirdische Nuklearanlagen in Fordo, Natans und Isfahan getroffen; laut DIA-Bewertung nicht vollständig zerstört",
    },
    "Khondab heavy water production plant destroyed rendered inoperable": {
        "es": "Planta de producción de agua pesada de Jondab destruida, inutilizable",
        "zh": "霍恩达布重水生产设施被摧毁，无法运行",
        "ja": "コンダブ重水生産施設が破壊され、運転不能に",
        "fr": "Usine de production d'eau lourde de Khondab détruite, rendue inutilisable",
        "de": "Schwerwasseranlage Chondab zerstört und betriebsunfähig gemacht",
    },
    "Missile intercepted by NATO air defense; debris fell in Hatay Province": {
        "es": "Misil interceptado por defensa aérea de la OTAN; restos cayeron en la provincia de Hatay",
        "zh": "导弹被北约防空系统拦截；碎片坠落哈塔伊省",
        "ja": "NATO防空網がミサイルを迎撃；残骸がハタイ県に落下",
        "fr": "Missile intercepté par la défense aérienne de l'OTAN ; débris tombés dans la province de Hatay",
        "de": "Rakete durch NATO-Luftabwehr abgefangen; Trümmer fielen in Provinz Hatay",
    },

    # === Tactical assessments (HOW / immediate military purpose) ===
    "Massive opening salvo targeting C2 infrastructure and leadership to paralyze Iranian command structure.": {
        "es": "Salva inicial masiva dirigida contra la infraestructura de mando y control (C2) y el liderazgo para paralizar la estructura de mando iraní.",
        "zh": "大规模首轮齐射，打击指挥控制(C2)基础设施和领导层，以瘫痪伊朗指挥体系。",
        "ja": "指揮統制(C2)インフラと指導部を標的とした大規模開戦一斉攻撃で、イラン指揮系統の麻痺を狙う。",
        "fr": "Salve d'ouverture massive ciblant l'infrastructure C2 et le commandement pour paralyser la structure de commandement iranienne.",
        "de": "Massive Eröffnungssalve gegen C2-Infrastruktur und Führung, um die iranische Kommandostruktur zu lähmen.",
    },
    "Decapitation strike designed to eliminate top-tier leadership and disrupt C2.": {
        "es": "Ataque de decapitación diseñado para eliminar al liderazgo de primer nivel y desestabilizar el mando y control.",
        "zh": "斩首行动，旨在消灭最高层领导并破坏指挥控制系统。",
        "ja": "最高指導層排除と指揮統制系統の撹乱を目的とした斬首作戦。",
        "fr": "Frappe de décapitation conçue pour éliminer les dirigeants de haut rang et désorganiser le commandement.",
        "de": "Enthauptungsschlag zur Eliminierung der obersten Führung und Störung der Kommandostruktur.",
    },
    "Broad retaliatory strikes to exact costs on US and regional allies simultaneously.": {
        "es": "Ataques de represalia amplios para infligir costos a EE.UU. y sus aliados regionales simultáneamente.",
        "zh": "广泛报复性打击，同时对美国及其地区盟友施加代价。",
        "ja": "米国と地域同盟国に同時に代償を強いる広範な報復攻撃。",
        "fr": "Frappes de représailles étendues pour imposer des coûts aux États-Unis et à leurs alliés régionaux simultanément.",
        "de": "Breit angelegte Vergeltungsschläge, um den USA und regionalen Verbündeten gleichzeitig Kosten aufzuerlegen.",
    },
    "Targeted critical civilian hub to demonstrate reach and disrupt regional operations.": {
        "es": "Ataque a infraestructura civil crítica para demostrar alcance y desestabilizar operaciones regionales.",
        "zh": "打击关键民用枢纽以展示打击范围并破坏地区运作。",
        "ja": "重要民間拠点を標的に攻撃範囲を示し、地域活動を妨害。",
        "fr": "Ciblage d'un hub civil critique pour démontrer la portée et perturber les opérations régionales.",
        "de": "Angriff auf kritische zivile Infrastruktur, um Reichweite zu demonstrieren und regionale Operationen zu stören.",
    },
    "Eliminated Iranian naval asset far from theater to deny force projection capability.": {
        "es": "Eliminación de activo naval iraní lejos del teatro de operaciones para negar capacidad de proyección de fuerza.",
        "zh": "在远离战区处消灭伊朗海军力量，以剥夺其力量投射能力。",
        "ja": "戦域から遠い場所でイラン海軍資産を排除し、戦力投射能力を否定。",
        "fr": "Destruction d'un navire iranien loin du théâtre d'opérations pour nier toute capacité de projection de force.",
        "de": "Zerstörung eines iranischen Marineschiffs weit vom Einsatzgebiet entfernt, um Machtprojektionsfähigkeit zu verweigern.",
    },
    "Proxy escalation opening a second front against Israel from Lebanon.": {
        "es": "Escalada por delegación que abre un segundo frente contra Israel desde Líbano.",
        "zh": "代理人升级行动，从黎巴嫩开辟对以色列的第二战线。",
        "ja": "レバノンからイスラエルに対する第二戦線を開く代理勢力によるエスカレーション。",
        "fr": "Escalade par procuration ouvrant un second front contre Israël depuis le Liban.",
        "de": "Stellvertreter-Eskalation eröffnet zweite Front gegen Israel vom Libanon aus.",
    },
    "Attempted to destroy deeply buried nuclear enrichment infrastructure.": {
        "es": "Intento de destruir la infraestructura de enriquecimiento nuclear profundamente enterrada.",
        "zh": "试图摧毁深埋的核浓缩基础设施。",
        "ja": "地下深く埋設された核濃縮インフラの破壊を試みた。",
        "fr": "Tentative de destruction des infrastructures d'enrichissement nucléaire profondément enfouies.",
        "de": "Versuch, die tief vergrabene Nuklearanreicherungsinfrastruktur zu zerstören.",
    },
    "Likely intended to degrade military operational capability or signal deterrence.": {
        "es": "Probablemente destinado a degradar la capacidad operativa militar o señalizar disuasión.",
        "zh": "可能旨在削弱军事作战能力或释放威慑信号。",
        "ja": "軍事作戦能力の低下または抑止シグナルの発信を意図したものと見られる。",
        "fr": "Probablement destiné à dégrader la capacité opérationnelle militaire ou à signaler la dissuasion.",
        "de": "Wahrscheinlich zur Schwächung der militärischen Einsatzfähigkeit oder als Abschreckungssignal gedacht.",
    },
    "Likely intended to disrupt military activity or signaling.": {
        "es": "Probablemente destinado a interrumpir la actividad militar o la señalización.",
        "zh": "可能旨在扰乱军事活动或信号传递。",
        "ja": "軍事活動またはシグナリングの妨害を意図したものと見られる。",
        "fr": "Probablement destiné à perturber l'activité militaire ou la signalisation.",
        "de": "Wahrscheinlich zur Störung militärischer Aktivitäten oder Signalgebung gedacht.",
    },

    # === Strategic assessments (WHY / broader significance) ===
    "US-Israel aim to induce regime change and permanently destroy Iran nuclear and ballistic missile programs.": {
        "es": "EE.UU. e Israel buscan inducir un cambio de régimen y destruir permanentemente los programas nucleares y de misiles balísticos de Irán.",
        "zh": "美以旨在促成政权更迭，并永久摧毁伊朗核武器和弹道导弹计划。",
        "ja": "米国・イスラエルは体制転換を誘導し、イランの核・弾道ミサイル計画を恒久的に破壊することを目指す。",
        "fr": "Les États-Unis et Israël visent à provoquer un changement de régime et détruire définitivement les programmes nucléaires et balistiques iraniens.",
        "de": "USA und Israel zielen auf Regimewechsel und dauerhafte Zerstörung der iranischen Nuklear- und Raketenprogramme.",
    },
    "Aimed at catalyzing regime collapse and preventing coordinated Iranian retaliation.": {
        "es": "Dirigido a catalizar el colapso del régimen e impedir una represalia iraní coordinada.",
        "zh": "旨在催化政权崩溃并阻止伊朗协调反击。",
        "ja": "体制崩壊の促進とイランの組織的報復の阻止を狙う。",
        "fr": "Visant à catalyser l'effondrement du régime et empêcher une riposte iranienne coordonnée.",
        "de": "Zielt auf Beschleunigung des Regimezusammenbruchs und Verhinderung koordinierter iranischer Vergeltung.",
    },
    "Iran uses Hormuz closure as strategic leverage to pressure ceasefire negotiations.": {
        "es": "Irán usa el cierre de Ormuz como palanca estratégica para presionar las negociaciones de alto el fuego.",
        "zh": "伊朗利用霍尔木兹海峡封锁作为战略筹码，向停火谈判施压。",
        "ja": "イランはホルムズ閉鎖を戦略的レバレッジとして停戦交渉に圧力をかける。",
        "fr": "L'Iran utilise la fermeture d'Ormuz comme levier stratégique pour faire pression sur les négociations de cessez-le-feu.",
        "de": "Iran nutzt Hormus-Sperrung als strategischen Hebel für Druck auf Waffenstillstandsverhandlungen.",
    },
    "Economic warfare disrupting aviation and commerce to pressure Gulf states.": {
        "es": "Guerra económica que interrumpe la aviación y el comercio para presionar a los estados del Golfo.",
        "zh": "通过扰乱航空和商业来对海湾国家施加经济战压力。",
        "ja": "航空・商業を妨害する経済戦争で湾岸諸国に圧力を加える。",
        "fr": "Guerre économique perturbant l'aviation et le commerce pour faire pression sur les États du Golfe.",
        "de": "Wirtschaftskrieg durch Störung von Luftfahrt und Handel zur Druckausübung auf Golfstaaten.",
    },
    "Demonstrates US willingness to strike Iranian assets globally.": {
        "es": "Demuestra la voluntad de EE.UU. de atacar activos iraníes a nivel global.",
        "zh": "表明美国愿意在全球范围内打击伊朗资产。",
        "ja": "イラン資産に対するグローバルな攻撃意志を示す。",
        "fr": "Démontre la volonté américaine de frapper les actifs iraniens à l'échelle mondiale.",
        "de": "Demonstriert US-Bereitschaft, iranische Güter weltweit anzugreifen.",
    },
    "Part of Irans Axis of Resistance strategy multi-front pressure on Israel.": {
        "es": "Parte de la estrategia del Eje de Resistencia de Irán: presión multifrontal sobre Israel.",
        "zh": "伊朗\u201c抵抗之弧\u201d战略的一部分：对以色列施加多线压力。",
        "ja": "イランの「抵抗の枢軸」戦略の一環として、イスラエルに多正面圧力をかける。",
        "fr": "Partie de la stratégie iranienne de l'Axe de la résistance : pression multi-fronts sur Israël.",
        "de": "Teil von Irans Achse-des-Widerstands-Strategie: Mehrfrontdruck auf Israel.",
    },
    "Core US war objective eliminating Irans nuclear breakout capability. Partial success only.": {
        "es": "Objetivo central de guerra de EE.UU.: eliminar la capacidad nuclear de Irán. Solo éxito parcial.",
        "zh": "美国核心战争目标：消除伊朗核突破能力。仅取得部分成功。",
        "ja": "イラン核保有能力除去という米国の核心的戦争目標。部分的成功にとどまる。",
        "fr": "Objectif de guerre central américain : éliminer la capacité nucléaire iranienne. Succès partiel uniquement.",
        "de": "Kernziel der US-Kriegsführung: Irans nukleare Ausbruchsfähigkeit eliminieren. Nur teilweiser Erfolg.",
    },
    "Likely linked to coercive diplomacy, deterrence signaling, or escalation management.": {
        "es": "Probablemente vinculado a diplomacia coercitiva, señalización de disuasión o gestión de la escalada.",
        "zh": "可能与强制外交、威慑信号传递或升级管控有关。",
        "ja": "強制外交、抑止シグナリング、またはエスカレーション管理と関連する可能性がある。",
        "fr": "Probablement lié à la diplomatie coercitive, à la dissuasion ou à la gestion de l'escalade.",
        "de": "Wahrscheinlich mit Zwangsdiplomatie, Abschreckungssignalen oder Eskalationsmanagement verbunden.",
    },
    "Significant escalation NATO territory affected alliance invoked Article 5 language.": {
        "es": "Escalada significativa: territorio de la OTAN afectado, la alianza invocó el lenguaje del Artículo 5.",
        "zh": "重大升级：北约领土受影响，联盟援引第五条措辞。",
        "ja": "重大なエスカレーション：NATO領域が影響を受け、同盟は第5条の文言を援用。",
        "fr": "Escalade significative : territoire de l'OTAN affecté, l'alliance a invoqué le langage de l'Article 5.",
        "de": "Signifikante Eskalation: NATO-Territorium betroffen, Bündnis berief sich auf Artikel-5-Formulierung.",
    },
    "Dynastic succession may consolidate hardliner control but leadership remains fragmented.": {
        "es": "La sucesión dinástica puede consolidar el control de los radicales, pero el liderazgo sigue fragmentado.",
        "zh": "世袭继承可能巩固强硬派控制，但领导层仍处于分裂状态。",
        "ja": "王朝的継承は強硬派支配を固めうるが、指導部は依然として分裂状態。",
        "fr": "La succession dynastique peut consolider le contrôle des durs, mais le leadership reste fragmenté.",
        "de": "Dynastische Nachfolge könnte Hardliner-Kontrolle festigen, aber die Führung bleibt fragmentiert.",
    },
}


def translate_sentence_ml(text: str | None, lang: str) -> str:
    """Translate a sentence to the specified language using 5W1H context.

    Tries exact match in SENTENCE_TRANSLATIONS first,
    then falls back to Korean translation for 'ko' or returns English for others.
    """
    if not text:
        return "-"
    if lang == "en":
        return text
    if lang == "ko":
        return _ko_sentence(text)

    # Try exact match
    if text in SENTENCE_TRANSLATIONS:
        result = SENTENCE_TRANSLATIONS[text].get(lang)
        if result:
            return result

    # Try stripped version
    stripped = text.strip().rstrip(".")
    if stripped in SENTENCE_TRANSLATIONS:
        result = SENTENCE_TRANSLATIONS[stripped].get(lang)
        if result:
            return result

    # For unregistered sentences, use deep-translator as fallback
    try:
        from deep_translator import GoogleTranslator
        lang_map = {"es": "es", "zh": "zh-CN", "ja": "ja", "fr": "fr", "de": "de"}
        target = lang_map.get(lang, lang)
        translated = GoogleTranslator(source="en", target=target).translate(text)
        return translated or text
    except Exception:
        return text
