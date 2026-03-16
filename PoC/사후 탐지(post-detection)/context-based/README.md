# PoC - 사후 탐지 (post-detection) / Context-based

메일 **사후 탐지** PoC의 "문맥 기반(context-based)" 탐지기입니다.

핵심 컨셉:
- 전수 데이터에서 1차로 후보군을 만들고(저비용)
- 후보군에만 LLM을 태워 문맥 판정(비용/시간 통제)

---

## 1) 준비물
- Python 3
- 패키지:
```bash
pip install -r requirements.txt
```

- 설정 파일: `.env`
- 프롬프트 파일: `prompt_context_detection.md`
- 키워드 파일: `detection_keywords.md` (1차 후보/보조 신호)

---

## 2) .env 주요 설정
- `OPENAI_API_KEY` (필수)
- `OPENAI_MODEL=gpt-5.2`
- `OPENAI_CONCURRENCY=5`
- 후보군 설정:
  - `CANDIDATE_RATIO` (예: 0.05)
  - `CANDIDATE_MIN_ROWS` / `CANDIDATE_MAX_ROWS`
- 히트 기준:
  - `HIT_RISK_LEVEL_THRESHOLD` (예: 4)
- 캐시:
  - `CACHE_ENABLED=true`
  - `CACHE_DIR=...`

---

## 3) 실행

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

### B) PowerShell(기존 CLI: run.ps1)
```powershell
.\run.ps1 -InputXlsx .\sample.xlsx
```

- 최초 1회는 `.env`가 없으면 `.env.template`에서 만들어주고, 메모장을 열어 API Key 입력을 유도합니다.

### C) Python 직접 실행
예)
```bash
python context-based_detection.py sample.xlsx
```

---

## 4) 동작 요약
1) 입력 엑셀 로드
2) 1차 후보군 생성
   - 키워드 히트 + 요청 의도 신호 + 첨부 확장자 신호 등을 이용해 `candidate_score` 생성
   - 후보군은 `.env`의 ratio/min/max로 상위만 선택
3) 후보군에 대해서만 LLM 호출 (병렬)
4) 결과를 엑셀로 저장
   - `Sheet1`: 전체 결과
   - (추가) `발신자부서명`별 HIT 시트: 검토 편의

---

## 5) 출력

### 웹 UI
- 통합 엑셀 1개 다운로드
  - `Sheet1`: 전체 결과
  - (추가) `발신자부서명`별 HIT 시트
- 부서별 개별 파일 zip 다운로드
  - 부서별 `HITS` 시트 1개(=HIT 행만)

### CLI
- 출력 파일명은 기본적으로 `.env`의 `OUTPUT_XLSX_NAME`을 따르며,
  덮어쓰기를 방지하기 위해 실행 시점 timestamp가 붙도록 구현되어 있을 수 있습니다.

---

## 6) 팁(운영 관점)
- 전수(20만+)를 LLM으로 직접 돌리면 비용/시간이 폭발합니다.
- PoC에서는 "후보만 LLM" 구조가 가장 설득력 있고 현실적입니다.
- 담당자 검토 UI/승인 플로우는 별도 PoC(사전 차단)에서 시연하면 좋습니다.
