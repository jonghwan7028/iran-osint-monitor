"""
Map renderer (v12e) — self-contained Leaflet map.

설계 요지:
- folium 대신 직접 Leaflet HTML 템플릿을 문자열로 생성해 ‘마커가 안 뜨는’
  오래된 문제를 근본적으로 제거한다. (folium 버전업/문법 변화에 영향받지 않음)
- 이벤트 데이터는 JSON으로 임베드하고 JS에서 circleMarker/Rectangle로 그린다.
- 팝업은 한국어가 기본, 내부 버튼으로 영어 원문을 토글할 수 있다.
- 마커에 마우스를 올리면 한국어 요약(툴팁)이 뜬다.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.entities import Incident, SourceDocument
from app.services.extractor import IncidentExtractor
from app.services.utils import infer_location_from_text, choose_fallback_location
from app.services.seed_data import get_actor_side
from app.services.ko_translate import build_bilingual_incident, translate_location


MAP_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<title>사건 지도 — 2026 이란전쟁 OSINT</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<style>
html, body { margin:0; padding:0; height:100%; background:#f5f5f7; color:#1d1d1f;
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Apple SD Gothic Neo','Malgun Gothic',sans-serif; }
#map { position:absolute; top:0; bottom:0; left:0; right:0; background:#f5f5f7; }
.legend {
  position:absolute; bottom:20px; left:20px; z-index:500;
  background:rgba(255,255,255,0.95); padding:12px 16px; border-radius:12px;
  border:1px solid rgba(0,0,0,0.08); font-size:12px; box-shadow:0 4px 16px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.05); color:#1d1d1f;
}
.legend h4 { margin:0 0 8px; font-size:13px; }
.legend .row { display:flex; align-items:center; margin-bottom:5px; gap:8px; }
.legend .sq { width:16px; height:16px; border:2px solid #ff3b30; background:rgba(255,59,48,0.18); border-radius:3px; }
.legend .c-blue { width:14px; height:14px; border-radius:50%; background:#0071e3; }
.legend .c-yel  { width:14px; height:14px; border-radius:50%; background:#ff9500; }
.lang-toggle {
  position:absolute; top:14px; right:14px; z-index:600;
  background:rgba(255,255,255,0.95); border:1px solid rgba(0,0,0,0.08); color:#1d1d1f;
  padding:7px 14px; border-radius:999px; box-shadow:0 1px 3px rgba(0,0,0,0.06); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); cursor:pointer; font-size:12px; font-weight:600;
}
.lang-toggle:hover { background:#ffffff; }
.empty {
  position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
  background:rgba(255,255,255,0.97); border:1px solid rgba(0,0,0,0.1); color:#1d1d1f;
  padding:18px 24px; border-radius:10px; font-size:14px; z-index:500;
}
.leaflet-popup-content-wrapper {
  background:#ffffff; color:#1d1d1f; border:1px solid rgba(0,0,0,0.08); border-radius:14px;
  max-width:620px !important;
}
.leaflet-popup-tip { background:#ffffff; }
.leaflet-popup-content {
  margin:10px 14px; font-size:11.5px; line-height:1.55;
  width:560px !important; max-width:560px !important;
}
.popup-side { font-weight:700; font-size:12.5px; margin-bottom:6px; }
.popup-title { font-weight:700; color:#1d1d1f; margin-bottom:4px; font-size:12px; }
.popup-row { margin-bottom:3px; color:#424245; font-size:11.5px; }
.popup-row .lbl { color:#86868b; display:inline-block; min-width:62px; font-weight:600; }
.popup-sep { border:none; border-top:1px solid rgba(0,0,0,0.08); margin:7px 0; }
.popup-assess { color:#424245; }
.popup-link { color:#0071e3; text-decoration:none; }
.popup-link:hover { text-decoration:underline; }
.popup-meta { font-size:10.5px; color:#86868b; margin-top:5px; }
.popup-switch {
  display:inline-block; background:#f7f0ff; color:#6c3fc7; border:1px solid rgba(108,63,199,0.2);
  padding:3px 10px; border-radius:14px; font-size:10.5px; cursor:pointer;
  margin-top:7px; user-select:none;
}
.popup-switch:hover { background:#efe2ff; }
.leaflet-tooltip.ko-tip {
  background:rgba(255,255,255,0.97); color:#1d1d1f; border:1px solid #0071e3; border-radius:10px;
  padding:8px 12px; font-size:10.5px; white-space:normal;
  max-width:460px; min-width:320px; line-height:1.5;
  box-shadow:0 8px 20px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.06);
}
.leaflet-tooltip.ko-tip b { color:#b86900; font-size:11px; }
.leaflet-tooltip.ko-tip .meta { color:#86868b; font-size:10px; margin-top:4px; }
.leaflet-tooltip.ko-tip.iran { border-color:#ff3b30; }
.leaflet-tooltip.ko-tip.other { border-color:#ff9500; }
</style>
</head>
<body>
<div id="map"></div>
<button class="lang-toggle" id="langToggle" title="클릭 시 기본 언어를 전환합니다">🇰🇷 한국어 / English</button>
<div class="legend">
  <h4>범 례</h4>
  <div class="row"><span class="sq"></span><span>이란/대리세력 공격</span></div>
  <div class="row"><span class="c-blue"></span><span>미국/이스라엘 타격</span></div>
  <div class="row"><span class="c-yel"></span><span>기타 (외교·정치)</span></div>
</div>
__EMPTY_BANNER__
<script>
const INCIDENTS = __INCIDENTS_JSON__;
let DEFAULT_LANG = 'ko';  // 클릭으로 전체 전환

const map = L.map('map', {
  center: [28.0, 49.0],
  zoom: 5,
  worldCopyJump: true,
  zoomControl: true,
  preferCanvas: false
});

L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap &copy; CARTO',
  subdomains: 'abcd',
  maxZoom: 19
}).addTo(map);

function escapeHtml(s) {
  if (s === null || s === undefined) return '-';
  return String(s).replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}

function renderPopupHTML(inc, lang) {
  const d = inc[lang];
  const sideLabel = lang === 'ko' ? inc.side_label_ko : inc.side_label_en;
  const sideColor =
    inc.actor_side === 'iran' ? '#ff4444' :
    inc.actor_side === 'us_israel' ? '#4488ff' : '#ffaa22';
  const labels = lang === 'ko'
    ? {target:'대상', loc:'위치', when:'일시', means:'수단', tgtType:'대상유형',
       damage:'피해', tact:'전술평가', strat:'전략평가', conf:'신뢰도', status:'상태',
       switchBtn:'🌐 English'}
    : {target:'Target', loc:'Location', when:'When', means:'Means', tgtType:'Target type',
       damage:'Damage', tact:'Tactical', strat:'Strategic', conf:'Confidence', status:'Status',
       switchBtn:'🌐 한국어'};
  const wrapBtnId = 'sw_' + inc.id + '_' + lang;
  return `
    <div style="max-width:420px;">
      <div class="popup-side" style="color:${sideColor}">${sideLabel}</div>
      <div class="popup-title">${escapeHtml(d.actor)} → ${escapeHtml(d.target_actor)}</div>
      <div class="popup-row"><span class="lbl">${labels.loc}</span> ${escapeHtml(d.location_name)}</div>
      <div class="popup-row"><span class="lbl">${labels.when}</span> ${escapeHtml(inc.pub_date || '-')}</div>
      <div class="popup-row"><span class="lbl">${labels.means}</span> ${escapeHtml(d.means)}</div>
      <div class="popup-row"><span class="lbl">${labels.tgtType}</span> ${escapeHtml(d.target_type)}</div>
      <hr class="popup-sep"/>
      <div class="popup-row"><span class="lbl">${labels.damage}</span> ${escapeHtml(d.damage_summary)}</div>
      <div class="popup-row"><span class="lbl">${labels.tact}</span> <span class="popup-assess">${escapeHtml(d.tactical_assessment)}</span></div>
      <div class="popup-row"><span class="lbl">${labels.strat}</span> <span class="popup-assess">${escapeHtml(d.strategic_assessment)}</span></div>
      <hr class="popup-sep"/>
      <div class="popup-meta">
        ${labels.conf}: ${inc.confidence.toFixed(2)} &nbsp;|&nbsp;
        ${labels.status}: ${escapeHtml(d.verified_status)}
      </div>
      <div class="popup-meta">
        <a class="popup-link" href="${escapeHtml(d.url)}" target="_blank" rel="noopener">
          ${escapeHtml(d.publisher)}: ${escapeHtml((d.title || '').slice(0, 80))}${(d.title || '').length > 80 ? '…' : ''}
        </a>
      </div>
      <span class="popup-switch" id="${wrapBtnId}" data-inc="${inc.id}">${labels.switchBtn}</span>
    </div>
  `;
}

function shortSummaryKo(inc) {
  return `${inc.ko.actor} → ${inc.ko.target_actor}\\n📍 ${inc.ko.location_name}\\n🗓 ${inc.pub_date || '-'}\\n${inc.ko.damage_summary.slice(0, 90)}${inc.ko.damage_summary.length > 90 ? '…' : ''}`;
}

function shortSummaryEn(inc) {
  return `${inc.en.actor} → ${inc.en.target_actor}\\n📍 ${inc.en.location_name}\\n🗓 ${inc.pub_date || '-'}\\n${inc.en.damage_summary.slice(0, 90)}${inc.en.damage_summary.length > 90 ? '…' : ''}`;
}

const markersById = new Map();

function bindPopup(layer, inc) {
  const popup = L.popup({ maxWidth: 620, minWidth: 560, autoPan: true, className: 'osint-popup' });
  const open = (lang) => {
    popup.setContent(renderPopupHTML(inc, lang));
    layer.bindPopup(popup).openPopup();
    // 토글 버튼 연결
    setTimeout(() => {
      const btn = document.getElementById('sw_' + inc.id + '_' + lang);
      if (btn) btn.onclick = (e) => {
        e.stopPropagation();
        const next = lang === 'ko' ? 'en' : 'ko';
        open(next);
      };
    }, 0);
  };
  layer.on('click', () => open(DEFAULT_LANG));

  // Hover 툴팁: 한국어 요약을 기본으로 (필요 정보를 최대한 담되 글자는 작게)
  const tipClass = 'ko-tip ' + (inc.actor_side || '');
  const buildTip = () => {
    const d = DEFAULT_LANG === 'ko' ? inc.ko : inc.en;
    const lbl = DEFAULT_LANG === 'ko'
      ? {loc:'위치', when:'일시', means:'수단', tgt:'대상유형', damage:'피해', click:'클릭 시 상세 보기'}
      : {loc:'Location', when:'When', means:'Means', tgt:'Target type', damage:'Damage', click:'Click for details'};
    const sideLabel = DEFAULT_LANG === 'ko' ? inc.side_label_ko : inc.side_label_en;
    const damageText = (d.damage_summary || '-');
    const damageTrunc = damageText.length > 220 ? damageText.slice(0, 220) + '…' : damageText;
    return `
      <div style="font-weight:600; margin-bottom:4px;">${escapeHtml(sideLabel)}</div>
      <b>${escapeHtml(d.actor)}</b> → ${escapeHtml(d.target_actor)}<br>
      📍 <span>${escapeHtml(d.location_name)}</span>&nbsp;&nbsp;
      🗓 <span>${escapeHtml(inc.pub_date || '-')}</span><br>
      <span style="color:#86868b;">${lbl.means}:</span> ${escapeHtml(d.means)}<br>
      <span style="color:#86868b;">${lbl.tgt}:</span> ${escapeHtml(d.target_type)}<br>
      <span style="color:#86868b;">${lbl.damage}:</span> ${escapeHtml(damageTrunc)}
      <div class="meta">▸ ${escapeHtml(lbl.click)}</div>
    `;
  };
  layer.bindTooltip(buildTip(), {
    className: tipClass,
    sticky: true,
    direction: 'auto',
    opacity: 0.97,
    offset: [8, 0]
  });
  layer._refreshTooltip = () => layer.setTooltipContent(buildTip());
  markersById.set(inc.id, layer);
}

const bounds = [];
INCIDENTS.forEach(inc => {
  if (inc.latitude === null || inc.longitude === null ||
      typeof inc.latitude !== 'number' || typeof inc.longitude !== 'number') {
    return;
  }
  const lat = inc.latitude, lon = inc.longitude;
  bounds.push([lat, lon]);

  if (inc.actor_side === 'iran') {
    const rect = L.rectangle(
      [[lat - 0.4, lon - 0.4], [lat + 0.4, lon + 0.4]],
      { color: '#ff3b30', weight: 2.5, fill: true, fillColor: '#ff3b30', fillOpacity: 0.15 }
    ).addTo(map);
    bindPopup(rect, inc);
    const dot = L.circleMarker([lat, lon], {
      radius: 6, color: '#ff3b30', weight: 2,
      fill: true, fillColor: '#ff3b30', fillOpacity: 0.9
    }).addTo(map);
    bindPopup(dot, inc);
  } else {
    const color = inc.actor_side === 'us_israel' ? '#0071e3' : '#ff9500';
    const cm = L.circleMarker([lat, lon], {
      radius: 9, color: color, weight: 2,
      fill: true, fillColor: color, fillOpacity: 0.7
    }).addTo(map);
    bindPopup(cm, inc);
  }
});

if (bounds.length > 0) {
  map.fitBounds(bounds, { padding: [40, 40], maxZoom: 7 });
} else {
  map.setView([28.0, 49.0], 4);
}

document.getElementById('langToggle').addEventListener('click', () => {
  DEFAULT_LANG = DEFAULT_LANG === 'ko' ? 'en' : 'ko';
  const btn = document.getElementById('langToggle');
  btn.textContent = DEFAULT_LANG === 'ko' ? '🇰🇷 한국어 / English' : '🇬🇧 English / 한국어';
  // 열려있는 팝업을 현재 기본 언어로 재렌더링
  markersById.forEach((layer, id) => {
    if (layer._refreshTooltip) layer._refreshTooltip();
    if (layer.isPopupOpen && layer.isPopupOpen()) {
      const inc = INCIDENTS.find(i => i.id === id);
      if (inc) {
        layer.getPopup().setContent(renderPopupHTML(inc, DEFAULT_LANG));
        layer.openPopup();
      }
    }
  });
});
</script>
</body>
</html>
"""


class MapService:
    def __init__(self, db: Session):
        self.db = db

    def _backfill_missing_coordinates(self) -> int:
        try:
            updated = IncidentExtractor(self.db).backfill_missing_locations()
        except Exception:
            updated = 0
        incidents = self.db.query(Incident).filter(
            (Incident.latitude.is_(None)) | (Incident.longitude.is_(None))
        ).all()
        for inc in incidents:
            doc = self.db.query(SourceDocument).filter(SourceDocument.id == inc.document_id).first()
            text = " ".join(filter(None, [inc.location_name, doc.title if doc else None, doc.raw_text if doc else None]))
            name, lat, lon = infer_location_from_text(text)
            if lat is not None and lon is not None:
                inc.location_name = inc.location_name or name
                inc.latitude = lat
                inc.longitude = lon
                updated += 1
        self.db.commit()
        return updated

    def _collect_events(self) -> list[dict]:
        """DB의 모든 사건을 좌표 보정 후 KO/EN 이중 구조로 직렬화."""
        from app.services.dashboard import get_all_incidents
        pairs = get_all_incidents(self.db)
        events: list[dict] = []
        for inc, doc in pairs:
            lat, lon = inc.latitude, inc.longitude
            loc_name = inc.location_name
            if lat is None or lon is None:
                fb_name, fb_lat, fb_lon = choose_fallback_location(
                    inc.location_name or "",
                    doc.title if doc else "",
                    doc.raw_text if doc else "",
                )
                lat = fb_lat
                lon = fb_lon
                loc_name = loc_name or fb_name
                # 임시 보정: 원본 엔티티는 건드리지 않고 팝업용 값만 채움
                if loc_name:
                    inc.location_name = loc_name  # ko_translate가 사용하도록
            if lat is None or lon is None:
                # 중동 중심 좌표로 최종 폴백
                lat, lon = 29.5, 47.5
                inc.location_name = inc.location_name or "Middle East"

            actor_side = get_actor_side(inc.actor or "")
            payload = build_bilingual_incident(inc, doc, actor_side)
            payload["latitude"] = lat
            payload["longitude"] = lon
            events.append(payload)
        return events

    def build_map(self, days: int = 90, output_path: str = "app/static/incidents_map.html") -> str:
        self._backfill_missing_coordinates()
        events = self._collect_events()

        empty_banner = ""
        if not events:
            empty_banner = (
                '<div class="empty">'
                '🔎 아직 수집된 사건이 없습니다. 대시보드에서 '
                '<b>‘검증 데이터 로드’</b> 버튼을 눌러주세요.<br>'
                '<span style="font-size:11px;color:#8a90a6;">No incidents yet. '
                'Click the <b>Seed verified data</b> button.</span>'
                '</div>'
            )

        html = (MAP_TEMPLATE
                .replace("__INCIDENTS_JSON__", json.dumps(events, ensure_ascii=False))
                .replace("__EMPTY_BANNER__", empty_banner))

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return str(path)
