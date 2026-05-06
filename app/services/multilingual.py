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

    # === Group A: Damage summaries (WHAT happened) ===
    "Multiple strikes on northern Israel; Hezbollah drone struck RAF Akrotiri base in Cyprus": {
        "es": "Múltiples ataques al norte de Israel; drone de Hezbolá golpeó la base RAF Akrotiri en Chipre",
        "zh": "以色列北部遭多次打击；真主党无人机击中塞浦路斯英国皇家空军阿克罗蒂里基地",
        "ja": "イスラエル北部への複数の攻撃；ヒズボラドローンがキプロスのRAFアクロティリ基地を攻撃",
        "fr": "Multiples frappes au nord d'Israël ; drone du Hezbollah a frappé la base RAF Akrotiri à Chypre",
        "de": "Mehrere Anschläge im Norden Israels; Hezbollah-Drohne traf RAF-Basis Akrotiri auf Zypern",
    },
    "F-15E shot down; A-10 lost during rescue; 4 Iranian soldiers killed including BG Masoud Zare; both US crew rescued": {
        "es": "F-15E derribado; A-10 perdido durante rescate; 4 soldados iraníes muertos incluyendo general Masoud Zare; ambas tripulaciones estadounidenses rescatadas",
        "zh": "F-15E被击落；A-10在救援中丧失；4名伊朗士兵阵亡，其中包括马苏德·扎雷准将；两个美国飞行员获救",
        "ja": "F-15E撃墜；救難中にA-10喪失；マスード・ザレ准将を含む4名のイラン兵が殺害；米国乗務員2名が救助される",
        "fr": "F-15E abattu ; A-10 perdu lors du sauvetage ; 4 soldats iraniens tués dont le général Masoud Zare ; deux équipages américains secourus",
        "de": "F-15E abgeschossen; A-10 bei Rettung verloren; 4 iranische Soldaten getötet, darunter General Masoud Zare; beide US-Besatzungen gerettet",
    },
    "4 killed in residential building strike; fires in residential area; multiple impacts across central and northern Israel": {
        "es": "4 muertos en ataque a edificio residencial; incendios en área residencial; múltiples impactos en Israel central y norte",
        "zh": "住宅楼被击中造成4人死亡；住宅区发生火灾；以色列中部和北部多处被击中",
        "ja": "住宅ビル攻撃で4人死亡；住宅地の火災；イスラエル中部・北部での複数の被弾",
        "fr": "4 tués dans une frappe sur immeuble résidentiel ; incendies dans zone résidentielle ; impacts multiples dans le centre et nord d'Israël",
        "de": "4 Tote bei Anschlag auf Wohngebäude; Brände in Wohngebiet; Mehrfachtreffer in Mittel- und Nordisrael",
    },
    "University mosque and fuel station damaged; 6 children killed in nearby residential area": {
        "es": "Mezquita universitaria y estación de combustible dañadas; 6 niños muertos en área residencial cercana",
        "zh": "大学清真寺和加油站受损；附近住宅区6名儿童丧生",
        "ja": "大学モスクとガソリンスタンドが損傷；近くの住宅地で6人の子どもが殺害される",
        "fr": "Mosquée universitaire et station-essence endommagées ; 6 enfants tués dans zone résidentielle adjacente",
        "de": "Universitätsmoschee und Tankstelle beschädigt; 6 Kinder in angrenzender Wohngebiet getötet",
    },
    "18 drones and 7 missiles intercepted; debris fell near energy facilities": {
        "es": "18 drones y 7 misiles interceptados; escombros cayeron cerca de instalaciones energéticas",
        "zh": "18架无人机和7枚导弹被拦截；碎片坠落在能源设施附近",
        "ja": "18機のドローンと7発のミサイルが迎撃される；残骸がエネルギー施設近くに落下",
        "fr": "18 drones et 7 missiles interceptés ; débris tombés près d'installations énergétiques",
        "de": "18 Drohnen und 7 Raketen abgefangen; Trümmer fielen in der Nähe von Energieeinrichtungen",
    },
    "15 US service members wounded": {
        "es": "15 miembros del servicio estadounidense heridos",
        "zh": "15名美国军人受伤",
        "ja": "米国軍人15名が負傷",
        "fr": "15 militaires américains blessés",
        "de": "15 US-Soldaten verwundet",
    },
    "Dozens of military targets destroyed; oil facilities reportedly not hit": {
        "es": "Docenas de objetivos militares destruidos; instalaciones petroleras aparentemente no alcanzadas",
        "zh": "数十个军事目标被摧毁；石油设施据报未被击中",
        "ja": "数十の軍事目標が破壊される；石油施設は未被弾と報告される",
        "fr": "Douzaines d'objectifs militaires détruits ; installations pétrolières apparemment non frappées",
        "de": "Dutzende Militärziele zerstört; Ölanlagen laut Bericht nicht getroffen",
    },
    "8 bridges destroyed; ~10 railway segments hit; 2 killed in Kashan bridge strike": {
        "es": "8 puentes destruidos; ~10 segmentos ferroviarios golpeados; 2 muertos en ataque a puente de Kashan",
        "zh": "8座桥梁被摧毁；约10段铁路被击中；卡尚桥梁打击中2人死亡",
        "ja": "8つの橋が破壊される；約10の鉄道区間が被弾；カシャン橋攻撃で2名死亡",
        "fr": "8 ponts détruits ; ~10 tronçons ferroviaires frappés ; 2 tués dans la frappe sur pont de Kashan",
        "de": "8 Brücken zerstört; ~10 Eisenbahnabschnitte getroffen; 2 Tote bei Anschlag auf Kashan-Brücke",
    },
    "2 attackers killed; 2 police officers injured; consulate was unstaffed": {
        "es": "2 atacantes muertos; 2 policías heridos; consulado estaba sin personal",
        "zh": "2名攻击者被击毙；2名警察受伤；领事馆无人值班",
        "ja": "2名の攻撃者が殺害される；2名の警察官が負傷；領事館は職員不在",
        "fr": "2 attaquants tués ; 2 agents de police blessés ; consulat était inoccupé",
        "de": "2 Angreifer getötet; 2 Polizisten verletzt; Konsulat war unbemannt",
    },
    "No immediate damage deadline/ultimatum; Iran rejects ceasefire proposals": {
        "es": "Sin daño inmediato; plazo/ultimátum; Irán rechaza propuestas de alto el fuego",
        "zh": "无直接损伤；截止期限/最后通牒；伊朗拒绝停火提案",
        "ja": "直接的損傷なし；期限/最後通牒；イランは停戦提案を拒否",
        "fr": "Pas de dommage immédiat ; délai/ultimatum ; l'Iran rejette les propositions de cessez-le-feu",
        "de": "Kein unmittelbarer Schaden; Frist/Ultimatum; Iran lehnt Waffenstillstandsvorschläge ab",
    },
    "3 airports struck; multiple planes and dozens of helicopters destroyed; synagogue destroyed": {
        "es": "3 aeropuertos atacados; múltiples aviones y docenas de helicópteros destruidos; sinagoga destruida",
        "zh": "3个机场被击中；多架飞机和数十架直升机被摧毁；犹太教堂被摧毁",
        "ja": "3つの空港が攻撃される；複数の航空機と数十のヘリコプターが破壊される；シナゴーグが破壊される",
        "fr": "3 aéroports frappés ; multiples avions et douzaines d'hélicoptères détruits ; synagogue détruite",
        "de": "3 Flughäfen getroffen; mehrere Flugzeuge und dutzende Hubschrauber zerstört; Synagoge zerstört",
    },
    "Telecom building hit by drone; 1 injured by shrapnel in Abu Dhabi": {
        "es": "Edificio de telecomunicaciones golpeado por dron; 1 herido por metralla en Abu Dabi",
        "zh": "电信大楼被无人机击中；阿布扎比1人被弹片伤害",
        "ja": "テレコム建物がドローンで被弾；アブダビで1名が破片で負傷",
        "fr": "Bâtiment télécom frappé par drone ; 1 blessé par éclats à Abu Dhabi",
        "de": "Telekommunikationsgebäude von Drohne getroffen; 1 durch Granatsplitter in Abu Dhabi verletzt",
    },
    "No physical damage causeway closed indefinitely as precaution": {
        "es": "Sin daño físico; calzada cerrada indefinidamente como precaución",
        "zh": "无物理损害；堤道无限期关闭作为预防措施",
        "ja": "物理的損傷なし；堤道は予防措置として無期限閉鎖",
        "fr": "Pas de dommage physique ; chaussée fermée indéfiniment par précaution",
        "de": "Kein physischer Schaden; Damm zu Vorsichtsmaßnahme auf unbestimmte Zeit geschlossen",
    },
    "Bandar Abbas power complex destroyed; ~2.5M residents without electricity; strategic port C2 degraded": {
        "es": "Complejo energético de Bandar Abbas destruido; ~2,5M residentes sin electricidad; C2 del puerto estratégico degradado",
        "zh": "班达尔阿巴斯电力综合设施被摧毁；约250万居民断电；战略港口C2能力下降",
        "ja": "バンダルアッバース電力複合施設破壊；約250万居民が停電；戦略的港湾の指揮統制能力が低下",
        "fr": "Complexe énergétique de Bandar Abbas détruit ; ~2,5M résidents sans électricité ; C2 du port stratégique dégradé",
        "de": "Energieanlage Bandar Abbas zerstört; ~2,5 Mio. Einwohner ohne Strom; strategischer Hafen-C2 beeinträchtigt",
    },
    "MV Olympic Spirit sunk; 3 crew killed, 17 rescued; Brent crude surges 11% to $142/bbl": {
        "es": "MV Olympic Spirit hundido; 3 tripulantes muertos, 17 rescatados; crudo Brent sube 11% a $142/barril",
        "zh": "MV奥林匹克精神号沉没；3名船员死亡，17人获救；布伦特原油飙升11%至142美元/桶",
        "ja": "MV オリンピック・スピリット号沈没；乗務員3名死亡、17名救助；ブレント原油11%上昇し142ドル/バレル",
        "fr": "MV Olympic Spirit coulé ; 3 marins tués, 17 secourus ; brut Brent monte de 11% à 142 $/bbl",
        "de": "MV Olympic Spirit versenkt; 3 Besatzungsmitglieder getötet, 17 gerettet; Brent-Rohöl steigt 11% auf 142 $/Barrel",
    },
    "Quds Force commander Ghaani killed; 5 IRGC officers + 2 Hezbollah liaisons killed": {
        "es": "Comandante de Fuerza Quds Ghaani muerto; 5 oficiales CGRI + 2 enlaces de Hezbolá muertos",
        "zh": "圣城军司令加尼被击毙；5名IRGC军官加2名真主党联络员被击毙",
        "ja": "クッズ部隊司令官ガーニが殺害される；5名のIRGC将校と2名のヒズボラ連絡官が殺害される",
        "fr": "Commandant de la Force Quds Ghaani tué ; 5 officiers IRGC + 2 liaisons Hezbollah tués",
        "de": "Quds-Kraft-Kommandeur Ghaani getötet; 5 IRGC-Offiziere + 2 Hezbollah-Verbindungsleute getötet",
    },
    "HaKirya command complex struck; 23 IDF killed incl. BG; first confirmed hypersonic target penetration": {
        "es": "Complejo de comando HaKirya atacado; 23 muertos de FDI incluyendo general; primera penetración de objetivo hipersónico confirmada",
        "zh": "哈基里亚指挥综合体被击中；以军23人阵亡，包括准将；首次确认极超音速目标穿透",
        "ja": "ハキリヤ司令部複合体が攻撃される；IDF23名殺害（準将含む）；初の確認された極超音速標的貫通",
        "fr": "Complexe de commandement HaKirya frappé ; 23 tués de l'IDF dont un général ; première pénétration de cible hypersonique confirmée",
        "de": "HaKirya-Kommandozentrale getroffen; 23 IDF-Tote incl. General; erste bestätigte Hyperschall-Zieldurchdringung",
    },
    "UNSC ceasefire resolution vetoed by US/UK; China announces naval deployment to Iran": {
        "es": "Resolución de alto el fuego de CSNU vetada por EE.UU./Reino Unido; China anuncia despliegue naval a Irán",
        "zh": "安理会停火决议遭美英否决；中国宣布向伊朗部署海军",
        "ja": "UN安保理停戦決議が米英により拒否される；中国がイランへの海軍展開を発表",
        "fr": "Résolution de cessez-le-feu du CSNU veto par États-Unis/Royaume-Uni ; Chine annonce déploiement naval en Iran",
        "de": "UN-Sicherheitsratsbeschuss über Waffenstillstand von USA/UK vetoed; China kündigt Marineeinsatz zum Iran an",
    },
    "USS Thomas Hudner damaged; 7 sailors killed, 12 wounded; ship transits to Fujairah": {
        "es": "USS Thomas Hudner dañado; 7 marineros muertos, 12 heridos; buque en tránsito a Fujairah",
        "zh": "USS托马斯·赫德纳号受损；7名水手死亡，12人受伤；船舶航向富查伊拉",
        "ja": "USS トマス・ハドナー号が損傷；乗組員7名死亡、12名負傷；船がフジャイラへ航行",
        "fr": "USS Thomas Hudner endommagé ; 7 marins tués, 12 blessés ; navire en transit vers Fujairah",
        "de": "USS Thomas Hudner beschädigt; 7 Matrosen getötet, 12 verwundet; Schiff fährt nach Fujairah",
    },
    "Supreme Leader Mojtaba Khamenei killed; ~40 senior clerics/IRGC officers killed; partial damage to Imam Reza shrine": {
        "es": "Líder supremo Mojtaba Jamenei muerto; ~40 clérigos superiores/oficiales CGRI muertos; daño parcial al santuario del Imán Reza",
        "zh": "最高领袖穆罕塔巴·哈梅内伊被击毙；约40名高级阿訇/IRGC军官被击毙；伊玛目礼萨圣陵部分受损",
        "ja": "最高指導者モジタバ・ハメネイが殺害される；約40名の高級聖職者/IRGC将校が殺害される；イマーム・レザー聖廟が部分的に損傷",
        "fr": "Guide suprême Mojtaba Khamenei tué ; ~40 dignitaires religieux/officiers IRGC tués ; dommage partiel au sanctuaire de l'Imam Reza",
        "de": "Oberster Führer Mojtaba Chamenei getötet; ~40 hohe Geistliche/IRGC-Offiziere getötet; Teilschaden am Imam-Reza-Schrein",
    },
    "Embassy compound breached; 14 attackers killed; staff evacuated; Iraqi PM orders US troop withdrawal": {
        "es": "Recinto de embajada penetrado; 14 atacantes muertos; personal evacuado; PM iraquí ordena retirada de tropas estadounidenses",
        "zh": "使馆大院被突破；14名攻击者被击毙；人员撤离；伊拉克总理命令美军撤出",
        "ja": "大使館敷地が突破される；14名の攻撃者が殺害される；職員が避難；イラク首相が米軍撤退を命じる",
        "fr": "Enceinte de l'ambassade franchie ; 14 attaquants tués ; personnel évacué ; PM irakien ordonne retrait des troupes américaines",
        "de": "Botschaftsgelände durchbrochen; 14 Angreifer getötet; Personal evakuiert; irakischer PM befiehlt US-Truppenabzug",
    },
    "No physical damage; first confirmed direct Iran-US contact since February 28 war start": {
        "es": "Sin daño físico; primer contacto directo confirmado Irán-EE.UU. desde inicio de guerra el 28 de febrero",
        "zh": "无物理损害；自2月28日战争开始以来首次确认的伊朗-美国直接接触",
        "ja": "物理的損傷なし；2月28日の戦争開始以来初の確認された直接的なイラン-米国接触",
        "fr": "Pas de dommage physique ; premier contact direct confirmé Iran-États-Unis depuis le début de la guerre le 28 février",
        "de": "Kein physischer Schaden; erste bestätigte direkte Iran-US-Kontakt seit Kriegsbeginn am 28. Februar",
    },
    "No physical damage political succession event amid ongoing war": {
        "es": "Sin daño físico; evento de sucesión política en medio de guerra en curso",
        "zh": "无物理损害；正在进行的战争期间的政治继承事件",
        "ja": "物理的損傷なし；進行中の戦争の中での政治的継承イベント",
        "fr": "Pas de dommage physique ; événement de succession politique au milieu de la guerre en cours",
        "de": "Kein physischer Schaden; Nachfolgeereignis inmitten des laufenden Krieges",
    },
    "11 Israeli civilians killed, 68 wounded; 47 Hezbollah operatives killed in retaliatory IDF strikes": {
        "es": "11 civiles israelíes muertos, 68 heridos; 47 operativos de Hezbolá muertos en ataques de represalia del FDI",
        "zh": "11名以色列平民死亡，68人受伤；IDF报复性打击中47名真主党武装分子被击毙",
        "ja": "イスラエル民間人11名死亡、68名負傷；IDF報復打撃で真主党戦闘員47名が殺害される",
        "fr": "11 civils israéliens tués, 68 blessés ; 47 combattants du Hezbollah tués dans les frappes de représailles de l'IDF",
        "de": "11 israelische Zivilisten getötet, 68 verwundet; 47 Hezbollah-Kämpfer bei Vergeltungsschlägen der IDF getötet",
    },
    "Hormuz reopens; oil prices fall 8% to $118/bbl; first offensive pause since Feb 28": {
        "es": "Ormuz reabre; precios del petróleo caen 8% a $118/barril; primera pausa ofensiva desde el 28 de febrero",
        "zh": "霍尔木兹海峡重新开放；油价下跌8%至118美元/桶；自2月28日以来首次停止进攻",
        "ja": "ホルムズが再開；油価が8%下落し118ドル/バレル；2月28日以来初の停止期間",
        "fr": "Ormuz rouvre ; prix du pétrole chutent de 8% à 118 $/bbl ; première pause offensive depuis le 28 février",
        "de": "Hormus wiedereröffnet; Ölpreise fallen 8% auf 118 $/Barrel; erste Offensive-Pause seit 28. Februar",
    },

    # === Group B: Tactical assessments (HOW / immediate military purpose) ===
    "Likely not intentionally aimed at Turkey missile overflew en route to other targets.": {
        "es": "Probablemente no intencionalmente apuntado a Turquía; misil sobrevoló en ruta hacia otros objetivos.",
        "zh": "可能不是有意针对土耳其；导弹在飞往其他目标的途中飞越领空。",
        "ja": "おそらくトルコを意図的に狙ったものではない；ミサイルは他の目標への航行中に上空を通過した。",
        "fr": "Probablement pas intentionnellement dirigé vers la Turquie ; missile a survolé en route vers d'autres cibles.",
        "de": "Wahrscheinlich nicht absichtlich auf die Türkei abzielt; Rakete überflog auf dem Weg zu anderen Zielen.",
    },
    "Attempt to reconstitute command authority after decapitation of senior leadership.": {
        "es": "Intento de reconstituir la autoridad de mando después de la decapitación del liderazgo superior.",
        "zh": "在高级领导遭斩首后试图重新建立指挥权。",
        "ja": "上級指導部の斬首後、指揮権の再構成を試みる。",
        "fr": "Tentative de reconstituer l'autorité de commandement après la décapitation de la haute direction.",
        "de": "Versuch, die Befehlsgewalt nach der Enthauptung der Führung wiederherzustellen.",
    },
    "Targeted key component of nuclear fuel cycle infrastructure.": {
        "es": "Objetivo clave de la infraestructura del ciclo del combustible nuclear.",
        "zh": "打击核燃料循环基础设施的关键组成部分。",
        "ja": "核燃料サイクル基盤設備の重要構成要素を標的にした。",
        "fr": "Ciblage d'un composant clé de l'infrastructure du cycle du combustible nucléaire.",
        "de": "Angriff auf Schlüsselkomponente der Infrastruktur des Atombrennstoffkreislaufs.",
    },
    "Asymmetric threat MANPADS remain effective against low-flying aircraft despite US air superiority.": {
        "es": "La amenaza asimétrica de MANPADS sigue siendo efectiva contra aeronaves de vuelo bajo a pesar de la superioridad aérea estadounidense.",
        "zh": "尽管美国空中优势，非对称威胁MANPAD对低空飞行器仍然有效。",
        "ja": "米国の航空優位性にもかかわらず、非対称的脅威MANPADSは低空飛行航空機に対して有効なままである。",
        "fr": "La menace asymétrique des MANPAD reste efficace contre les aéronefs volant à basse altitude malgré la supériorité aérienne américaine.",
        "de": "Asymmetrische Bedrohung MANPAD bleibt trotz US-Luftüberlegenheit gegen Tiefflugler wirksam.",
    },
    "Targeted mixed military-civilian infrastructure in northern Israel to maximize pressure.": {
        "es": "Infraestructura militar-civil mixta dirigida al norte de Israel para maximizar la presión.",
        "zh": "打击以色列北部的混合军民基础设施以最大化压力。",
        "ja": "イスラエル北部の混合軍民インフラを標的に圧力を最大化した。",
        "fr": "Infrastructure militaro-civile mixte ciblée au nord d'Israël pour maximiser la pression.",
        "de": "Gemischte Militär-Zivil-Infrastruktur in Nordisrael zum Druckaufbau angegriffen.",
    },
    "Collateral damage to civilian and educational infrastructure near military targets.": {
        "es": "Daño colateral a infraestructura civil y educativa cerca de objetivos militares.",
        "zh": "对军事目标附近的民用和教育基础设施的附带损害。",
        "ja": "軍事目標近くの民間および教育インフラへの随伴被害。",
        "fr": "Dommage collatéral aux infrastructures civiles et éducatives près des objectifs militaires.",
        "de": "Begleitschaden an Zivil- und Bildungsinfrastruktur in der Nähe von Militärzielen.",
    },
    "Persistent attacks on Saudi energy sector to pressure Riyadh and disrupt oil exports.": {
        "es": "Ataques persistentes al sector energético saudí para presionar a Riad y disrumpir exportaciones petroleras.",
        "zh": "对沙特能源部门的持续攻击，以施压利雅得并中断石油出口。",
        "ja": "サウジアラビア湾岸地域圧力をかけ、石油輸出を遮断するための継続的な攻撃。",
        "fr": "Attaques persistantes contre le secteur énergétique saoudien pour faire pression sur Riyad et perturber les exportations de pétrole.",
        "de": "Anhaltende Anschläge auf den saudischen Energiesektor zur Druckausübung auf Riad und Unterbrechung der Ölausfuhren.",
    },
    "Targeted key US air operations hub in Kuwait to degrade forward operations.": {
        "es": "Centro clave de operaciones aéreas estadounidenses en Kuwait objetivo para degradar operaciones adelantadas.",
        "zh": "打击科威特关键的美国空中行动枢纽，以削弱前沿作战。",
        "ja": "クウェートの主要な米国空中作戦ハブを標的に前方作戦を低下させた。",
        "fr": "Ciblage du centre clé des opérations aériennes américaines au Koweït pour dégrader les opérations avancées.",
        "de": "Schlüssel-US-Luftoperationszentrum in Kuwait angegriffen, um Vorwärtsoperationen zu beeinträchtigen.",
    },
    "Degrading military assets on strategic island while avoiding oil infrastructure escalation.": {
        "es": "Degradación de activos militares en isla estratégica evitando escalada de infraestructura petrolera.",
        "zh": "在战略岛屿上削弱军事资产，同时避免石油基础设施升级。",
        "ja": "戦略的島嶼での軍事資産の低下、石油インフラ升級の回避。",
        "fr": "Dégradation des actifs militaires sur île stratégique tout en évitant l'escalade de l'infrastructure pétrolière.",
        "de": "Beeinträchtigung militärischer Vermögenswerte auf strategischer Insel unter Vermeidung von Öl-Infrastruktur-Eskalation.",
    },
    "Disrupting military logistics and weapons transport via rail network.": {
        "es": "Disrumpción de logística militar y transporte de armas a través de red ferroviaria.",
        "zh": "通过铁路网络中断军事后勤和武器运输。",
        "ja": "鉄道網を通じた軍事後方支援と武器輸送の遮断。",
        "fr": "Perturbation de la logistique militaire et du transport d'armes via le réseau ferroviaire.",
        "de": "Unterbrechung von Militärlogistik und Waffentransport über Eisenbahnnetz.",
    },
    "Asymmetric attack on diplomatic target in neutral NATO country.": {
        "es": "Ataque asimétrico a objetivo diplomático en país NATO neutral.",
        "zh": "对中立北约国家外交目标的非对称攻击。",
        "ja": "中立のNATO加盟国の外交目標への非対称攻撃。",
        "fr": "Attaque asymétrique contre cible diplomatique dans pays OTAN neutre.",
        "de": "Asymmetrischer Angriff auf diplomatisches Ziel in neutralem NATO-Land.",
    },
    "Maximum pressure tactic using infrastructure destruction threats.": {
        "es": "Táctica de máxima presión utilizando amenazas de destrucción de infraestructura.",
        "zh": "使用基础设施破坏威胁的最大压力战术。",
        "ja": "インフラ破壊の脅迫を使った最大圧力戦術。",
        "fr": "Tactique de pression maximale utilisant menaces de destruction d'infrastructure.",
        "de": "Maximaler Drucktaktik unter Verwendung von Infrastruktur-Zerstörungsdrohungen.",
    },
    "Targeting aviation assets to deny Iran air mobility and transport capability.": {
        "es": "Objetivo de activos aeronáuticos para negar a Irán movilidad aérea y capacidad de transporte.",
        "zh": "打击航空资产以剥夺伊朗的空中机动和运输能力。",
        "ja": "航空資産を標的にイランの空中機動性と輸送能力を否定した。",
        "fr": "Ciblage des actifs aéronautiques pour refuser à l'Iran la mobilité aérienne et la capacité de transport.",
        "de": "Angriff auf Luftfahrtanlagen, um dem Iran Luftmobilität und Transportfähigkeit zu verweigern.",
    },
    "Targeting critical civilian communications infrastructure in Gulf states.": {
        "es": "Infraestructura civil de comunicaciones crítica en estados del Golfo como objetivo.",
        "zh": "打击海湾国家关键民用通信基础设施。",
        "ja": "湾岸諸国の重要な民間通信インフラを標的にした。",
        "fr": "Infrastructure civile de communications critiques dans états du Golfe comme cible.",
        "de": "Kritische zivile Kommunikationsinfrastruktur in Golfstaaten angegriffen.",
    },
    "Iranian threats causing disruption without direct kinetic action.": {
        "es": "Amenazas iraníes causando disrumpción sin acción cinética directa.",
        "zh": "伊朗威胁在没有直接动能作用的情况下造成中断。",
        "ja": "イランの脅迫が直接的な運動エネルギー作用なしで混乱を引き起こす。",
        "fr": "Menaces iraniennes causant perturbation sans action cinétique directe.",
        "de": "Iranische Drohungen verursachen Störungen ohne direkte kinetische Aktion.",
    },
    "Escalation to civilian-adjacent critical infrastructure per presidential directive.": {
        "es": "Escalada a infraestructura crítica adyacente a civiles según directiva presidencial.",
        "zh": "根据总统指令升级至平民相邻的关键基础设施。",
        "ja": "大統領令による民間隣接の重要基盤施設へのエスカレーション。",
        "fr": "Escalade vers infrastructure critique adjacente aux civils selon directive présidentielle.",
        "de": "Eskalation zu zivilnaher kritischer Infrastruktur gemäß Präsidentialdirektive.",
    },
    "Coordinated saturation attack overwhelming tankers defensive measures.": {
        "es": "Ataque de saturación coordinado abrumando medidas defensivas de buques cisterna.",
        "zh": "协调的饱和攻击，淘汰油轮的防御措施。",
        "ja": "タンカーの防御措置を圧倒する調整された飽和攻撃。",
        "fr": "Attaque de saturation coordonnée dépassant mesures défensives des pétroliers.",
        "de": "Koordinierter Sättigungsangriff überwältigte Tankschiff-Abwehrmaßnahmen.",
    },
    "Surgical decapitation strike against proxy coordination hub in permissive airspace.": {
        "es": "Ataque de decapitación quirúrgica contra centro de coordinación de delegados en espacio aéreo permisivo.",
        "zh": "在允许的空域中对代理协调枢纽进行精准斩首打击。",
        "ja": "許容空域内の代理協調拠点に対する外科的斬首打撃。",
        "fr": "Frappe de décapitation chirurgicale contre hub de coordination des délégués dans espace aérien permissif.",
        "de": "Chirurgischer Enthauptungsschlag gegen Proxy-Koordinierungszentrum im erlaubten Luftraum.",
    },
    "Hypersonic glide vehicle defeated Israels layered defense demonstrating defense gap.": {
        "es": "Vehículo de planeo hipersónico derrotó defensa escalonada israelí demostrando brecha defensiva.",
        "zh": "极超音速滑翔飞行器击破以色列分层防御，暴露防御漏洞。",
        "ja": "極超音速滑空体がイスラエルの多層防御を突破し、防御ギャップを示した。",
        "fr": "Véhicule de planeur hypersonique a vaincu défense échelonnée israélienne démontrant brèche défensive.",
        "de": "Hyperschall-Gleitflugkörper durchbrach Israels mehrstufige Verteidigung, offenbart Verteidigungslücke.",
    },
    "Chinese naval deployment signals willingness to tie broader power competition to the conflict.": {
        "es": "Despliegue naval chino señala disposición a vincular competencia de poder más amplia al conflicto.",
        "zh": "中国海军部署表明愿意将更广泛的权力竞争与冲突联系起来。",
        "ja": "中国海軍展開はより広範な権力競争を紛争に結びつける意思を示唆している。",
        "fr": "Déploiement naval chinois signale volonté de lier concurrence de pouvoir plus large au conflit.",
        "de": "Chinesischer Marineeinsatz signalisiert Bereitschaft, breitere Machtkonkurrenz mit dem Konflikt zu verbinden.",
    },
    "Asymmetric swarm tactic successfully penetrated layered ship defenses demonstrating CIWS saturation vulnerability.": {
        "es": "Táctica de enjambre asimétrica penetró exitosamente defensas escalonadas de buque demostrando vulnerabilidad de saturación CIWS.",
        "zh": "非对称集群战术成功穿透分层舰船防御，展现CIWS饱和漏洞。",
        "ja": "非対称的スウォーム戦術は分層化された艦船防御を成功裏に貫通し、CIWS飽和脆弱性を示した。",
        "fr": "Tactique d'essaim asymétrique a avec succès pénétré défenses échelonnées du navire démontrant vulnérabilité saturation CIWS.",
        "de": "Asymmetrische Schwarmtaktik durchbrach erfolgreich mehrstufige Schiffsabwehr, zeigt CIWS-Sättigungsschwachstelle.",
    },
    "Second successful decapitation strike removing recently-installed leadership.": {
        "es": "Segundo ataque de decapitación exitoso eliminando liderazgo recientemente instalado.",
        "zh": "第二次成功的斩首打击，消除最近安装的领导层。",
        "ja": "最近就任した指導部を排除する2度目の成功した斬首打撃。",
        "fr": "Deuxième frappe de décapitation réussie éliminant leadership récemment installé.",
        "de": "Zweiter erfolgreicher Enthauptungsschlag entfernt kürzlich installierte Führung.",
    },
    "Political-kinetic pressure forcing US retreat from Iraq an Iranian strategic objective since 2003.": {
        "es": "Presión política-cinética forzando retirada estadounidense de Irak, objetivo estratégico iraní desde 2003.",
        "zh": "政治-运动压力强制美国从伊拉克撤退，伊朗自2003年以来的战略目标。",
        "ja": "政治・運動圧力が米国のイラク撤退を強制し、イランの2003年以来の戦略目標。",
        "fr": "Pression politico-cinétique forçant retraite américaine d'Irak, objectif stratégique iranien depuis 2003.",
        "de": "Politisch-kinetischer Druck zwingt US-Rückzug aus dem Irak, iranisches Strategisches Ziel seit 2003.",
    },
    "Omani mediation channel offers face-saving de-escalation path for both sides.": {
        "es": "Canal de mediación omaní ofrece camino de desescalada que salva la cara para ambos lados.",
        "zh": "阿曼调解渠道为双方提供体面的降级途径。",
        "ja": "オマーン仲介チャネルは両者のための面目を保った緩和路線を提供する。",
        "fr": "Canal de médiation omanais offre chemin de désescalade sauvant la face pour les deux côtés.",
        "de": "Omanischer Vermittlungskanal bietet gesichtswahrend Deeskalationspfad für beide Seiten.",
    },
    "Saturation attack nearly exhausted northern Iron Dome battery magazines.": {
        "es": "Ataque de saturación casi agota cartuchos de batería Iron Dome norte.",
        "zh": "饱和攻击几乎耗尽北方铁穹电池弹药库。",
        "ja": "飽和攻撃は北部アイアンドーム電池弾薬庫をほぼ消耗した。",
        "fr": "Attaque de saturation a presque épuisé magasins batterie Iron Dome nord.",
        "de": "Sättigungsangriff erschöpfte Nordliche Iron-Dome-Batterie-Magazine fast.",
    },
    "Short pause allows both sides to rearm reconstitute and evaluate ceasefire framework.": {
        "es": "Pausa corta permite a ambos lados rearmarse, reconstituirse y evaluar marco de alto el fuego.",
        "zh": "短暂停顿允许双方重新武装、重建和评估停火框架。",
        "ja": "短い一時停止により両側が再武装、再構成し、停戦枠組みを評価できる。",
        "fr": "Pause courte permet aux deux côtés de se réarmer, se reconstituer et évaluer cadre cessez-le-feu.",
        "de": "Kurze Pause erlaubt beiden Seiten, sich aufzurüsten, wiederherzustellen und Waffenstillstandsrahmen zu bewerten.",
    },
    "Part of systematic campaign to dismantle Irans nuclear program.": {
        "es": "Parte de campaña sistemática para desmantelar programa nuclear de Irán.",
        "zh": "拆除伊朗核计划的系统性运动的一部分。",
        "ja": "イラン核計画を解体する系統的キャンペーンの一部。",
        "fr": "Partie de campagne systématique pour démanteler programme nucléaire iranien.",
        "de": "Teil systematischer Kampagne zur Zerschlagung des Iranischen Kernprogramms.",
    },

    # === Group C: Strategic assessments (WHY / broader significance) ===
    "High-profile shootdown tested limits of US air dominance; rescue became propaganda event for both sides.": {
        "es": "Derribo de alto perfil probó límites de dominio aéreo estadounidense; rescate se convirtió en evento de propaganda para ambos lados.",
        "zh": "高调击落测试了美国空中优势的极限；救援成为双方的宣传事件。",
        "ja": "高い地位の撃墨は米国の航空優位性の限界を試し、救援は両側の宣伝イベントになった。",
        "fr": "Abattage de haut profil a testé limites de la domination aérienne américaine ; sauvetage devenu événement propagande pour deux côtés.",
        "de": "Hochkarätiger Abschuss testete US-Luftüberlegenheitsgrenzen; Rettung wurde Propagandaevent für beide Seiten.",
    },
    "Direct Iran-Israel kinetic exchange signals willingness to accept escalation costs.": {
        "es": "Intercambio cinético directo Irán-Israel señala disposición de aceptar costos de escalada.",
        "zh": "伊朗-以色列直接运动交换表明愿意接受升级成本。",
        "ja": "イラン-イスラエル直接運動交換は升级コストを受け入れる意思を示唆している。",
        "fr": "Échange cinétique direct Iran-Israël signale volonté d'accepter coûts d'escalade.",
        "de": "Direkter Iran-Israel-Kinetic-Austausch signalisiert Bereitschaft, Eskalationskosten zu akzeptieren.",
    },
    "Growing civilian toll raising international pressure and war crimes concerns.": {
        "es": "Creciente número de civiles aumenta presión internacional y preocupaciones de crímenes de guerra.",
        "zh": "不断增长的平民伤亡引发国际压力和战争罪行担忧。",
        "ja": "増加する民間人死傷者は国際圧力と戦争犯罪懸念を高める。",
        "fr": "Montée du nombre de civiles exacerbe pression internationale et préoccupations crimes de guerre.",
        "de": "Wachsende Ziviltoten erhöhen internationalen Druck und Kriegsverbrechensbedenken.",
    },
    "Economic warfare targeting global oil supply chain as leverage.": {
        "es": "Guerra económica dirigida a cadena de suministro de petróleo global como palanca.",
        "zh": "针对全球石油供应链的经济战争作为杠杆。",
        "ja": "グローバル石油供給チェーンを標的にした経済戦争をレバレッジとして。",
        "fr": "Guerre économique ciblant chaîne d'approvisionnement pétrolière mondiale comme levier.",
        "de": "Wirtschaftskrieg gegen globale Ölversorgungskette als Hebel.",
    },
    "Persistent strikes on US bases demonstrate Irans sustained retaliatory capability.": {
        "es": "Ataques persistentes en bases estadounidenses demuestran capacidad de represalia sostenida de Irán.",
        "zh": "对美国基地的持续打击展示伊朗的持续报复能力。",
        "ja": "米軍基地への継続的な打撃はイランの持続的な報復能力を示している。",
        "fr": "Frappes persistantes sur bases américaines démontrent capacité de représailles soutenue d'Iran.",
        "de": "Anhaltende Anschläge auf US-Basen zeigen Irans anhaltende Vergeltungsfähigkeit.",
    },
    "Pressure on Irans economic lifeline; Iran responded by removing restraint on regional oil targets.": {
        "es": "Presión sobre la vena de vida económica de Irán; Irán respondió removiendo restricción en objetivos petroleros regionales.",
        "zh": "对伊朗经济命脉的压力；伊朗通过解除对地区油气目标的限制来回应。",
        "ja": "イランの経済的生命線への圧力；イランは地域石油目標への制限を削除することで対応した。",
        "fr": "Pression sur la veine de vie économique d'Iran ; Iran a répondu en supprimant restriction sur objectifs pétroliers régionaux.",
        "de": "Druck auf Irans wirtschaftliche Lebensader; Iran reagierte durch Entfernung von Beschränkungen auf regionale Ölziele.",
    },
    "Infrastructure targeting escalation crossing into dual-use civilian targets.": {
        "es": "Escalada de objetivo de infraestructura cruzando hacia objetivos civiles de doble uso.",
        "zh": "基础设施目标升级，跨越到双用民间目标。",
        "ja": "インフラ目標エスカレーション、双用民間目標に越境。",
        "fr": "Escalade de ciblage d'infrastructure franchissant objectifs civiles à double usage.",
        "de": "Infrastrukturziele-Eskalation überschreitet Dual-Use-Zivile-Ziele.",
    },
    "Widening of conflict beyond Middle East theater terrorism nexus.": {
        "es": "Ampliación del conflicto más allá del nexo de terrorismo del teatro Medio Oriente.",
        "zh": "冲突超越中东地区恐怖主义关联的扩大。",
        "ja": "中東地域テロリズム関係を越えた紛争の拡大。",
        "fr": "Élargissement du conflit au-delà du nexe terrorisme du théâtre Moyen-Orient.",
        "de": "Erweiterung des Konflikts über Mittlerer Osten Theater Terrorismus Nexus hinaus.",
    },
    "Demonstrates how conflict disrupts civilian life and commerce across Gulf region.": {
        "es": "Demuestra cómo el conflicto disrumpe la vida civil y el comercio en toda la región del Golfo.",
        "zh": "展示冲突如何破坏海湾地区的民间生活和商业。",
        "ja": "紛争が湾岸地域全体の民間生活と商業をどのように混乱させるかを示す。",
        "fr": "Démontre comment le conflit perturbe la vie civile et le commerce dans toute la région du Golfe.",
        "de": "Zeigt, wie der Konflikt das Zivilleben und den Handel in der gesamten Golfregion stört.",
    },
    "Iran expanding target set to non-military infrastructure to increase pressure on neighbors.": {
        "es": "Irán expandiendo conjunto de objetivos a infraestructura no militar para aumentar presión en vecinos.",
        "zh": "伊朗将目标扩展至非军事基础设施，以增加对邻近国家的压力。",
        "ja": "イランが非軍事インフラへの目標範囲を拡大し、隣国への圧力を増加させる。",
        "fr": "Iran élargissant ensemble d'objectifs vers infrastructure non-militaire pour augmenter pression sur voisins.",
        "de": "Iran erweitert Zielgruppe auf zivile Infrastruktur, um Druck auf Nachbarn zu erhöhen.",
    },
    "Crossing threshold into systematic civilian infrastructure targeting risks wider international condemnation.": {
        "es": "Cruzando umbral hacia objetivo sistemático de infraestructura civil riesga condena internacional más amplia.",
        "zh": "跨越系统性民用基础设施目标的阈值，冒险更广泛的国际谴责。",
        "ja": "系統的民間インフラ目標の閾値を越え、より広い国際的非難のリスク。",
        "fr": "Franchissant seuil vers ciblage systématique infrastructure civile risque condamnation internationale plus large.",
        "de": "Überschreitung des Schwellwerts zu systematischen Zivil-Infrastruktur-Zielen birgt breitere internationale Verurteilung.",
    },
    "Irans asymmetric economic warfare via proxies pressuring global energy markets.": {
        "es": "Guerra económica asimétrica de Irán vía delegados presionando mercados energéticos globales.",
        "zh": "伊朗通过代理人进行的非对称经济战争对全球能源市场施加压力。",
        "ja": "イランの代理を通じた非対称経済戦争がグローバルエネルギー市場に圧力をかける。",
        "fr": "Guerre économique asymétrique d'Iran via délégués pressurisant marchés énergétiques globaux.",
        "de": "Irans asymmetrischer Wirtschaftskrieg über Proxy übt Druck auf globale Energiemärkte aus.",
    },
    "Removes key architect of Axis of Resistance operations degrading command of proxy war effort.": {
        "es": "Elimina arquitecto clave de operaciones del Eje de Resistencia degradando comando del esfuerzo de guerra por delegación.",
        "zh": "消除\"抵抗之弧\"行动的关键建筑师，降低代理战争努力的指挥。",
        "ja": "抵抗の枢軸作戦の主要設計者を削除し、代理戦争の指揮を低下させる。",
        "fr": "Élimine architecte clé des opérations Axe de la résistance dégradant commande effort guerre par procuration.",
        "de": "Entfernt Schlüsselarchitekt der Achse-des-Widerstands-Operationen, degradiert Proxy-Kriegsbefehl.",
    },
    "Strategic shock to Israeli deterrence posture and invalidates assumptions of air defense supremacy.": {
        "es": "Choque estratégico a postura de disuasión israelí e invalida suposiciones de supremacía de defensa aérea.",
        "zh": "对以色列威慑态势的战略冲击，否定防空优势的假设。",
        "ja": "イスラエルの抑止態勢への戦略的ショック、防空優位性の仮定を無効化。",
        "fr": "Choc stratégique à posture de dissuasion israélienne et invalide hypothèses de suprématie défense aérienne.",
        "de": "Strategischer Schock für israelische Abschreckungshaltung und invalidiert Annahmen von Luftabwehrüberlegenheit.",
    },
    "Risk of great power entanglement rising sharply; global alignment crystallizing around war.": {
        "es": "Riesgo de enredamiento de potencias mayores aumentando bruscamente; alineación global cristalizando alrededor de guerra.",
        "zh": "大国纠缠的风险大幅上升；全球对齐在战争周围结晶。",
        "ja": "大国関与のリスク急上昇；グローバル同盟戦争周辺で結晶化。",
        "fr": "Risque d'enchevêtrement de grandes puissances augmentant fortement ; alignement global cristallisant autour de guerre.",
        "de": "Risiko großmächtiger Verstrickung steigt stark; globale Ausrichtung um Krieg kristallisierend.",
    },
    "First significant US Navy surface combatant damage challenging US freedom-of-navigation posture.": {
        "es": "Primer daño significativo de combatiente de superficie de Armada estadounidense desafiando postura de libertad de navegación estadounidense.",
        "zh": "首次重大美国海军水面战斗舰损伤，挑战美国航行自由态势。",
        "ja": "米国海軍水上戦闘艦初の重大損傷、米国の航海の自由態勢に異議。",
        "fr": "Premier dommage significatif combattant de surface marine américaine défiant posture liberté de navigation américaine.",
        "de": "Erster signifikanter US-Marine-Oberflächenkampfschiff-Schaden, der US-Navigationsfreiheitshaltung herausfordert.",
    },
    "Destruction near Shia holiest site triggers unprecedented protests; risks binding Shia populations worldwide to Iran cause.": {
        "es": "Destrucción cerca del sitio más sagrado chiíta desencadena protestas sin precedentes; riesgo de vincular poblaciones chiítas mundiales a causa iraní.",
        "zh": "什叶派最圣地附近的破坏引发前所未有的抗议；冒险将全球什叶派人口与伊朗事业联系起来的风险。",
        "ja": "シーア派最聖地近くの破壊は前例のない抗議を引き起こす；シーア派世界人口をイランの大義に結びつけるリスク。",
        "fr": "Destruction près site le plus saint chiite déclenche protestations sans précédent ; risque liant populations chiites mondiales à cause iranienne.",
        "de": "Zerstörung bei heiligster Schia-Stätte löst beispiellose Proteste aus; Risiko der Bindung Schia-Bevölkerungen weltweit an iranische Sache.",
    },
    "Collapse of US position in Iraq hands Iran major strategic win reshaping regional balance.": {
        "es": "Colapso de posición estadounidense en Irak entrega a Irán victoria estratégica importante remodelando equilibrio regional.",
        "zh": "美国在伊拉克的地位崩溃给伊朗带来重大战略胜利，重塑地区平衡。",
        "ja": "イラクでの米国の地位崩壊がイランに大きな戦略的勝利をもたらし、地域バランスを再形成。",
        "fr": "Effondrement position américaine en Irak confère à Iran victoire stratégique importante remodelant équilibre régional.",
        "de": "Zusammenbruch der US-Position im Irak gibt dem Iran großen strategischen Sieg, der regionales Gleichgewicht umgestaltet.",
    },
    "After 45 days of war exhaustion and domestic political costs may enable phased ceasefire.": {
        "es": "Después de 45 días de guerra, agotamiento y costos políticos domésticos pueden habilitar alto el fuego por fases.",
        "zh": "45天战争后，疲惫和国内政治成本可能促成分阶段停火。",
        "ja": "45日間の戦争後、疲弊と国内政治的コストは段階的停戦を可能にする可能性がある。",
        "fr": "Après 45 jours de guerre, épuisement et coûts politiques domestiques peuvent permettre cessez-le-feu par phases.",
        "de": "Nach 45 Tagen Krieg können Erschöpfung und inländische politische Kosten gestaffelte Waffenstillstand ermöglichen.",
    },
    "Hezbollah signals ability to sustain high-intensity strikes indefinitely complicating Israeli strategic calculus.": {
        "es": "Hezbollah señala capacidad de sostener ataques de alta intensidad indefinidamente complicando cálculo estratégico israelí.",
        "zh": "真主党表明能够无限期地维持高强度打击，复杂化以色列战略计算。",
        "ja": "ヒズボラは無期限に高強度攻撃を維持する能力を示唆し、イスラエルの戦略計算を複雑化させている。",
        "fr": "Hezbollah signale capacité soutenir frappes haute intensité indéfiniment compliquant calcul stratégique israélien.",
        "de": "Hezbollah signalisiert Fähigkeit, hochintensive Anschläge auf unbestimmte Zeit aufrechtzuerhalten, was israelische Strategieberechnung erschwert.",
    },
    "First concrete de-escalation of the war; could become foundation for permanent ceasefire or collapse if any party breaks pause.": {
        "es": "Primera desescalada concreta de la guerra; podría convertirse en fundación para alto el fuego permanente o colapso si cualquier lado rompe pausa.",
        "zh": "战争首次具体降级；如果任何一方打破停顿，可能成为永久停火基础或崩溃。",
        "ja": "戦争初の具体的なエスカレーション；いずれかの当事者が停止を破った場合、永続的停戦の基礎になるか崩壊する可能性がある。",
        "fr": "Première désescalade concrète de la guerre ; pourrait devenir fondation pour cessez-le-feu permanent ou effondrement si tout côté rompt pause.",
        "de": "Erste konkrete Deeskalation des Krieges; könnte zur Grundlage für dauerhaften Waffenstillstand werden oder zusammenbrechen, wenn eine Partei Pause bricht.",
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
    "Likely linked to coercive diplomacy, deterrence signaling, or escalation management.": {
        "es": "Probablemente vinculado a diplomacia coercitiva, señalización de disuasión o gestión de la escalada.",
        "zh": "可能与强制外交、威慑信号传递或升级管控有关。",
        "ja": "強制外交、抑止シグナリング、またはエスカレーション管理と関連する可能性がある。",
        "fr": "Probablement lié à la diplomatie coercitive, à la dissuasion ou à la gestion de l'escalade.",
        "de": "Wahrscheinlich mit Zwangsdiplomatie, Abschreckungssignalen oder Eskalationsmanagement verbunden.",
    },
    "Proxy escalation opening a second front against Israel from Lebanon.": {
        "es": "Escalada por delegación que abre un segundo frente contra Israel desde Líbano.",
        "zh": "代理人升级行动，从黎巴嫩开辟对以色列的第二战线。",
        "ja": "レバノンからイスラエルに対する第二戦線を開く代理勢力によるエスカレーション。",
        "fr": "Escalade par procuration ouvrant un second front contre Israël depuis le Liban.",
        "de": "Stellvertreter-Eskalation eröffnet zweite Front gegen Israel vom Libanon aus.",
    },
    "Attempt to reconstitute command authority after decapitation of senior leadership.": {
        "es": "Intento de reconstituir la autoridad de mando tras la eliminación del liderazgo superior.",
        "zh": "在高层领导被消灭后试图重建指挥权威。",
        "ja": "最高指導部の排除後、指揮権の再構築を試みる。",
        "fr": "Tentative de reconstituer l'autorité de commandement après l'élimination de la direction.",
        "de": "Versuch, die Befehlsgewalt nach Enthauptung der Führung wiederherzustellen.",
    },
    "Targeted key component of nuclear fuel cycle infrastructure.": {
        "es": "Objetivo clave de la infraestructura del ciclo de combustible nuclear.",
        "zh": "打击核燃料循环基础设施的关键组成部分。",
        "ja": "核燃料サイクルインフラの重要構成要素を標的とした。",
        "fr": "Ciblage d'un composant clé de l'infrastructure du cycle du combustible nucléaire.",
        "de": "Angriff auf Schlüsselkomponente der Kernbrennstoffkreislauf-Infrastruktur.",
    },
    "Asymmetric threat MANPADS remain effective against low-flying aircraft despite US air superiority.": {
        "es": "Amenaza asimétrica: los MANPADS siguen siendo eficaces contra aeronaves de vuelo bajo pese a la superioridad aérea de EE.UU.",
        "zh": "非对称威胁：尽管美国拥有制空权，便携式防空导弹对低空飞行器仍然有效。",
        "ja": "米国の制空権にもかかわらず、MANPADSは低空飛行機に対する非対称脅威として有効。",
        "fr": "Menace asymétrique : les MANPADS restent efficaces contre les aéronefs à basse altitude malgré la supériorité aérienne US.",
        "de": "Asymmetrische Bedrohung: MANPADS bleiben trotz US-Luftüberlegenheit gegen Tiefflieger wirksam.",
    },
    "Targeted mixed military-civilian infrastructure in northern Israel to maximize pressure.": {
        "es": "Ataque contra infraestructura militar-civil mixta en el norte de Israel para maximizar la presión.",
        "zh": "打击以色列北部军民混合基础设施以最大化施压。",
        "ja": "圧力を最大化するため、イスラエル北部の軍民混合インフラを標的。",
        "fr": "Ciblage d'infrastructures mixtes militaires-civiles dans le nord d'Israël pour maximiser la pression.",
        "de": "Angriff auf gemischte militärisch-zivile Infrastruktur in Nordisrael zur Druckmaximierung.",
    },
    "Collateral damage to civilian and educational infrastructure near military targets.": {
        "es": "Daños colaterales a infraestructura civil y educativa cerca de objetivos militares.",
        "zh": "军事目标附近的民用和教育基础设施遭受附带损害。",
        "ja": "軍事目標近くの民間・教育インフラへの付随的被害。",
        "fr": "Dommages collatéraux aux infrastructures civiles et éducatives proches des cibles militaires.",
        "de": "Kollateralschäden an ziviler und Bildungsinfrastruktur nahe militärischer Ziele.",
    },
    "Persistent attacks on Saudi energy sector to pressure Riyadh and disrupt oil exports.": {
        "es": "Ataques persistentes al sector energético saudí para presionar a Riad y perturbar las exportaciones de petróleo.",
        "zh": "对沙特能源部门的持续攻击，以施压利雅得并扰乱石油出口。",
        "ja": "サウジのエネルギー部門への持続的攻撃でリヤドに圧力をかけ石油輸出を妨害。",
        "fr": "Attaques persistantes contre le secteur énergétique saoudien pour faire pression sur Riyad et perturber les exportations pétrolières.",
        "de": "Anhaltende Angriffe auf saudischen Energiesektor, um Riad unter Druck zu setzen und Ölexporte zu stören.",
    },
    "Targeted key US air operations hub in Kuwait to degrade forward operations.": {
        "es": "Ataque al centro clave de operaciones aéreas de EE.UU. en Kuwait para degradar las operaciones avanzadas.",
        "zh": "打击科威特的美国关键航空作战枢纽以削弱前沿作战能力。",
        "ja": "前方展開作戦を弱体化するため、クウェートの米軍主要航空作戦拠点を攻撃。",
        "fr": "Ciblage du hub clé des opérations aériennes US au Koweït pour dégrader les opérations avancées.",
        "de": "Angriff auf wichtigen US-Luftoperationsstützpunkt in Kuwait zur Schwächung der Vorwärtsoperationen.",
    },
    "Degrading military assets on strategic island while avoiding oil infrastructure escalation.": {
        "es": "Degradación de activos militares en isla estratégica evitando la escalada en infraestructura petrolera.",
        "zh": "在避免石油基础设施升级的同时削弱战略岛屿上的军事资产。",
        "ja": "石油インフラへのエスカレーションを避けつつ、戦略的島嶼の軍事資産を劣化。",
        "fr": "Dégradation des actifs militaires sur une île stratégique tout en évitant l'escalade pétrolière.",
        "de": "Schwächung militärischer Güter auf strategischer Insel unter Vermeidung einer Eskalation bei Ölinfrastruktur.",
    },
    "Disrupting military logistics and weapons transport via rail network.": {
        "es": "Interrupción de la logística militar y el transporte de armas por la red ferroviaria.",
        "zh": "通过打击铁路网络干扰军事后勤和武器运输。",
        "ja": "鉄道網を通じた軍事物流と武器輸送を妨害。",
        "fr": "Perturbation de la logistique militaire et du transport d'armes par le réseau ferroviaire.",
        "de": "Störung der militärischen Logistik und des Waffentransports über das Schienennetz.",
    },
    "Asymmetric attack on diplomatic target in neutral NATO country.": {
        "es": "Ataque asimétrico contra un objetivo diplomático en un país neutral de la OTAN.",
        "zh": "在中立北约国家对外交目标发动的非对称攻击。",
        "ja": "中立NATO国家の外交目標に対する非対称攻撃。",
        "fr": "Attaque asymétrique contre une cible diplomatique dans un pays neutre de l'OTAN.",
        "de": "Asymmetrischer Angriff auf diplomatisches Ziel in neutralem NATO-Land.",
    },
    "Maximum pressure tactic using infrastructure destruction threats.": {
        "es": "Táctica de máxima presión mediante amenazas de destrucción de infraestructura.",
        "zh": "利用基础设施毁灭威胁的极限施压战术。",
        "ja": "インフラ破壊の脅威を用いた最大圧力戦術。",
        "fr": "Tactique de pression maximale par des menaces de destruction d'infrastructures.",
        "de": "Taktik des maximalen Drucks durch Drohung mit Infrastrukturzerstörung.",
    },
    "Targeting aviation assets to deny Iran air mobility and transport capability.": {
        "es": "Ataque a activos de aviación para privar a Irán de movilidad aérea y capacidad de transporte.",
        "zh": "打击航空资产以剥夺伊朗的空中机动和运输能力。",
        "ja": "イランの航空機動力と輸送能力を否定するため航空資産を標的。",
        "fr": "Ciblage des moyens aériens pour priver l'Iran de sa mobilité aérienne et de sa capacité de transport.",
        "de": "Angriff auf Luftfahrtmittel, um Irans Luftmobilität und Transportfähigkeit zu verweigern.",
    },
    "Targeting critical civilian communications infrastructure in Gulf states.": {
        "es": "Ataque a infraestructura civil crítica de comunicaciones en los Estados del Golfo.",
        "zh": "打击海湾国家关键民用通信基础设施。",
        "ja": "湾岸諸国の重要な民間通信インフラを標的。",
        "fr": "Ciblage d'infrastructures civiles de communication critiques dans les États du Golfe.",
        "de": "Angriff auf kritische zivile Kommunikationsinfrastruktur in Golfstaaten.",
    },
    "Iranian threats causing disruption without direct kinetic action.": {
        "es": "Amenazas iraníes causando perturbación sin acción cinética directa.",
        "zh": "伊朗威胁在无直接动能行动的情况下造成干扰。",
        "ja": "直接的な武力行使なしにイランの脅威が混乱を引き起こす。",
        "fr": "Menaces iraniennes provoquant des perturbations sans action cinétique directe.",
        "de": "Iranische Drohungen verursachen Störungen ohne direkte kinetische Aktion.",
    },
    "Escalation to civilian-adjacent critical infrastructure per presidential directive.": {
        "es": "Escalada a infraestructura crítica adyacente a zonas civiles según directiva presidencial.",
        "zh": "根据总统指令，升级至打击民用相邻关键基础设施。",
        "ja": "大統領指令に基づく民間隣接重要インフラへのエスカレーション。",
        "fr": "Escalade vers les infrastructures critiques proches des zones civiles selon directive présidentielle.",
        "de": "Eskalation auf zivilnahe kritische Infrastruktur gemäß Präsidentenanweisung.",
    },
    "Coordinated saturation attack overwhelming tankers defensive measures.": {
        "es": "Ataque de saturación coordinado que superó las medidas defensivas del petrolero.",
        "zh": "协调的饱和攻击突破了油轮的防御措施。",
        "ja": "タンカーの防御措置を圧倒する組織的飽和攻撃。",
        "fr": "Attaque de saturation coordonnée dépassant les mesures défensives du pétrolier.",
        "de": "Koordinierter Sättigungsangriff, der die Abwehrmaßnahmen des Tankers überwältigte.",
    },
    "Surgical decapitation strike against proxy coordination hub in permissive airspace.": {
        "es": "Ataque quirúrgico de decapitación contra centro de coordinación de grupos aliados en espacio aéreo permisivo.",
        "zh": "在可控空域内对代理人协调中心实施精确斩首打击。",
        "ja": "許容的な空域内でのプロキシ調整拠点に対する外科的斬首攻撃。",
        "fr": "Frappe chirurgicale de décapitation contre le centre de coordination des mandataires dans un espace aérien permissif.",
        "de": "Chirurgischer Enthauptungsschlag gegen Stellvertreter-Koordinierungszentrum in permissivem Luftraum.",
    },
    "Hypersonic glide vehicle defeated Israels layered defense demonstrating defense gap.": {
        "es": "El vehículo hipersónico superó la defensa multicapa de Israel, demostrando una brecha defensiva.",
        "zh": "高超音速滑翔体突破了以色列的多层防御，暴露了防御缺口。",
        "ja": "極超音速滑空体がイスラエルの多層防御を突破し、防衛の隙を実証。",
        "fr": "Le planeur hypersonique a percé la défense multicouche d'Israël, révélant une faille défensive.",
        "de": "Hyperschallgleitflugkörper durchbrach Israels Schichtverteidigung und zeigte Verteidigungslücke auf.",
    },
    "Chinese naval deployment signals willingness to tie broader power competition to the conflict.": {
        "es": "El despliegue naval chino señala disposición a vincular la competencia de potencias al conflicto.",
        "zh": "中国海军部署表明愿意将大国竞争与该冲突挂钩。",
        "ja": "中国の海軍展開は、大国間競争を紛争に結びつける意思を示す。",
        "fr": "Le déploiement naval chinois signale la volonté de lier la compétition entre grandes puissances au conflit.",
        "de": "Chinas Marineentsendung signalisiert Bereitschaft, den Großmachtwettbewerb mit dem Konflikt zu verknüpfen.",
    },
    "Asymmetric swarm tactic successfully penetrated layered ship defenses demonstrating CIWS saturation vulnerability.": {
        "es": "La táctica de enjambre asimétrica penetró con éxito las defensas multicapa del buque, demostrando la vulnerabilidad de saturación del CIWS.",
        "zh": "非对称蜂群战术成功突破了舰艇的多层防御，暴露了近防系统饱和脆弱性。",
        "ja": "非対称群集戦術が艦艇の多層防御を突破し、CIWSの飽和脆弱性を実証。",
        "fr": "La tactique d'essaim asymétrique a percé les défenses multicouches du navire, démontrant la vulnérabilité de saturation du CIWS.",
        "de": "Asymmetrische Schwarmtaktik durchbrach die Schichtverteidigung des Schiffs und zeigte die CIWS-Sättigungsverwundbarkeit.",
    },
    "Second successful decapitation strike removing recently-installed leadership.": {
        "es": "Segundo ataque de decapitación exitoso que elimina al liderazgo recién instalado.",
        "zh": "第二次成功的斩首行动，消灭了新近上任的领导层。",
        "ja": "最近就任した指導部を排除する2度目の成功した斩首攻撃。",
        "fr": "Deuxième frappe de décapitation réussie éliminant le leadership récemment installé.",
        "de": "Zweiter erfolgreicher Enthauptungsschlag, der die kürzlich eingesetzte Führung beseitigt.",
    },
    "Political-kinetic pressure forcing US retreat from Iraq an Iranian strategic objective since 2003.": {
        "es": "Presión político-cinética que fuerza la retirada de EE.UU. de Irak, un objetivo estratégico iraní desde 2003.",
        "zh": "迫使美国从伊拉克撤退的政治-动能压力——自2003年以来伊朗的战略目标。",
        "ja": "イラクからの米軍撤退を強いる政治的・軍事的圧力——2003年以来のイランの戦略目標。",
        "fr": "Pression politico-cinétique forçant le retrait américain d'Irak, un objectif stratégique iranien depuis 2003.",
        "de": "Politisch-kinetischer Druck erzwingt US-Rückzug aus dem Irak — ein strategisches Ziel Irans seit 2003.",
    },
    "Omani mediation channel offers face-saving de-escalation path for both sides.": {
        "es": "El canal de mediación omaní ofrece a ambas partes una vía de desescalada que permite salvar las apariencias.",
        "zh": "阿曼斡旋渠道为双方提供保全面子的降级途径。",
        "ja": "オマーンの仲介チャンネルが双方に面子を保つ緊張緩和の道を提供。",
        "fr": "Le canal de médiation omanais offre aux deux parties une voie de désescalade honorable.",
        "de": "Omanischer Vermittlungskanal bietet beiden Seiten einen gesichtswahrenden Deeskalationsweg.",
    },
    "Saturation attack nearly exhausted northern Iron Dome battery magazines.": {
        "es": "El ataque de saturación casi agotó los cargadores de las baterías del Domo de Hierro en el norte.",
        "zh": "饱和攻击几乎耗尽了北部铁穹防御系统的弹药。",
        "ja": "飽和攻撃が北部アイアンドーム砲台の弾薬をほぼ枯渇させた。",
        "fr": "L'attaque de saturation a presque épuisé les réserves des batteries du Dôme de fer au nord.",
        "de": "Sättigungsangriff erschöpfte die Magazine der nördlichen Iron-Dome-Batterien nahezu.",
    },
    "Short pause allows both sides to rearm reconstitute and evaluate ceasefire framework.": {
        "es": "La breve pausa permite a ambas partes rearmarse, reconstituirse y evaluar el marco de alto el fuego.",
        "zh": "短暂停顿使双方得以重新武装、重组并评估停火框架。",
        "ja": "短い停止が双方に再武装、再編成、停戦枠組みの評価を可能にする。",
        "fr": "La courte pause permet aux deux parties de se réarmer, se reconstituer et évaluer le cadre de cessez-le-feu.",
        "de": "Kurze Pause ermöglicht beiden Seiten Wiederbewaffnung, Neuaufstellung und Bewertung des Waffenstillstandsrahmens.",
    },
    "Likely not intentionally aimed at Turkey missile overflew en route to other targets.": {
        "es": "Probablemente no dirigido intencionalmente contra Turquía; el misil sobrevoló en ruta hacia otros objetivos.",
        "zh": "可能并非有意瞄准土耳其；导弹在飞往其他目标途中经过其领空。",
        "ja": "トルコを意図的に狙ったものではない可能性；ミサイルは他の標的への途中で上空を通過。",
        "fr": "Probablement pas dirigé intentionnellement contre la Turquie ; le missile a survolé en route vers d'autres cibles.",
        "de": "Wahrscheinlich nicht absichtlich auf die Türkei gerichtet; Rakete überflog auf dem Weg zu anderen Zielen.",
    },
    "Part of systematic campaign to dismantle Irans nuclear program.": {
        "es": "Parte de una campaña sistemática para desmantelar el programa nuclear de Irán.",
        "zh": "系统性拆除伊朗核计划行动的一部分。",
        "ja": "イラン核計画解体に向けた組織的作戦の一環。",
        "fr": "Partie d'une campagne systématique pour démanteler le programme nucléaire iranien.",
        "de": "Teil einer systematischen Kampagne zur Zerschlagung des iranischen Nuklearprogramms.",
    },
    "Persistent strikes on US bases demonstrate Irans sustained retaliatory capability.": {
        "es": "Los ataques persistentes a bases de EE.UU. demuestran la capacidad de represalia sostenida de Irán.",
        "zh": "对美军基地的持续打击表明伊朗具有持续报复能力。",
        "ja": "米軍基地への持続的攻撃がイランの継続的報復能力を実証。",
        "fr": "Les frappes persistantes sur les bases US démontrent la capacité de représailles soutenue de l'Iran.",
        "de": "Anhaltende Angriffe auf US-Stützpunkte zeigen Irans dauerhafte Vergeltungsfähigkeit.",
    },
    "Critical inflection point potential escalation to targeting civilian power grid.": {
        "es": "Punto de inflexión crítico: posible escalada al ataque contra la red eléctrica civil.",
        "zh": "关键转折点：可能升级至打击民用电力网络。",
        "ja": "民間電力網への標的化への潜在的エスカレーションという重大な転換点。",
        "fr": "Point d'inflexion critique : escalade potentielle vers le ciblage du réseau électrique civil.",
        "de": "Kritischer Wendepunkt: mögliche Eskalation zur Zielbekämpfung des zivilen Stromnetzes.",
    },
    "Systematic degradation of Iranian military logistics and air transport.": {
        "es": "Degradación sistemática de la logística militar y el transporte aéreo iraníes.",
        "zh": "系统性削弱伊朗军事后勤和空中运输。",
        "ja": "イラン軍事物流・航空輸送の体系的弱体化。",
        "fr": "Dégradation systématique de la logistique militaire et du transport aérien iraniens.",
        "de": "Systematische Schwächung der iranischen Militärlogistik und des Lufttransports.",
    },
    # Event 6: Hezbollah missiles into Israel
    "Multiple strikes on northern Israel; Hezbollah drone struck RAF Akrotiri base in Cyprus": {
        "es": "Múltiples ataques al norte de Israel; un dron de Hezbolá alcanzó la base RAF Akrotiri en Chipre",
        "zh": "以色列北部遭多次打击；真主党无人机袭击塞浦路斯RAF阿克罗蒂里基地",
        "ja": "イスラエル北部に複数の攻撃；ヒズボラのドローンがキプロスのRAFアクロティリ基地を攻撃",
        "fr": "Frappes multiples sur le nord d'Israël ; un drone du Hezbollah a frappé la base RAF d'Akrotiri à Chypre",
        "de": "Mehrere Angriffe auf Nordisrael; Hisbollah-Drohne traf RAF-Stützpunkt Akrotiri auf Zypern",
    },
    # Event 9: Mojtaba Khamenei elected
    "No physical damage political succession event amid ongoing war": {
        "es": "Sin daños físicos; evento de sucesión política en medio de la guerra en curso",
        "zh": "无物理损害；战争期间的政治继任事件",
        "ja": "物理的損害なし；戦争継続中の政治的権力継承",
        "fr": "Aucun dommage physique ; succession politique en pleine guerre",
        "de": "Kein physischer Schaden; politisches Nachfolgeereignis während des laufenden Krieges",
    },
    # Event 11: F-15E shot down
    "F-15E shot down; A-10 lost during rescue; 4 Iranian soldiers killed including BG Masoud Zare; both US crew rescued": {
        "es": "F-15E derribado; A-10 perdido durante el rescate; 4 soldados iraníes muertos, incluido el general Masoud Zare; ambos tripulantes estadounidenses rescatados",
        "zh": "F-15E被击落；救援中损失A-10；4名伊朗士兵死亡，包括准将马苏德·扎雷；两名美军机组人员获救",
        "ja": "F-15E撃墜；救出中にA-10喪失；マスード・ザレ准将含むイラン兵4名死亡；米軍搭乗員2名救出",
        "fr": "F-15E abattu ; A-10 perdu lors du sauvetage ; 4 soldats iraniens tués dont le général Masoud Zare ; les deux membres d'équipage US secourus",
        "de": "F-15E abgeschossen; A-10 bei Rettung verloren; 4 iranische Soldaten getötet, darunter BG Masoud Zare; beide US-Besatzungsmitglieder gerettet",
    },
    # Event 12: Iranian missiles hit Haifa
    "4 killed in residential building strike; fires in residential area; multiple impacts across central and northern Israel": {
        "es": "4 muertos por impacto en edificio residencial; incendios en zona residencial; múltiples impactos en el centro y norte de Israel",
        "zh": "住宅楼被击中致4人死亡；居民区发生火灾；以色列中部和北部多处遭到打击",
        "ja": "住宅ビル攻撃で4名死亡；住宅地で火災；イスラエル中部・北部の広範囲に着弾",
        "fr": "4 tués par frappe sur un immeuble résidentiel ; incendies dans une zone résidentielle ; impacts multiples dans le centre et le nord d'Israël",
        "de": "4 Tote durch Treffer auf Wohngebäude; Brände im Wohngebiet; mehrere Einschläge in Zentral- und Nordisrael",
    },
    # Event 13: Sharif University
    "University mosque and fuel station damaged; 6 children killed in nearby residential area": {
        "es": "Mezquita universitaria y gasolinera dañadas; 6 niños muertos en zona residencial cercana",
        "zh": "大学清真寺和加油站受损；附近居民区6名儿童死亡",
        "ja": "大学のモスクとガソリンスタンドが損傷；近隣住宅地で子供6名が死亡",
        "fr": "Mosquée universitaire et station-service endommagées ; 6 enfants tués dans le quartier résidentiel voisin",
        "de": "Universitätsmoschee und Tankstelle beschädigt; 6 Kinder im nahen Wohngebiet getötet",
    },
    # Event 14: Saudi Arabia intercepts
    "18 drones and 7 missiles intercepted; debris fell near energy facilities": {
        "es": "18 drones y 7 misiles interceptados; restos cayeron cerca de instalaciones energéticas",
        "zh": "18架无人机和7枚导弹被拦截；碎片坠落在能源设施附近",
        "ja": "ドローン18機とミサイル7発を迎撃；残骸がエネルギー施設近くに落下",
        "fr": "18 drones et 7 missiles interceptés ; des débris sont tombés près d'installations énergétiques",
        "de": "18 Drohnen und 7 Raketen abgefangen; Trümmer fielen in der Nähe von Energieanlagen",
    },
    # Event 15: Ali Al Salem airbase
    "15 US service members wounded": {
        "es": "15 militares estadounidenses heridos",
        "zh": "15名美军人员受伤",
        "ja": "米軍兵士15名が負傷",
        "fr": "15 militaires américains blessés",
        "de": "15 US-Soldaten verwundet",
    },
    # Event 16: Kharg Island
    "Dozens of military targets destroyed; oil facilities reportedly not hit": {
        "es": "Decenas de objetivos militares destruidos; instalaciones petrolíferas presuntamente no alcanzadas",
        "zh": "数十个军事目标被摧毁；据报石油设施未被打击",
        "ja": "数十の軍事目標を破壊；石油施設は攻撃されなかったと報道",
        "fr": "Des dizaines de cibles militaires détruites ; les installations pétrolières n'auraient pas été touchées",
        "de": "Dutzende militärische Ziele zerstört; Ölanlagen Berichten zufolge nicht getroffen",
    },
    # Event 17: Bridges
    "8 bridges destroyed; ~10 railway segments hit; 2 killed in Kashan bridge strike": {
        "es": "8 puentes destruidos; ~10 tramos ferroviarios alcanzados; 2 muertos en el ataque al puente de Kashán",
        "zh": "8座桥梁被毁；约10段铁路被击中；卡尚桥梁打击中2人死亡",
        "ja": "橋梁8か所破壊；鉄道区間約10か所に命中；カシャーン橋梁攻撃で2名死亡",
        "fr": "8 ponts détruits ; ~10 segments ferroviaires touchés ; 2 tués dans la frappe du pont de Kachan",
        "de": "8 Brücken zerstört; ~10 Eisenbahnabschnitte getroffen; 2 Tote bei Brückenangriff in Kaschan",
    },
    # Event 18: Istanbul consulate
    "2 attackers killed; 2 police officers injured; consulate was unstaffed": {
        "es": "2 atacantes abatidos; 2 policías heridos; el consulado no tenía personal",
        "zh": "2名袭击者被击毙；2名警察受伤；领事馆当时无人值守",
        "ja": "襲撃者2名射殺；警察官2名負傷；領事館は無人だった",
        "fr": "2 assaillants tués ; 2 policiers blessés ; le consulat était inoccupé",
        "de": "2 Angreifer getötet; 2 Polizisten verletzt; Konsulat war unbesetzt",
    },
    # Event 19: Trump threatens
    "No immediate damage deadline/ultimatum; Iran rejects ceasefire proposals": {
        "es": "Sin daño inmediato; plazo/ultimátum; Irán rechaza las propuestas de alto el fuego",
        "zh": "无即时损害；设定最后期限/最后通牒；伊朗拒绝停火提议",
        "ja": "即時的な被害なし；期限/最後通牒；イランが停戦提案を拒否",
        "fr": "Aucun dommage immédiat ; délai/ultimatum ; l'Iran rejette les propositions de cessez-le-feu",
        "de": "Kein unmittelbarer Schaden; Frist/Ultimatum; Iran lehnt Waffenstillstandsvorschläge ab",
    },
    # Event 20: Tehran airports
    "3 airports struck; multiple planes and dozens of helicopters destroyed; synagogue destroyed": {
        "es": "3 aeropuertos atacados; múltiples aviones y decenas de helicópteros destruidos; sinagoga destruida",
        "zh": "3座机场被打击；多架飞机和数十架直升机被摧毁；犹太教堂被毁",
        "ja": "空港3か所を攻撃；複数の航空機と数十機のヘリコプターを破壊；シナゴーグ破壊",
        "fr": "3 aéroports frappés ; de nombreux avions et des dizaines d'hélicoptères détruits ; synagogue détruite",
        "de": "3 Flughäfen angegriffen; zahlreiche Flugzeuge und Dutzende Hubschrauber zerstört; Synagoge zerstört",
    },
    # Event 21: UAE telecom
    "Telecom building hit by drone; 1 injured by shrapnel in Abu Dhabi": {
        "es": "Edificio de telecomunicaciones alcanzado por un dron; 1 herido por metralla en Abu Dabi",
        "zh": "电信大楼被无人机击中；阿布扎比1人被弹片所伤",
        "ja": "ドローンにより通信ビルが被弾；アブダビで1名が破片により負傷",
        "fr": "Bâtiment de télécommunications touché par un drone ; 1 blessé par éclats à Abou Dabi",
        "de": "Telekommunikationsgebäude von Drohne getroffen; 1 Verletzter durch Splitter in Abu Dhabi",
    },
    # Event 22: King Fahd Causeway
    "No physical damage causeway closed indefinitely as precaution": {
        "es": "Sin daños físicos; calzada cerrada indefinidamente como precaución",
        "zh": "无物理损害；大桥因预防措施无限期关闭",
        "ja": "物理的損害なし；予防措置として橋が無期限閉鎖",
        "fr": "Aucun dommage physique ; chaussée fermée indéfiniment par précaution",
        "de": "Kein physischer Schaden; Brücke vorsorglich auf unbestimmte Zeit gesperrt",
    },
    # Event 23: Bandar Abbas power
    "Bandar Abbas power complex destroyed; ~2.5M residents without electricity; strategic port C2 degraded": {
        "es": "Complejo eléctrico de Bandar Abás destruido; ~2,5 millones de residentes sin electricidad; mando del puerto estratégico degradado",
        "zh": "班达尔阿巴斯电力设施被摧毁；约250万居民断电；战略港口指挥控制能力下降",
        "ja": "バンダルアッバース電力施設破壊；約250万人が停電；戦略的港湾の指揮統制能力低下",
        "fr": "Complexe électrique de Bandar Abbas détruit ; ~2,5 millions de résidents sans électricité ; C2 du port stratégique dégradé",
        "de": "Stromkomplex Bandar Abbas zerstört; ~2,5 Mio. Einwohner ohne Strom; Führungsfähigkeit des strategischen Hafens beeinträchtigt",
    },
    # Event 24: MV Olympic Spirit
    "MV Olympic Spirit sunk; 3 crew killed, 17 rescued; Brent crude surges 11% to $142/bbl": {
        "es": "MV Olympic Spirit hundido; 3 tripulantes muertos, 17 rescatados; crudo Brent sube un 11% hasta $142/barril",
        "zh": "MV奥林匹克精神号沉没；3名船员死亡，17人获救；布伦特原油飙升11%至142美元/桶",
        "ja": "MVオリンピック・スピリット号沈没；乗組員3名死亡、17名救助；ブレント原油11%急騰し142ドル/バレル",
        "fr": "MV Olympic Spirit coulé ; 3 membres d'équipage tués, 17 secourus ; le Brent bondit de 11% à 142 $/baril",
        "de": "MV Olympic Spirit versenkt; 3 Besatzungsmitglieder getötet, 17 gerettet; Brent-Rohöl steigt 11% auf 142 $/Barrel",
    },
    # Event 25: Ghaani assassination
    "Quds Force commander Ghaani killed; 5 IRGC officers + 2 Hezbollah liaisons killed": {
        "es": "Comandante de la Fuerza Quds Ghaani muerto; 5 oficiales de la CGRI + 2 enlaces de Hezbolá muertos",
        "zh": "圣城旅指挥官加尼被击毙；5名革命卫队军官和2名真主党联络官死亡",
        "ja": "コッズ部隊司令官ガアニ殺害；IRGC将校5名＋ヒズボラ連絡官2名死亡",
        "fr": "Le commandant de la Force Qods Ghaani tué ; 5 officiers du CGRI + 2 agents de liaison du Hezbollah tués",
        "de": "Quds-Kommandeur Ghaani getötet; 5 IRGC-Offiziere + 2 Hisbollah-Verbindungsleute getötet",
    },
    # Event 26: Fattah-2 Tel Aviv
    "HaKirya command complex struck; 23 IDF killed incl. BG; first confirmed hypersonic target penetration": {
        "es": "Complejo de mando HaKirya alcanzado; 23 soldados de las FDI muertos, incluido un general; primera penetración hipersónica confirmada",
        "zh": "哈基里亚指挥中心被击中；以军23人死亡含准将；首次确认的高超音速突防",
        "ja": "ハキルヤ司令部施設に命中；IDF23名死亡（准将含む）；初の確認された極超音速突破",
        "fr": "Complexe de commandement HaKirya frappé ; 23 soldats de Tsahal tués dont un général ; première pénétration hypersonique confirmée",
        "de": "HaKirya-Kommandokomplex getroffen; 23 IDF-Soldaten getötet inkl. Brigadegeneral; erster bestätigter Hyperschall-Durchbruch",
    },
    # Event 27: UNSC session
    "UNSC ceasefire resolution vetoed by US/UK; China announces naval deployment to Iran": {
        "es": "Resolución de alto el fuego del CSNU vetada por EE.UU./Reino Unido; China anuncia despliegue naval hacia Irán",
        "zh": "联合国安理会停火决议遭美英否决；中国宣布向伊朗方向部署海军",
        "ja": "国連安保理の停戦決議を米英が拒否権行使；中国がイランへの海軍派遣を発表",
        "fr": "Résolution de cessez-le-feu du CSNU bloquée par le veto US/UK ; la Chine annonce un déploiement naval vers l'Iran",
        "de": "UN-Sicherheitsrat-Waffenstillstandsresolution von USA/UK mit Veto belegt; China kündigt Marineentsendung Richtung Iran an",
    },
    # Event 28: USS Thomas Hudner
    "USS Thomas Hudner damaged; 7 sailors killed, 12 wounded; ship transits to Fujairah": {
        "es": "USS Thomas Hudner dañado; 7 marineros muertos, 12 heridos; el buque se dirige a Fujairah",
        "zh": "USS托马斯·哈德纳号受损；7名水兵死亡，12人受伤；军舰转移至富查伊拉",
        "ja": "USSトーマス・ハドナー損傷；水兵7名死亡、12名負傷；艦はフジャイラへ移動",
        "fr": "USS Thomas Hudner endommagé ; 7 marins tués, 12 blessés ; le navire rejoint Fujaïrah",
        "de": "USS Thomas Hudner beschädigt; 7 Matrosen getötet, 12 verwundet; Schiff fährt nach Fudschaira",
    },
    # Event 29: Mojtaba killed
    "Supreme Leader Mojtaba Khamenei killed; ~40 senior clerics/IRGC officers killed; partial damage to Imam Reza shrine": {
        "es": "Líder supremo Mojtaba Jamenei muerto; ~40 clérigos/oficiales de la CGRI muertos; daños parciales al santuario del Imán Reza",
        "zh": "最高领袖穆杰塔巴·哈梅内伊被击毙；约40名高级神职人员/革命卫队军官死亡；伊玛目礼萨圣陵部分受损",
        "ja": "最高指導者モジュタバー・ハメネイ殺害；高位聖職者/IRGC将校約40名死亡；イマーム・レザー廟が部分損傷",
        "fr": "Guide suprême Mojtaba Khamenei tué ; ~40 hauts clercs/officiers du CGRI tués ; dommages partiels au sanctuaire de l'Imam Reza",
        "de": "Oberster Führer Mojtaba Chamenei getötet; ~40 hochrangige Geistliche/IRGC-Offiziere getötet; Teilschäden am Imam-Resa-Schrein",
    },
    # Event 30: US Embassy stormed
    "Embassy compound breached; 14 attackers killed; staff evacuated; Iraqi PM orders US troop withdrawal": {
        "es": "Recinto de la embajada asaltado; 14 atacantes abatidos; personal evacuado; primer ministro iraquí ordena la retirada de tropas de EE.UU.",
        "zh": "大使馆院区被突破；14名袭击者被击毙；工作人员撤离；伊拉克总理下令美军撤离",
        "ja": "大使館敷地が侵入される；襲撃者14名射殺；職員避難；イラク首相が米軍撤退を命令",
        "fr": "Enceinte de l'ambassade percée ; 14 assaillants tués ; personnel évacué ; le PM irakien ordonne le retrait des troupes US",
        "de": "Botschaftsgelände durchbrochen; 14 Angreifer getötet; Personal evakuiert; irakischer PM ordnet US-Truppenabzug an",
    },
    # Event 31: Oman mediation
    "No physical damage; first confirmed direct Iran-US contact since February 28 war start": {
        "es": "Sin daños físicos; primer contacto directo confirmado entre Irán y EE.UU. desde el inicio de la guerra el 28 de febrero",
        "zh": "无物理损害；自2月28日开战以来首次确认的伊美直接接触",
        "ja": "物理的損害なし；2月28日の開戦以来、初の確認されたイラン・米国間の直接接触",
        "fr": "Aucun dommage physique ; premier contact direct confirmé entre l'Iran et les États-Unis depuis le début de la guerre le 28 février",
        "de": "Kein physischer Schaden; erster bestätigter direkter Iran-US-Kontakt seit Kriegsbeginn am 28. Februar",
    },
    # Event 32: Hezbollah largest salvo
    "11 Israeli civilians killed, 68 wounded; 47 Hezbollah operatives killed in retaliatory IDF strikes": {
        "es": "11 civiles israelíes muertos, 68 heridos; 47 milicianos de Hezbolá muertos en ataques de represalia de las FDI",
        "zh": "11名以色列平民死亡、68人受伤；以军报复打击中47名真主党武装人员死亡",
        "ja": "イスラエル民間人11名死亡、68名負傷；IDF報復攻撃でヒズボラ戦闘員47名死亡",
        "fr": "11 civils israéliens tués, 68 blessés ; 47 combattants du Hezbollah tués dans les frappes de représailles de Tsahal",
        "de": "11 israelische Zivilisten getötet, 68 verwundet; 47 Hisbollah-Kämpfer bei IDF-Vergeltungsschlägen getötet",
    },
    # Event 33: Hormuz reopens
    "Hormuz reopens; oil prices fall 8% to $118/bbl; first offensive pause since Feb 28": {
        "es": "Ormuz reabre; precios del petróleo bajan un 8% a $118/barril; primera pausa ofensiva desde el 28 de febrero",
        "zh": "霍尔木兹海峡重新开放；油价下跌8%至118美元/桶；2月28日以来首次攻势暂停",
        "ja": "ホルムズ海峡再開；原油価格8%下落し118ドル/バレル；2月28日以来初の攻撃停止",
        "fr": "Ormuz rouvre ; les prix du pétrole baissent de 8% à 118 $/baril ; première pause offensive depuis le 28 février",
        "de": "Hormus wird wiedereröffnet; Ölpreise fallen 8% auf 118 $/Barrel; erste Angriffspause seit dem 28. Februar",
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
