# 이란-미국 전쟁 OSINT 모니터 v14

2026 이란전쟁(2월 28일 개전) 실시간 OSINT 대시보드.

## v12e 변경사항
- **한글 UI**: 모든 인터페이스를 한글로 통일
- **지도 표시 문제 해결**: 시간 필터(days) 기반이 아닌 **전체 데이터**를 지도에 표시
  - 기존 문제: seed 데이터의 고정 날짜가 window 밖으로 밀려 지도에 안 보임
  - 해결: `get_all_incidents()` 함수로 시간 필터 없이 전체 사건 표시
- **검증된 22건의 실제 이벤트** (Reuters, AP, BBC, CNN, Al Jazeera, NBC, CBS 등)
- **이란 공격 = 빨간 외각선 사각형** 으로 지도에 표시
- **색상 구분 테이블**: 이란측 빨간색, 미국/이스라엘 파란색, 기타 노란색

## 실행 방법

```bash
pip install -r requirements.txt
python run_app.py
# 또는
uvicorn app.main:app --reload --port 8000
```

http://localhost:8000 열고 **"검증 데이터 로드"** 클릭.

## 지도 범례
- 🔴 빨간 사각형 = 이란/대리세력 공격 (헤즈볼라, 후티, IRGC)
- 🔵 파란 원 = 미국/이스라엘 타격
- 🟡 노란 원 = 기타 이벤트 (정치, 외교)

## 요구사항
- Python 3.10+
- requirements.txt 참조
