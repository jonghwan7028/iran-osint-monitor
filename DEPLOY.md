# 🚀 Render 배포 가이드 (실시간 공개 웹사이트로 올리기)

이 가이드는 현재 코드를 **Render** 에 올려서 **1시간마다 자동 수집되는 공개 모니터링 사이트**로 만드는 전체 절차입니다.

> **v14-noGPT**: OpenAI 의존성을 제거한 버전입니다. 규칙 기반 키워드 매칭으로 사건을 추출하므로 외부 API 비용이 없습니다.

## 개요: 무엇이 자동화되는가?

배포가 끝나면 다음이 자동으로 돌아갑니다:

1. 웹사이트가 `https://iran-osint-web.onrender.com` 같은 주소로 공개됨
2. 매시 정각(UTC)마다 Google News + GDELT 에서 뉴스를 자동 수집
3. 수집된 기사를 규칙 기반 엔진으로 분석해 사건(incident)으로 추출
4. 지도·브리핑이 자동 갱신되어 방문자에게 표시
5. ▶ 수집/분석 버튼은 공개 UI 에서 숨겨짐 (관리자 cron 만 호출 가능)

---

## 준비물 (체크리스트)

- [ ] GitHub 계정
- [ ] Render 계정 (GitHub 로 로그인 가능) — https://render.com
- [ ] (선택) 본인 도메인 (예: `osint.mydomain.kr`)

Render 무료 티어로 시작 가능, 15분 idle 시 슬립 → 필요시 Starter ($7/mo) 로 업그레이드.

---

## 1단계 — GitHub 에 코드 올리기

현재 `iran_us_osint_mvp_v14_nogpt` 폴더 전체를 GitHub 저장소로 만듭니다.

```bash
cd iran_us_osint_mvp_v14_nogpt
git init
git add .
git commit -m "Initial commit - v14-noGPT"
gh repo create iran-osint-monitor --public --source=. --push
# 또는 수동으로:
# 1. https://github.com/new 에서 "iran-osint-monitor" 생성
# 2. git remote add origin https://github.com/<본인>/iran-osint-monitor.git
# 3. git branch -M main
# 4. git push -u origin main
```

## 2단계 — Render 에 Blueprint 로 배포

1. https://render.com 에 GitHub 로 로그인
2. Dashboard → **New +** → **Blueprint**
3. 방금 만든 `iran-osint-monitor` 저장소 선택
4. Render 가 `render.yaml` 을 읽어서 자동으로 4개 서비스를 제안:
   - `iran-osint-db` (Postgres, 무료)
   - `iran-osint-web` (FastAPI 웹 서비스, 무료)
   - `iran-osint-hourly-ingest` (1시간마다 cron)
   - `iran-osint-daily-refresh` (매일 1회 cron)
5. **Apply** 를 누르면 빌드 시작

## 3단계 — 비밀 환경변수 주입 (Render 대시보드에서)

`render.yaml` 의 `sync: false` 로 표시된 항목은 git 에 올라가지 않으므로 대시보드에서 수동 입력이 필요합니다.

**iran-osint-web** 서비스 → **Environment** 탭:

| Key | Value | 비고 |
|---|---|---|
| `ADMIN_TOKEN` | 임의 랜덤 문자열 | `openssl rand -hex 32` 결과 복사/붙여넣기 |

**iran-osint-hourly-ingest** 및 **iran-osint-daily-refresh** cron 에도:

| Key | Value |
|---|---|
| `ADMIN_TOKEN` | 웹 서비스에 넣은 것과 **정확히 동일한 값** |

> 💡 `ADMIN_TOKEN` 을 세 군데 모두 같은 값으로 설정하지 않으면 cron 이 401 Unauthorized 로 실패합니다.

## 4단계 — 첫 배포 확인

1. Render 대시보드에서 `iran-osint-web` 의 로그를 보고 `Application startup complete` 확인
2. 서비스 URL (예: `https://iran-osint-web.onrender.com`) 을 브라우저에서 열기
3. 확인:
   - [x] 지도에 검증 이벤트 마커가 표시됨 (시드 데이터)
   - [x] ▶ 수집/분석, ★ 검증 데이터 로드 버튼이 **보이지 않음** (PUBLIC_MODE=1)
   - [x] "🔒 자동 업데이트 모드 · 1시간마다 갱신" 문구 표시

## 5단계 — Cron 수동 테스트

첫 cron 이 돌기를 기다리지 말고 직접 트리거해봅니다:

```bash
curl -X POST https://iran-osint-web.onrender.com/pipeline/run \
     -H "X-Admin-Token: <ADMIN_TOKEN 값>"
```

성공 시 JSON 으로 `ingested: N, incidents_extracted: M` 같은 응답이 옵니다.
토큰이 틀리면 `{"detail":"관리자 토큰이 필요합니다"}` 401 이 옵니다.

## 6단계 (선택) — 본인 도메인 연결

- Render 웹 서비스 → **Settings** → **Custom Domains** → `osint.mydomain.kr` 추가
- 도메인 등록업체 DNS 에 `CNAME` 레코드 추가 (Render 가 알려주는 값 사용)
- 인증서는 Render 가 Let's Encrypt 로 자동 발급

---

## 로컬 개발과 프로덕션 차이 요약

| 설정 | 로컬 (개발) | 프로덕션 (Render) |
|---|---|---|
| `DATABASE_URL` | 없음 → SQLite (`app/data/osint.db`) | Postgres 자동 주입 |
| `PUBLIC_MODE` | 없음 → `0` (버튼 노출) | `1` (버튼 숨김) |
| `ADMIN_TOKEN` | 없음 → 인증 생략 | 필수 (cron 호출 시) |
| 수집 트리거 | ▶ 버튼 클릭 | cron 1시간마다 자동 |

로컬에서 프로덕션 시뮬레이션하려면:
```bash
export PUBLIC_MODE=1
export ADMIN_TOKEN=testtoken123
uvicorn app.main:app --reload
```

---

## 비용 요약

| 항목 | 무료 티어 | 유료 전환 시 |
|---|---|---|
| Web 서비스 | $0 (15분 idle 시 슬립) | $7/월 (상시 가동) |
| PostgreSQL | $0 (90일 한정, 1GB) | $7/월 (starter) |
| Cron 2개 | 무료 포함 | 포함 |
| OpenAI API | **불필요 (제거됨)** | — |
| **월 총액** | **$0** | **$14/월** |

## 문제 해결

| 증상 | 원인 / 해결 |
|---|---|
| 웹 첫 요청이 30초 걸림 | 무료 티어 cold start. Starter 플랜으로 업그레이드하거나 UptimeRobot 으로 5분마다 ping. |
| cron 이 매시 호출되지만 데이터가 안 늘어남 | RSS 피드 응답 지연 또는 중복 기사 — 로그에서 `ingested: 0` 확인. |
| "sqlite3.OperationalError: no such table" | DB 초기화 전에 쿼리. 앱 재시작하면 `Base.metadata.create_all()` 이 다시 돌아 해결. |
| 지도 마커가 빈 화면 | 시드 데이터가 아직 안 들어감 → `/pipeline/seed` 수동 호출 (admin token 필요). |
