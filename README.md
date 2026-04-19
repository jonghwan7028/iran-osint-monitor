# Iran-US War OSINT Monitor

Real-time OSINT dashboard tracking the 2026 Iran War (started Feb 28).

**Live Demo:** [https://iran-osint-web.onrender.com](https://iran-osint-web.onrender.com)

---

## Features

- **Interactive Incident Map** — Leaflet-based map with actor-color-coded markers (Iran/red, US-Israel/blue, Other/yellow), date filtering (1d/3d/7d/14d/1mo/all), and bilingual popups
- **War Timeline** — Chronological event feed with summary/detail toggle, top-incident star badges, and relative timestamps (KST/UTC)
- **Casualty Tracker (KIA Panel)** — Military/civilian casualty estimates by side with source evidence popover
- **Incident Comparison** — Select 2–3 incidents to compare side-by-side (actor, means, damage, confidence)
- **Map ↔ List Linking** — Hover on a table row to highlight the map marker; click a marker to scroll to the row
- **Multilingual UI** — Korean/English toggle across all content (map legend, date filter, timeline, stats)
- **Fact vs. Analysis Labels** — Each item is tagged as Fact, Claim, Analysis, or Strategic Assessment
- **5-Level Verification** — Confirmed → Partially Verified → Unverified → Disputed → Denied
- **Source Attribution** — Publisher type badges, direct links to original articles
- **Methodology Page** — Transparent documentation of collection & analysis methods
- **Pipeline Dashboard** — Compact status view: documents collected, incidents detected, verified, mapped
- **Feedback System** — Built-in user feedback form
- **Auto Pipeline** — Hourly RSS/API ingestion + daily coordinate backfill via Render Cron
- **One-click Deploy** — Render Blueprint (render.yaml) auto-provisions Web + Postgres + Cron jobs

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy + Jinja2
- **Database:** PostgreSQL (Render managed) / SQLite (local)
- **Map:** Self-contained Leaflet (no folium dependency at runtime)
- **Deploy:** Docker on Render (free tier supported)

## Quick Start

```bash
pip install -r requirements.txt
python run_app.py
```

Open http://localhost:8000 and click **"Seed verified data"**.

## Deploy to Render

1. Push this repo to GitHub
2. Render Dashboard → New → Blueprint → select this repo
3. Set environment variables: `ADMIN_TOKEN`, `WEB_URL`
4. Render auto-creates: Web Service + PostgreSQL + 2 Cron Jobs

See `DEPLOY.md` for detailed instructions.

## Map Legend

- 🔴 Red square = Iran / proxy forces (IRGC, Hezbollah, Houthis)
- 🔵 Blue circle = US / Israel strikes
- 🟡 Yellow circle = Other events (diplomatic, political)

## Requirements

- Python 3.10+
- See `requirements.txt`

## License

For academic and research purposes.

---

# 이란-미국 전쟁 OSINT 모니터

2026 이란전쟁(2월 28일 개전) 실시간 OSINT 대시보드.

**라이브 데모:** [https://iran-osint-web.onrender.com](https://iran-osint-web.onrender.com)

---

## 주요 기능

- **사건 지도** — Leaflet 기반 인터랙티브 지도. 행위자별 색상 마커(이란/빨강, 미-이스라엘/파랑, 기타/노랑), 날짜 필터링(1일/3일/7일/14일/1개월/전체), 이중언어 팝업
- **전쟁 타임라인** — 시간순 이벤트 피드. 요약형/상세형 전환, 핵심 사건 별표 표시, 상대시간(KST/UTC)
- **인명피해 현황(KIA 패널)** — 진영별 군사/민간 사상자 추정치와 근거 출처 팝오버
- **사건 비교 기능** — 2~3개 사건을 선택하여 나란히 비교(행위자, 수단, 피해, 신뢰도)
- **지도↔목록 연동** — 테이블 행에 마우스를 올리면 지도 마커가 강조, 마커 클릭 시 해당 행으로 이동
- **다국어 UI** — 한국어/영어 전체 전환(지도 범례, 날짜 필터, 타임라인, 통계)
- **사실·분석 구분 표시** — 각 항목에 사실(Fact), 주장(Claim), 분석(Analysis), 전략평가(Strategic) 라벨 부여
- **5단계 검증 체계** — 확인됨 → 부분 확인 → 미확인 → 논쟁 중 → 부인됨
- **출처 강화 표시** — 매체 유형 배지, 원문 기사 직접 링크
- **방법론 페이지** — 수집·분석 방법에 대한 투명한 문서화
- **파이프라인 상태** — 수집 문서, 탐지 사건, 검증 완료, 지도 표시 현황을 한눈에 표시
- **피드백 시스템** — 사용자 의견 제출 폼 내장
- **자동 파이프라인** — Render Cron을 통해 매시간 RSS/API 수집 + 매일 좌표 보정
- **원클릭 배포** — Render Blueprint(render.yaml)로 웹 + PostgreSQL + Cron 자동 구성

## 기술 스택

- **백엔드:** FastAPI + SQLAlchemy + Jinja2
- **데이터베이스:** PostgreSQL (Render 관리형) / SQLite (로컬)
- **지도:** 자체 Leaflet 템플릿 (런타임 folium 의존 없음)
- **배포:** Docker on Render (무료 티어 지원)

## 빠른 시작

```bash
pip install -r requirements.txt
python run_app.py
```

http://localhost:8000 접속 후 **"검증 데이터 로드"** 클릭.

## Render 배포

1. 이 저장소를 GitHub에 push
2. Render 대시보드 → New → Blueprint → 저장소 선택
3. 환경변수 설정: `ADMIN_TOKEN`, `WEB_URL`
4. Render가 자동 생성: 웹 서비스 + PostgreSQL + Cron 2개

자세한 내용은 `DEPLOY.md`를 참조하세요.

## 지도 범례

- 🔴 빨간 사각형 = 이란/대리세력 공격 (IRGC, 헤즈볼라, 후티 반군)
- 🔵 파란 원 = 미국/이스라엘 타격
- 🟡 노란 원 = 기타 이벤트 (외교, 정치)

## 요구사항

- Python 3.10+
- `requirements.txt` 참조

## 라이선스

학술 및 연구 목적.
