# Iran-US War OSINT Monitor — v20k

2026년 이란-미국 전쟁(2/28 개전) 실시간 OSINT 대시보드.

## v20k 변경사항 (v20j 대비)

### 1. 4월 25일 검증 사건 4건 박제 (시드 33 → 37건)

이전 v20j는 33건의 시드 데이터를 갖고 있었습니다. v20k는 4월 25일 추가된 14건의 자동 수집·분석 결과 중 **검증 가능한 4건**을 선별·정제하여 시드로 박제했습니다.

자동 추출된 14건은 actor/location 오인, 기사 본문 잔재 등 품질 문제가 있어 그대로 사용하기 어려웠습니다. 따라서 다음 4건만 다중 출처 검증을 거쳐 추가했습니다:

| ID | 일시 | 사건 | 출처 |
|----|------|------|------|
| 34 | 4/25 14:00 UTC | 이스라엘, 남부 레바논 공습 — 6명 사망 17명 부상 | Al Jazeera / AFP / Times of Israel |
| 35 | 4/25 19:00 UTC | 트럼프, 위트코프·쿠슈너 파키스탄 사절 방문 취소 | CNN / Reuters / NPR / Bloomberg |
| 36 | 4/25 20:30 UTC | 이란 외무장관 아락치, 이슬라마바드 → 무스카트 이동 | NPR / CNN |
| 37 | 4/25 22:00 UTC | 미해군, 제재 대상 유조선 M/V 세반호 차단 (누적 37척) | CNN / US CENTCOM |

각 사건의 한국어 번역(damage_summary / tactical / strategic) 9문장이 `ko_sentences.SENTENCE_KO`에 등록되어 자연스럽게 표시됩니다.

### 2. 사이트가 시드 데이터로 영구화되는 이유

Render 무료 플랜은 컨테이너 재시작 시 디스크가 초기화되므로 SQLite DB 파일이 사라집니다. 이 때문에 "수집 & 분석"으로 갱신된 데이터(47건)가 시간이 지나면 33건으로 되돌아갔습니다.

v20k는 **시드 데이터에 검증된 사건을 박제**해서, 컨테이너가 재시작되어도 항상 37건 유지됩니다. `seed_sample_data(force=True)`가 시작 시 기존 URL/해시 중복을 건너뛰고 새 시드만 추가하므로, 향후 새 사건이 발견되면 시드에 추가하기만 하면 됩니다.

### 3. 자동화 도구 추가 (`tools/db_to_seed.py`)

향후 새 사건을 시드로 추가할 때 사용할 수 있는 도구입니다.

```bash
# 4월 25일 이후 사건만 출력
python tools/db_to_seed.py path/to/osint.db --since 2026-04-25

# 특정 ID만 출력
python tools/db_to_seed.py path/to/osint.db --ids 35,36,37

# 특정 ID 이상
python tools/db_to_seed.py path/to/osint.db --min-id 34
```

출력은 `seed_data.VERIFIED_EVENTS` 리스트에 바로 붙여넣을 수 있는 딕셔너리 리터럴입니다. 단, **자동 추출은 부정확한 항목이 섞여있을 수 있으므로 항상 사람이 검토 후 정제**하는 것을 전제로 합니다 (actor/location 오인 가능, damage_summary가 기사 본문 일부일 수 있음).

워크플로우 예시:
1. 새 사건이 onrender 사이트에 수집되었다 가정
2. SSH나 다른 방법으로 osint.db 다운로드
3. `python tools/db_to_seed.py osint.db --since YYYY-MM-DD` 실행
4. 출력에서 검증 가능한 항목만 골라 `seed_data.VERIFIED_EVENTS` 끝에 붙여넣기
5. `damage_summary` / `tactical_assessment` / `strategic_assessment` 의 한국어 번역을 `ko_sentences.SENTENCE_KO`에 추가
6. git commit & push → Render 자동 재배포 → 영구 시드화

## v20j에서 이어진 핵심 기능

- **번역 품질 향상** (`translator_v2.py`) — 패턴 기반 SOV 한국어 재구성
- **다국어 데이터 콘텐츠** (`multilang.py`) — 행위자/수단/위치/상태/심각도 7개 언어
- **피해요약 톤 정제** (`tone_softener.py`) — 잔혹·선정적 표현 → 사실 보고형
- **표 셀 마우스오버 풀 텍스트** — 짧은 정제 셀 + title 속성 풀 텍스트

## 빠른 시작

```bash
pip install -r requirements.txt
python run_app.py
```

http://localhost:8000 → 자동으로 37건 시드 로드됨

## 파일 변경 요약

- 수정: `app/services/seed_data.py` — 4월 25일 4건 추가
- 수정: `app/services/ko_sentences.py` — 새 사건의 한국어 번역 9문장
- 수정: `app/services/ko_translate.py` — 행위자·위치·수단 사전 보강
- 수정: `app/services/multilang.py` — 새 행위자 7개 언어 매핑
- 신규: `tools/db_to_seed.py` — DB → 시드 코드 변환 도구
