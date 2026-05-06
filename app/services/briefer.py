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
from app.services.multilingual import (
    translate_actor_ml, translate_means_ml, translate_location_ml,
    translate_sentence_ml, translate_status_ml, translate_severity_ml,
)


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


class BriefingService:
    def __init__(self, db: Session):
        self.db = db

    def build_daily_html(self, days: int = 90, output_path: str = "app/static/daily_brief.html") -> str:
        incident_pairs = get_all_incidents(self.db)
        incidents = [inc for inc, _ in incident_pairs]

        # Stats — 7개 언어별 카운터 생성
        actor_counters: dict[str, Counter] = {}
        means_counters: dict[str, Counter] = {}
        loc_counters: dict[str, Counter] = {}
        for lang in ALL_LANGS:
            if lang == "en":
                actor_counters[lang] = Counter([i.actor for i in incidents if i.actor])
                means_counters[lang] = Counter([i.means for i in incidents if i.means])
                loc_counters[lang] = Counter([i.location_name for i in incidents if i.location_name])
            elif lang == "ko":
                actor_counters[lang] = Counter([translate_actor(i.actor) for i in incidents if i.actor])
                means_counters[lang] = Counter([translate_means(i.means) for i in incidents if i.means])
                loc_counters[lang] = Counter([translate_location(i.location_name) for i in incidents if i.location_name])
            else:
                actor_counters[lang] = Counter([translate_actor_ml(i.actor, lang) for i in incidents if i.actor])
                means_counters[lang] = Counter([translate_means_ml(i.means, lang) for i in incidents if i.means])
                loc_counters[lang] = Counter([translate_location_ml(i.location_name, lang) for i in incidents if i.location_name])

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

        # Build incident cards — 각 언어별 5W1H 기반 문맥 번역
        cards_html = ""
        for inc, doc in incident_pairs[:30]:
            side = get_actor_side(inc.actor or "")
            side_css = "iran" if side == "iran" else ("us" if side == "us_israel" else "other")
            dot = "🔴" if side == "iran" else ("🔵" if side == "us_israel" else "🟡")
            pub_date = ""
            if doc and doc.published_at:
                pub_date = doc.published_at.strftime("%Y-%m-%d %H:%M UTC")

            sev_raw = classify_damage_severity(inc.damage_summary)
            url = _esc(doc.url if doc else "#")
            pub = _esc(doc.publisher if doc else "-")

            def _ml_field(en_text: str | None, field_type: str) -> str:
                """각 언어별로 올바른 번역을 생성하여 span 세트를 만든다.
                field_type: actor, means, location, sentence, status, severity
                """
                en_val = en_text or "-"
                spans = []
                for lang in ALL_LANGS:
                    display = "" if lang == "en" else "none"
                    if lang == "en":
                        translated = _esc(en_val)
                    elif lang == "ko":
                        if field_type == "actor":
                            translated = _esc(translate_actor(en_text))
                        elif field_type == "means":
                            translated = _esc(translate_means(en_text))
                        elif field_type == "location":
                            translated = _esc(translate_location(en_text))
                        elif field_type == "status":
                            translated = _esc(translate_sentence(en_text) if en_text else "-")
                        else:
                            translated = _esc(translate_sentence(en_text))
                    else:
                        if field_type == "actor":
                            translated = _esc(translate_actor_ml(en_text, lang))
                        elif field_type == "means":
                            translated = _esc(translate_means_ml(en_text, lang))
                        elif field_type == "location":
                            translated = _esc(translate_location_ml(en_text, lang))
                        elif field_type == "status":
                            translated = _esc(translate_status_ml(en_text, lang))
                        elif field_type == "severity":
                            translated = _esc(translate_severity_ml(en_text, lang))
                        else:  # sentence (damage, tactical, strategic)
                            translated = _esc(translate_sentence_ml(en_text, lang))
                    spans.append(f'<span class="ml" data-lang="{lang}" style="display:{display}">{translated}</span>')
                return "".join(spans)

            def _ml_actor_arrow(actor: str | None, target: str | None) -> str:
                """행위자 → 대상 형태의 다국어 표현."""
                spans = []
                for lang in ALL_LANGS:
                    display = "" if lang == "en" else "none"
                    if lang == "en":
                        t = _esc(f"{actor or 'Unknown'} → {target or '-'}")
                    elif lang == "ko":
                        t = _esc(f"{translate_actor(actor)} → {translate_actor(target)}")
                    else:
                        t = _esc(f"{translate_actor_ml(actor, lang)} → {translate_actor_ml(target, lang)}")
                    spans.append(f'<span class="ml" data-lang="{lang}" style="display:{display}">{t}</span>')
                return "".join(spans)

            # 심각도 다국어
            sev_ml = _ml_field(sev_raw, "severity")
            # 상태 다국어
            status_ml = _ml_field(inc.verified_status, "status")

            cards_html += f"""
            <div class="inc-card {side_css}">
                <div class="inc-title">{dot} {_ml_actor_arrow(inc.actor, inc.target_actor)}</div>
                <div class="inc-meta">
                    {_lbl('date')}: {_esc(pub_date)} &nbsp;|&nbsp;
                    {_lbl('location')}: {_ml_field(inc.location_name, "location")} &nbsp;|&nbsp;
                    {_lbl('means')}: {_ml_field(inc.means, "means")} &nbsp;|&nbsp;
                    {_lbl('severity')}: {sev_ml} &nbsp;|&nbsp;
                    {_lbl('confidence')}: {inc.confidence:.2f} &nbsp;|&nbsp;
                    {_lbl('status')}: {status_ml}
                </div>
                <div class="inc-field"><span class="inc-label">{_lbl('damage')}:</span> {_ml_field(inc.damage_summary, "sentence")}</div>
                <div class="inc-field"><span class="inc-label">{_lbl('tactical')}:</span> {_ml_field(inc.tactical_assessment, "sentence")}</div>
                <div class="inc-field"><span class="inc-label">{_lbl('strategic')}:</span> {_ml_field(inc.strategic_assessment, "sentence")}</div>
                <div class="inc-source">
                    {_lbl('source')}: <a href="{url}" target="_blank" rel="noopener">{pub}</a>
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
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: var(--font);
    background: var(--bg); color: var(--text);
    line-height: 1.6; font-size: 14px;
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
    font-size: 20px; font-weight: 700; letter-spacing: -0.01em;
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
.lang-select {{
    font-family: var(--font);
    font-size: 13px; font-weight: 500;
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
    font-size: 13px; font-weight: 500; color: var(--accent);
    text-decoration: none; padding: 7px 14px; border-radius: 999px;
    border: 1px solid rgba(0,113,227,0.15); background: var(--accent-soft);
    transition: all 0.15s;
}}
.back-link:hover {{ background: var(--accent); color: white; }}
.gen-time {{
    font-size: 12px; color: var(--text-dim); margin-top: 6px;
}}
/* War Day */
.war-day-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 16px; font-weight: 700;
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
    font-size: 15px; font-weight: 600; color: var(--text);
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
.sum-tile .sv {{ font-size: 24px; font-weight: 700; }}
.sum-tile .sl {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; }}
.sum-tile.iran .sv {{ color: var(--danger); }}
.sum-tile.us .sv {{ color: var(--accent); }}
.sum-tile.total .sv {{ color: var(--text); }}
.sum-list {{
    font-size: 12.5px; color: var(--text-soft); line-height: 1.7;
}}
.sum-list-label {{
    font-weight: 600; color: var(--text-muted); font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.03em;
    margin-top: 10px; margin-bottom: 3px;
}}
/* Section title */
.section-title {{
    font-size: 13px; font-weight: 600; color: var(--text-muted);
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
    font-size: 15px; font-weight: 600; margin-bottom: 6px;
}}
.inc-card.iran .inc-title {{ color: var(--danger); }}
.inc-card.us .inc-title {{ color: var(--accent); }}
.inc-card.other .inc-title {{ color: #b86900; }}
.inc-meta {{
    font-size: 11.5px; color: var(--text-muted); margin-bottom: 10px;
    line-height: 1.6;
}}
.inc-field {{
    font-size: 13px; color: var(--text-soft); margin-bottom: 5px;
    line-height: 1.55;
}}
.inc-label {{ font-weight: 600; color: var(--text); }}
.inc-source {{
    font-size: 11.5px; color: var(--text-dim); margin-top: 10px;
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
                {"".join(f'<span class="ml" data-lang="{l}" style="display:{"" if l == "en" else "none"}">{_top5(actor_counters[l])}</span>' for l in ALL_LANGS)}
            </div>
            <div class="sum-list-label">{_lbl('top_means')}</div>
            <div>
                {"".join(f'<span class="ml" data-lang="{l}" style="display:{"" if l == "en" else "none"}">{_top5(means_counters[l])}</span>' for l in ALL_LANGS)}
            </div>
            <div class="sum-list-label">{_lbl('top_locations')}</div>
            <div>
                {"".join(f'<span class="ml" data-lang="{l}" style="display:{"" if l == "en" else "none"}">{_top5(loc_counters[l])}</span>' for l in ALL_LANGS)}
            </div>
        </div>
    </div>

    <div class="section-title">{_lbl('incidents_detail')}</div>
    {cards_html}
</div>

<script>
document.getElementById('langSelect').addEventListener('change', function() {{
    const lang = this.value;
    document.querySelectorAll('.ml').forEach(el => {{
        el.style.display = el.dataset.lang === lang ? '' : 'none';
    }});
}});
</script>
</body>
</html>"""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return str(path)
