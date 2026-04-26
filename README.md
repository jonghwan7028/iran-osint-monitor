# Iran-US War OSINT Monitor — v20j

2026년 이란-미국 전쟁(2/28 개전) 실시간 OSINT 대시보드.

## v20j 변경사항 (이전 버전 대비)

### 1. 번역 품질 대폭 개선 (`app/services/translator_v2.py` 신규)

**이전 문제**: 새로 수집되는 영어 헤드라인(Google News RSS, GDELT)은 사전 등록된 시드 문장이 아니므로, 단어 단위 치환만 수행되어 **한·영이 뒤섞인 어색한 결과**가 나왔습니다.

**개선**:
- 패턴 기반 SOV 한국어 재구성 (`A struck B`, `N people killed in C`, `A fired X at B` 등)
- 어휘 확장: 200+ 군사·외교 명사, 동사, 형용사, 도시·국가명, 무기 용어
- 시드 사전 일치 → 패턴 매칭 → 어휘 보강 + 정리의 우선순위 파이프라인

**번역 예시**:

| 영어 원문 | 이전 (단어 치환) | v20j |
|-----------|-----------------|------|
| Iran struck Tel Aviv in Israel | Iran 타격함 Tel Aviv in Israel | 이란, 이스라엘의 텔아비브을(를) 타격. |
| 47 people killed in airstrike on Tehran | 47 people 사망 in airstrike on 테헤란 | 공습에서 테헤란 주거 지역, 사람 47명 사망함. |
| Houthis attacked oil tanker in Red Sea | Houthis 공격 oil tanker in Red Sea | 후티 반군, 홍해의 유조선을(를) 공격. |

### 2. 다국어 데이터 콘텐츠 (`app/services/multilang.py` 신규)

**이전 문제**: 다국어 모드(es/zh/ja/fr/de) 선택 시 UI 라벨만 다국어로 바뀌고, **데이터 콘텐츠(행위자/대상/위치/수단/상태/심각도)는 영어 원문**이 그대로 노출되었습니다.

**개선**:
- 행위자, 수단, 위치, 검증상태, 심각도를 7개 언어(ko·en·es·zh·ja·fr·de)로 매핑
- 사건 목록 표의 모든 셀이 선택 언어로 자동 전환
- 모바일 뷰 셀(사건 개요/평가)도 다국어 적용

### 3. 피해요약 톤 정제 (`app/services/tone_softener.py` 신규)

**이전 문제**: 사건 목록 표의 "피해요약" 컬럼에 잔혹·선정적 표현(시신 묘사, 잔혹한 형용사 등)이 그대로 노출되어 **표 셀에서 시각적으로 강하게 강조**되었습니다.

**개선**:
- 한국어·영어 양방향 톤 정제 (잔혹 형용사·시신 묘사 → 사실 보고형 표현)
- 표 셀용 짧은 정제 버전 (긴 본문은 일일 브리핑·팝업에서 확인)
- 다수 사상자 신호 자동 감지 → 표 셀에 "ⓘ" 표시 (마우스오버: 풀 텍스트 표시)
- 영어 정제는 *번역 전*에 적용되어 한국어 결과에도 자동 반영

**정제 예시**:

| 원문 | 정제 후 |
|------|---------|
| Brutal massacre — at least 80 killed, body parts everywhere | 사망 — 최소 80 사망, 현장 내 다수의 잔해 |
| Charred bodies of dozens of civilians | casualties of dozens of civilians |
| 시체 50구가 발견되었으며 처참한 상태 | 사망자 50명이 발견되었으며 심각한 상태 |
| Catastrophic damage with apocalyptic scenes | severe damage with extensive scenes |

### 4. 표 셀 마우스오버 풀 텍스트

표 셀은 짧게 정제된 버전을 보여주지만, **마우스를 셀에 올리면(title 속성)** 정제된 풀 텍스트가 툴팁으로 표시됩니다.

### 5. 적용 범위

이 개선은 다음 모든 출력 경로에 자동 반영됩니다:
- 메인 대시보드 사건 목록 표 (`/`)
- 지도 팝업 (`/map`) — `build_bilingual_incident()` 패치
- 일일 브리핑 (`/brief/daily`) — `briefer.py` 패치
- 전략 분석 카드, 타임라인, 최근 이벤트 배너

## 빠른 시작

```bash
pip install -r requirements.txt
python run_app.py
```

http://localhost:8000 → "검증 데이터 로드" 클릭

## 파일 변경 요약

- 신규: `app/services/translator_v2.py`, `app/services/multilang.py`, `app/services/tone_softener.py`
- 수정: `app/api/routes.py`, `app/services/ko_translate.py`, `app/services/briefer.py`, `app/templates/index.html`
