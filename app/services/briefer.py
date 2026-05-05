"""Daily briefing generator (v12e).

Apple-style light design, consistent with homepage.
Supports 7 languages: KO, EN, ES, ZH, JA, FR, DE.
Language switching is client-side (JS) using data-lang-* attributes.
"""
from __future__ import annotations

import html as html_mod
from collections import Counter
from datetime import datetime, date, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.services.dashboard import classify_damage_severity, get_all_incidents
from app.services.seed_data import get_actor_side
from app.services.ko_translate import (
    translate_actor, translate_means, translate_location,
    translate_sentence, translate_title,
)
from app.services import i18n


def _esc(s: str | None) -> str:
    return html_mod.escape(str(s or "-"))


# ─── UI label translations ───
LABELS = {
    "title": {
        "ko": "일일 OSINT 브리핑 — 2026 이란전쟁",
        "en": "Daily OSINT Briefing — 2026 Iran War",
        "es": "Informe OSINT diario — Guerra de Irán 2026",
        "zh": "每日OSINT简报 — 2026年伊朗战争",
        "ja": "デイリーOSINTブリーフィング — 2026年イラン戦争",
        "fr": "Briefing OSINT quotidien — Guerre d'Iran 2026",
        "de": "Tägliches OSINT-Briefing — Irankrieg 2026",
    },
    "generated": {
        "ko": "생성 시각",
        "en": "Generated",
        "es": "Generado",
        "zh": "生成时间",
        "ja": "生成時刻",
        "fr": "Généré",
        "de": "Erstellt",
    },
    "summary": {
        "ko": "요약",
        "en": "Summary",
        "es": "Resumen",
        "zh": "概要",
        "ja": "概要",
        "fr": "Résumé",
        "de": "Zusammenfassung",
    },
    "war_day": {
        "ko": "전쟁",
        "en": "War Day",
        "es": "Día de guerra",
        "zh": "战争第",
        "ja": "戦争",
        "fr": "Jour de guerre",
        "de": "Kriegstag",
    },
    "war_day_suffix": {
        "ko": "일차",
        "en": "",
        "es": "",
        "zh": "天",
        "ja": "日目",
        "fr": "",
        "de": "",
    },
    "total_incidents": {
        "ko": "전체 사건",
        "en": "Total incidents",
        "es": "Incidentes totales",
        "zh": "事件总数",
        "ja": "全事件数",
        "fr": "Total incidents",
        "de": "Gesamtvorfälle",
    },
    "iran_attacks": {
        "ko": "이란/대리세력 공격",
        "en": "Iran/proxy attacks",
        "es": "Ataques Irán/aliados",
        "zh": "伊朗/代理人攻击",
        "ja": "イラン/代理勢力攻撃",
        "fr": "Attaques Iran/mandataires",
        "de": "Iran/Stellvertreter-Angriffe",
    },
    "us_attacks": {
        "ko": "미국/이스라엘 타격",
        "en": "US/Israel strikes",
        "es": "Ataques EE.UU./Israel",
        "zh": "美国/以色列打击",
        "ja": "米国/イスラエル攻撃",
        "fr": "Frappes USA/Israël",
        "de": "US/Israel-Angriffe",
    },
    "top_actors": {
        "ko": "주요 행위자",
        "en": "Top actors",
        "es": "Actores principales",
        "zh": "主要行为者",
        "ja": "主要行為者",
        "fr": "Acteurs principaux",
        "de": "Hauptakteure",
    },
    "top_means": {
        "ko": "주요 공격수단",
        "en": "Top means",
        "es": "Medios principales",
        "zh": "主要攻击手段",
        "ja": "主要攻撃手段",
        "fr": "Principaux moyens",
        "de": "Hauptangriffsmittel",
    },
    "top_locations": {
        "ko": "주요 위치",
        "en": "Top locations",
        "es": "Ubicaciones principales",
        "zh": "主要地点",
        "ja": "主要地点",
        "fr": "Lieux principaux",
        "de": "Hauptstandorte",
    },
    "incidents_detail": {
        "ko": "사건 상세",
        "en": "Incident details",
        "es": "Detalles de incidentes",
        "zh": "事件详情",
        "ja": "事件詳細",
        "fr": "Détails des incidents",
        "de": "Vorfalldetails",
    },
    "date": {
        "ko": "일시",
        "en": "Date",
        "es": "Fecha",
        "zh": "日期",
        "ja": "日時",
        "fr": "Date",
        "de": "Datum",
    },
    "location": {
        "ko": "위치",
        "en": "Location",
        "es": "Ubicación",
        "zh": "地点",
        "ja": "場所",
        "fr": "Lieu",
        "de": "Standort",
    },
    "confidence": {
        "ko": "신뢰도",
        "en": "Confidence",
        "es": "Confianza",
        "zh": "置信度",
        "ja": "信頼度",
        "fr": "Confiance",
        "de": "Konfidenz",
    },
    "status": {
        "ko": "상태",
        "en": "Status",
        "es": "Estado",
        "zh": "状态",
        "ja": "状態",
        "fr": "Statut",
        "de": "Status",
    },
    "means": {
        "ko": "수단",
        "en": "Means",
        "es": "Medio",
        "zh": "手段",
        "ja": "手段",
        "fr": "Moyen",
        "de": "Mittel",
    },
    "severity": {
        "ko": "심각도",
        "en": "Severity",
        "es": "Gravedad",
        "zh": "严重程度",
        "ja": "深刻度",
        "fr": "Gravité",
        "de": "Schweregrad",
    },
    "damage": {
        "ko": "피해",
        "en": "Damage",
        "es": "Daños",
        "zh": "损害",
        "ja": "被害",
        "fr": "Dégâts",
        "de": "Schaden",
    },
    "tactical": {
        "ko": "전술 평가",
        "en": "Tactical assessment",
        "es": "Evaluación táctica",
        "zh": "战术评估",
        "ja": "戦術評価",
        "fr": "Évaluation tactique",
        "de": "Taktische Bewertung",
    },
    "strategic": {
        "ko": "전략 평가",
        "en": "Strategic assessment",
        "es": "Evaluación estratégica",
        "zh": "战略评估",
        "ja": "戦略評価",
        "fr": "Évaluation stratégique",
        "de": "Strategische Bewertung",
    },
    "source": {
        "ko": "출처",
        "en": "Source",
        "es": "Fuente",
        "zh": "来源",
        "ja": "出典",
        "fr": "Source",
        "de": "Quelle",
    },
    "back": {
        "ko": "← 대시보드로 돌아가기",
        "en": "← Back to dashboard",
        "es": "← Volver al panel",
        "zh": "← 返回仪表板",
        "ja": "← ダッシュボードに戻る",
        "fr": "← Retour au tableau de bord",
        "de": "← Zurück zum Dashboard",
    },
    "language": {
        "ko": "언어",
        "en": "Language",
        "es": "Idioma",
        "zh": "语言",
        "ja": "言語",
        "fr": "Langue",
        "de": "Sprache",
    },
    "font_size": {
        "ko": "글자 크기",
        "en": "Font size",
        "es": "Tamaño de letra",
        "zh": "字体大小",
        "ja": "文字サイズ",
        "fr": "Taille du texte",
        "de": "Schriftgröße",
    },
    "fs_small": {
        "ko": "작게",
        "en": "Small",
        "es": "Pequeño",
        "zh": "小",
        "ja": "小",
        "fr": "Petit",
        "de": "Klein",
    },
    "fs_normal": {
        "ko": "보통",
        "en": "Normal",
        "es": "Normal",
        "zh": "标准",
        "ja": "標準",
        "fr": "Normal",
        "de": "Normal",
    },
    "fs_large": {
        "ko": "크게",
        "en": "Large",
        "es": "Grande",
        "zh": "大",
        "ja": "大",
        "fr": "Grand",
        "de": "Groß",
    },
    "fs_xlarge": {
        "ko": "아주 크게",
        "en": "Extra large",
        "es": "Muy grande",
        "zh": "超大",
        "ja": "特大",
        "fr": "Très grand",
        "de": "Sehr groß",
    },
}

LANG_NAMES = {
    "ko": "🇰🇷 한국어",
    "en": "🇬🇧 English",
    "es": "🇪🇸 Español",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
}

ALL_LANGS = list(LANG_NAMES.keys())


def _lbl(key: str) -> str:
    """Generate span set for all languages from LABELS[key]."""
    parts = []
    for lang in ALL_LANGS:
        text = _esc(LABELS.get(key, {}).get(lang, key))
        display = "" if lang == "en" else "none"
        parts.append(f'<span class="ml" data-lang="{lang}" style="display:{display}">{text}</span>')
    return "".join(parts)


def _ml_from_en(en_text: str | None, ko_override: str | None = None) -> str:
    """영어 원문 → 7개 언어 span 세트.
    ko_override 가 주어지면 한국어 셀에 그대로 사용 (사전 기반 정확 번역이 있는 경우),
    없으면 i18n.translate(en, "ko") 로 사전+MT 폴백을 거친다.
    한국어 외 5개 언어는 항상 i18n.translate(en, lang) 로 Google MT.
    EN 셀은 원문 그대로.
    """
    en_raw = str(en_text or "-")
    en_safe = _esc(en_raw)

    # KO
    if ko_override is not None:
        ko_safe = _esc(ko_override)
    else:
        ko_safe = _esc(i18n.translate(en_raw, "ko"))

    parts = [f'<span class="ml" data-lang="ko" style="display:none">{ko_safe}</span>']
    parts.append(f'<span class="ml" data-lang="en" style="">{en_safe}</span>')
    for lang in ("es", "zh", "ja", "fr", "de"):
        translated = i18n.translate(en_raw, lang)
        parts.append(
            f'<span class="ml" data-lang="{lang}" style="display:none">{_esc(translated)}</span>'
        )
    return "".join(parts)


def _ml_pair_from_en(en_left: str | None, en_right: str | None,
                     ko_left: str | None = None, ko_right: str | None = None,
                     sep: str = " → ") -> str:
    """`A → B` 형태(주체 → 대상)를 7개 언어로 묶어서 출력."""
    en_l = str(en_left or "-")
    en_r = str(en_right or "-")
    ko_l = ko_left if ko_left is not None else i18n.translate(en_l, "ko")
    ko_r = ko_right if ko_right is not None else i18n.translate(en_r, "ko")

    parts = [
        f'<span class="ml" data-lang="ko" style="display:none">{_esc(ko_l)}{_esc(sep)}{_esc(ko_r)}</span>',
        f'<span class="ml" data-lang="en" style="">{_esc(en_l)}{_esc(sep)}{_esc(en_r)}</span>',
    ]
    for lang in ("es", "zh", "ja", "fr", "de"):
        l = i18n.translate(en_l, lang)
        r = i18n.translate(en_r, lang)
        parts.append(
            f'<span class="ml" data-lang="{lang}" style="display:none">'
            f'{_esc(l)}{_esc(sep)}{_esc(r)}</span>'
        )
    return "".join(parts)


class BriefingService:
    def __init__(self, db: Session):
        self.db = db

    def build_daily_html(self, days: int = 90, output_path: str = "app/static/daily_brief.html") -> str:
        incident_pairs = get_all_incidents(self.db)
        incidents = [inc for inc, _ in incident_pairs]

        # Stats — 영문 Counter 를 만든 뒤 i18n 으로 언어별 묶음을 산출
        actor_en = Counter([i.actor for i in incidents if i.actor])
        means_en = Counter([i.means for i in incidents if i.means])
        loc_en = Counter([i.location_name for i in incidents if i.location_name])

        def _localize_counter(counter: Counter, ko_translator, lang: str) -> Counter:
            """한국어는 사전 기반 함수(ko_translator), 그 외는 i18n.translate."""
            out: Counter = Counter()
            for raw, n in counter.items():
                if not raw:
                    continue
                if lang == "ko":
                    label = ko_translator(raw)
                elif lang == "en":
                    label = raw
                else:
                    label = i18n.translate(raw, lang)
                out[label] += n
            return out

        actor_by_lang = {l: _localize_counter(actor_en, translate_actor, l) for l in ALL_LANGS}
        means_by_lang = {l: _localize_counter(means_en, translate_means, l) for l in ALL_LANGS}
        loc_by_lang = {l: _localize_counter(loc_en, translate_location, l) for l in ALL_LANGS}

        iran_attacks = sum(1 for i in incidents if get_actor_side(i.actor or "") == "iran")
        us_attacks = sum(1 for i in incidents if get_actor_side(i.actor or "") == "us_israel")

        # War day
        WAR_START = date(2026, 2, 28)
        today = date.today()
        war_day = (today - WAR_START).days + 1
        gen_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        def _top5(counter: Counter) -> str:
            return ", ".join(f"{k} ({v})" for k, v in counter.most_common(5))

        # Language selector options
        lang_opts = "".join(
            f'<option value="{l}"{"selected" if l == "en" else ""}>{n}</option>'
            for l, n in LANG_NAMES.items()
        )

        # Font size selector options (작게/보통/크게/아주크게)
        # value 는 CSS --fs 값과 직접 매핑됨
        fs_options = [
            ("0.85", "fs_small"),
            ("1",    "fs_normal"),
            ("1.18", "fs_large"),
            ("1.4",  "fs_xlarge"),
        ]
        fs_opts = "".join(
            f'<option value="{val}"{" selected" if val == "1" else ""}>'
            + "".join(
                f'<span data-lang="{lng}">{LABELS[key][lng]}</span>'
                for lng in ALL_LANGS
            ) + '</option>'
            for val, key in fs_options
        )
        # <option> 안의 <span> 은 브라우저가 무시하므로, 실제 텍스트로 한 번 더 표기.
        # 가장 짧은 영문 라벨로 대체한 단순 옵션을 다시 만든다.
        fs_opts = "".join(
            f'<option value="{val}"{" selected" if val == "1" else ""} '
            f'data-fs-key="{key}">{LABELS[key]["en"]}</option>'
            for val, key in fs_options
        )

        # Build incident cards
        cards_html = ""
        for inc, doc in incident_pairs[:30]:
            side = get_actor_side(inc.actor or "")
            side_css = "iran" if side == "iran" else ("us" if side == "us_israel" else "other")
            dot = "🔴" if side == "iran" else ("🔵" if side == "us_israel" else "🟡")
            pub_date = ""
            if doc and doc.published_at:
                pub_date = doc.published_at.strftime("%Y-%m-%d %H:%M UTC")

            # 한국어는 기존 사전(사람/조직/장소/수단) 우선, 그 외 언어는 i18n로 MT.
            actor_en = inc.actor or "-"
            target_en = inc.target_actor or "-"
            loc_en = inc.location_name or "-"
            means_en = inc.means or "-"
            damage_en = inc.damage_summary or "-"
            tact_en = inc.tactical_assessment or "-"
            strat_en = inc.strategic_assessment or "-"
            title_en = doc.title if doc else "-"
            pub_en = doc.publisher if doc else "-"

            actor_ko_dict = translate_actor(inc.actor)
            target_ko_dict = translate_actor(inc.target_actor)
            loc_ko_dict = translate_location(inc.location_name)
            means_ko_dict = translate_means(inc.means)
            # 긴 문장은 사전이 영어를 많이 남길 수 있어 i18n.translate(., "ko") 가 필요
            # (i18n 내부에서 사전→MT 폴백을 자동 결정)
            damage_ko = i18n.translate(damage_en, "ko")
            tact_ko = i18n.translate(tact_en, "ko")
            strat_ko = i18n.translate(strat_en, "ko")
            title_ko = i18n.translate(title_en, "ko")

            sev = classify_damage_severity(inc.damage_summary)
            url = _esc(doc.url if doc else "#")
            pub_safe = _esc(pub_en)

            cards_html += f"""
            <div class="inc-card {side_css}">
                <div class="inc-title">{dot} {_ml_pair_from_en(actor_en, target_en, ko_left=actor_ko_dict, ko_right=target_ko_dict)}</div>
                <div class="inc-meta">
                    {_lbl('date')}: {_esc(pub_date)} &nbsp;|&nbsp;
                    {_lbl('location')}: {_ml_from_en(loc_en, ko_override=loc_ko_dict)} &nbsp;|&nbsp;
                    {_lbl('means')}: {_ml_from_en(means_en, ko_override=means_ko_dict)} &nbsp;|&nbsp;
                    {_lbl('severity')}: {_esc(sev)} &nbsp;|&nbsp;
                    {_lbl('confidence')}: {inc.confidence:.2f} &nbsp;|&nbsp;
                    {_lbl('status')}: {_esc(inc.verified_status)}
                </div>
                <div class="inc-field"><span class="inc-label">{_lbl('damage')}:</span> {_ml_from_en(damage_en, ko_override=damage_ko)}</div>
                <div class="inc-field"><span class="inc-label">{_lbl('tactical')}:</span> {_ml_from_en(tact_en, ko_override=tact_ko)}</div>
                <div class="inc-field"><span class="inc-label">{_lbl('strategic')}:</span> {_ml_from_en(strat_en, ko_override=strat_ko)}</div>
                <div class="inc-source">
                    {_lbl('source')}: <a href="{url}" target="_blank" rel="noopener">{pub_safe}: {_ml_from_en(title_en, ko_override=title_ko)}</a>
                </div>
            </div>
            """

        # Full HTML
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>일일 OSINT 브리핑 — 2026 이란전쟁</title>
<style>
:root {{
    --bg: #f5f5f7;
    --surface: #ffffff;
    --surface-2: #fbfbfd;
    --border: rgba(0,0,0,0.08);
    --border-strong: rgba(0,0,0,0.14);
    --text: #1d1d1f;
    --text-soft: #424245;
    --text-muted: #6e6e73;
    --text-dim: #86868b;
    --accent: #0071e3;
    --accent-soft: rgba(0,113,227,0.08);
    --danger: #ff3b30;
    --danger-soft: rgba(255,59,48,0.08);
    --warning: #ff9500;
    --warning-soft: rgba(255,149,0,0.1);
    --success: #30d158;
    --success-soft: rgba(48,209,88,0.12);
    --radius: 14px;
    --shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.04);
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans CJK SC", "Noto Sans CJK JP", sans-serif;
    /* 폰트 스케일 — JS 로 0.85/1/1.18/1.4 사이 전환 */
    --fs: 1;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: var(--font);
    background: var(--bg); color: var(--text);
    line-height: 1.6; font-size: calc(14px * var(--fs));
    -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 960px; margin: 0 auto; padding: 28px 32px; }}
/* Header */
.brief-header {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 24px 28px; margin-bottom: 20px;
    box-shadow: var(--shadow);
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 14px;
}}
.brief-header h1 {{
    font-size: calc(20px * var(--fs)); font-weight: 700; letter-spacing: -0.01em;
    display: flex; align-items: center; gap: 10px;
    color: var(--text);
}}
.brief-header h1 .dot {{
    width: 10px; height: 10px; border-radius: 50%;
    background: linear-gradient(135deg, var(--danger), var(--warning));
}}
.brief-controls {{
    display: flex; align-items: center; gap: 10px;
}}
.lang-select, .fs-select {{
    font-family: var(--font);
    font-size: calc(13px * var(--fs)); font-weight: 500;
    background: var(--surface-2); color: var(--text);
    border: 1px solid var(--border); border-radius: 999px;
    padding: 7px 14px; cursor: pointer;
    appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2386868b' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
    padding-right: 30px;
}}
.back-link {{
    font-size: calc(13px * var(--fs)); font-weight: 500; color: var(--accent);
    text-decoration: none; padding: 7px 14px; border-radius: 999px;
    border: 1px solid rgba(0,113,227,0.15); background: var(--accent-soft);
    transition: all 0.15s;
}}
.back-link:hover {{ background: var(--accent); color: white; }}
.gen-time {{
    font-size: calc(12px * var(--fs)); color: var(--text-dim); margin-top: 6px;
}}
/* War Day */
.war-day-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    font-size: calc(16px * var(--fs)); font-weight: 700;
    background: linear-gradient(135deg, var(--danger) 0%, var(--warning) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
/* Summary */
.summary-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px 24px; margin-bottom: 20px;
    box-shadow: var(--shadow);
}}
.summary-card h2 {{
    font-size: calc(15px * var(--fs)); font-weight: 600; color: var(--text);
    margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
}}
.summary-grid {{
    display: grid; grid-template-columns: repeat(3,1fr); gap: 12px;
    margin-bottom: 14px;
}}
.sum-tile {{
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 14px; text-align: center;
}}
.sum-tile .sv {{ font-size: calc(24px * var(--fs)); font-weight: 700; }}
.sum-tile .sl {{ font-size: calc(11px * var(--fs)); color: var(--text-muted); margin-top: 2px; }}
.sum-tile.iran .sv {{ color: var(--danger); }}
.sum-tile.us .sv {{ color: var(--accent); }}
.sum-tile.total .sv {{ color: var(--text); }}
.sum-list {{
    font-size: calc(12.5px * var(--fs)); color: var(--text-soft); line-height: 1.7;
}}
.sum-list-label {{
    font-weight: 600; color: var(--text-muted); font-size: calc(11px * var(--fs));
    text-transform: uppercase; letter-spacing: 0.03em;
    margin-top: 10px; margin-bottom: 3px;
}}
/* Section title */
.section-title {{
    font-size: calc(13px * var(--fs)); font-weight: 600; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.03em;
    margin: 0 0 14px 2px;
}}
/* Incident card */
.inc-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 18px 22px; margin-bottom: 14px;
    border-left: 4px solid var(--border-strong);
    box-shadow: var(--shadow);
    transition: transform 0.12s ease;
}}
.inc-card:hover {{ transform: translateY(-1px); }}
.inc-card.iran {{ border-left-color: var(--danger); }}
.inc-card.us {{ border-left-color: var(--accent); }}
.inc-card.other {{ border-left-color: var(--warning); }}
.inc-title {{
    font-size: calc(15px * var(--fs)); font-weight: 600; margin-bottom: 6px;
}}
.inc-card.iran .inc-title {{ color: var(--danger); }}
.inc-card.us .inc-title {{ color: var(--accent); }}
.inc-card.other .inc-title {{ color: #b86900; }}
.inc-meta {{
    font-size: calc(11.5px * var(--fs)); color: var(--text-muted); margin-bottom: 10px;
    line-height: 1.6;
}}
.inc-field {{
    font-size: calc(13px * var(--fs)); color: var(--text-soft); margin-bottom: 5px;
    line-height: 1.55;
}}
.inc-label {{ font-weight: 600; color: var(--text); }}
.inc-source {{
    font-size: calc(11.5px * var(--fs)); color: var(--text-dim); margin-top: 10px;
    padding-top: 8px; border-top: 1px solid var(--border);
}}
.inc-source a {{ color: var(--accent); text-decoration: none; }}
.inc-source a:hover {{ text-decoration: underline; }}
@media (max-width: 768px) {{
    .wrap {{ padding: 16px; }}
    .summary-grid {{ grid-template-columns: 1fr; }}
    .brief-header {{ flex-direction: column; align-items: flex-start; }}
}}
</style>
</head>
<body>
<div class="wrap">
    <div class="brief-header">
        <div>
            <h1>
                <span class="dot"></span>
                {_lbl('title')}
            </h1>
            <div class="gen-time">{_lbl('generated')}: {gen_time}</div>
        </div>
        <div class="brief-controls">
            <select class="lang-select" id="langSelect" aria-label="Language">
                {lang_opts}
            </select>
            <select class="fs-select" id="fsSelect" aria-label="Font size" title="{LABELS['font_size']['en']}">
                {fs_opts}
            </select>
            <a class="back-link" href="/">{_lbl('back')}</a>
        </div>
    </div>

    <div class="summary-card">
        <h2>📊 {_lbl('summary')}</h2>
        <div class="war-day-badge">D+{war_day} &nbsp;—&nbsp; {_lbl('war_day')} {war_day}{_lbl('war_day_suffix')}</div>
        <div class="summary-grid" style="margin-top:14px;">
            <div class="sum-tile total">
                <div class="sv">{len(incidents)}</div>
                <div class="sl">{_lbl('total_incidents')}</div>
            </div>
            <div class="sum-tile iran">
                <div class="sv">{iran_attacks}</div>
                <div class="sl">{_lbl('iran_attacks')}</div>
            </div>
            <div class="sum-tile us">
                <div class="sv">{us_attacks}</div>
                <div class="sl">{_lbl('us_attacks')}</div>
            </div>
        </div>
        <div class="sum-list">
            <div class="sum-list-label">{_lbl('top_actors')}</div>
            <div>
                {"".join(
                    f'<span class="ml" data-lang="{l}" style="display:{"" if l == "en" else "none"}">{_esc(_top5(actor_by_lang[l]))}</span>'
                    for l in ALL_LANGS
                )}
            </div>
            <div class="sum-list-label">{_lbl('top_means')}</div>
            <div>
                {"".join(
                    f'<span class="ml" data-lang="{l}" style="display:{"" if l == "en" else "none"}">{_esc(_top5(means_by_lang[l]))}</span>'
                    for l in ALL_LANGS
                )}
            </div>
            <div class="sum-list-label">{_lbl('top_locations')}</div>
            <div>
                {"".join(
                    f'<span class="ml" data-lang="{l}" style="display:{"" if l == "en" else "none"}">{_esc(_top5(loc_by_lang[l]))}</span>'
                    for l in ALL_LANGS
                )}
            </div>
        </div>
    </div>

    <div class="section-title">{_lbl('incidents_detail')}</div>
    {cards_html}
</div>

<script>
(function() {{
    // 폰트 사이즈 라벨 — 언어별 텍스트를 옵션에 매핑
    const FS_LABELS = {{
        "fs_small":  {{"ko":"작게","en":"Small","es":"Pequeño","zh":"小","ja":"小","fr":"Petit","de":"Klein"}},
        "fs_normal": {{"ko":"보통","en":"Normal","es":"Normal","zh":"标准","ja":"標準","fr":"Normal","de":"Normal"}},
        "fs_large":  {{"ko":"크게","en":"Large","es":"Grande","zh":"大","ja":"大","fr":"Grand","de":"Groß"}},
        "fs_xlarge": {{"ko":"아주 크게","en":"Extra large","es":"Muy grande","zh":"超大","ja":"特大","fr":"Très grand","de":"Sehr groß"}}
    }};
    function applyLang(lang) {{
        document.querySelectorAll('.ml').forEach(el => {{
            el.style.display = el.dataset.lang === lang ? '' : 'none';
        }});
        // 폰트 크기 옵션 라벨 다국어 갱신
        document.querySelectorAll('#fsSelect option').forEach(opt => {{
            const k = opt.dataset.fsKey;
            if (k && FS_LABELS[k] && FS_LABELS[k][lang]) {{
                opt.textContent = FS_LABELS[k][lang];
            }}
        }});
        try {{ localStorage.setItem('osintLang', lang); }} catch (e) {{}}
    }}
    function applyFs(scale) {{
        document.documentElement.style.setProperty('--fs', String(scale));
        try {{ localStorage.setItem('osintFs', String(scale)); }} catch (e) {{}}
    }}

    const langSel = document.getElementById('langSelect');
    const fsSel = document.getElementById('fsSelect');

    // localStorage 복원
    try {{
        const savedLang = localStorage.getItem('osintLang');
        if (savedLang) {{
            langSel.value = savedLang;
        }}
        const savedFs = localStorage.getItem('osintFs');
        if (savedFs) {{
            fsSel.value = savedFs;
        }}
    }} catch (e) {{}}

    // 초기 적용
    applyLang(langSel.value);
    applyFs(fsSel.value);

    langSel.addEventListener('change', function() {{ applyLang(this.value); }});
    fsSel.addEventListener('change',  function() {{ applyFs(this.value); }});
}})();
</script>
</body>
</html>"""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        # 번역 캐시 영구 저장 (이번 빌드에서 새로 추가된 항목)
        try:
            i18n.save_cache()
        except Exception:
            pass
        return str(path)
