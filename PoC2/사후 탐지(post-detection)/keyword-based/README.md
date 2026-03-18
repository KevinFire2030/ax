# PoC - 사후 탐지 (post-detection) / Keyword-based

메일 **사후 탐지** PoC의 "키워드 기반(keyword-based)" 스캐너입니다.

- 입력: CPCex에서 다운로드한 메일 이력 Excel
- 처리: 제목/본문/첨부파일명에서 키워드 문자열을 탐지
- 출력: 탐지 결과를 엑셀로 저장(검토용)

---

## 1) 준비물
- Python 3
- 패키지:
```bash
pip install -r requirements.txt
```

- 키워드 파일(한 줄 1키워드): `detection_keywords.md`

---

## 2) 실행

### A) 웹 UI 데모(추천)
```powershell
.\run_web.ps1
# (첫 실행은 패키지 설치로 1~3분 정도 걸릴 수 있습니다)
# 브라우저에서 http://127.0.0.1:8000 접속
```

(포트 변경)
```powershell
.\run_web.ps1 -Port 8010
```

### B) CLI(PowerShell: run.ps1)
```powershell
.\run.ps1 -InputXlsx .\sample.xlsx
```

### C) CLI(Python 직접 실행)
예)
```bash
python keyword-based_detection.py sample.xlsx
```

(선택) 키워드 파일을 직접 지정하고 싶으면:
```bash
python keyword-based_detection.py sample.xlsx detection_keywords.md
```

---

## 3) 동작 요약
- 키워드 파일(`detection_keywords.md`)을 읽어 리스트로 구성
- 각 행에 대해 아래 4개 텍스트를 합쳐서 검색
  - `제목`
  - `일반자료명: 삼성등록`
  - `일반자료명: 협력사등록`
  - `본문내용`
- 본문에 `data:image/...;base64,...` blob이 있으면 `<BASE64_IMAGE>`로 치환 (속도/오탐 방지)
- 키워드가 발견되면
  - `detected-title` / `detected-attachment` / `detected-body` / `detected-keyword` 컬럼에 기록

---

## 4) 출력

### 웹 UI
- 통합 엑셀 1개 다운로드
  - `Sheet1`: 전체 결과
  - (추가) `발신자부서명`별 시트: 히트된 행만 분리(검토 편의)
- 부서별 개별 파일 zip 다운로드
  - 부서별로 `HITS` 시트 1개(탐지 행만)

### CLI
- 기본 출력 파일명: `keyword_based_detection_by_dept.xlsx`
- Sheet 구성:
  - `Sheet1`: 전체 결과
  - (추가) `발신자부서명`별 시트: 히트된 행만 분리(검토 편의)

---

## 5) 팁
- 대량 데이터(월 20만+건)는 키워드 기반으로 1차 후보군을 만들고,
  문맥 기반(LLM) 분석은 후보에만 태우는 방식이 운영상 현실적입니다.
