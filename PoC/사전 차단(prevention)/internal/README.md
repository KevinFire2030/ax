# CPCex 사전 차단 PoC (내부 호출 방식: CPCex가 LLM을 직접 호출)

이 폴더는 **CPCex 내부(전송 직전)**에서 LLM(OpenAI)을 직접 호출해 `allow / warn / block`을 결정하는 PoC 골격입니다.

- ✅ 훅(Webhook) 서버 호출 없음
- ✅ CPCex 서버 코드가 전송 직전 `precheck_mail(payload)`를 호출
- ✅ 결과에 따라 UI 분기(Allow/Warn/Block) + Block이면 **3단계 승인 라우팅** 표시/생성

---

## 0) 빠른 시작 (5분)

### (1) 의존성 설치
```bash
pip install openai python-dotenv pandas openpyxl fastapi uvicorn
```

### (2) 환경변수(.env) 준비
- `.env.template`을 복사해서 `.env`를 만듭니다.
- `OPENAI_API_KEY`를 꼭 입력합니다.

Windows PowerShell 예시:
```powershell
cd /d "E:\ax\상생\사전 차단\internal"
Copy-Item .\.env.template .\.env
notepad .\.env
```

### (3) 실행 2가지 중 하나 선택

#### A안) 웹 UI 데모(가장 직관적)

(추천) PowerShell 스크립트로 실행:
```powershell
cd /d "E:\ax\상생\PoC\사전 차단(prevention)\internal"
.\run_server.ps1
```

직접 실행:
```powershell
cd /d "E:\ax\상생\PoC\사전 차단(prevention)\internal"
python .\internal_ui_server.py
```

브라우저에서 접속:
- http://127.0.0.1:8001/ui

(선택) UI만 열기:
```powershell
.\run_ui.ps1
```

UI에서:
- 제목/본문/첨부파일명/외부수신자 여부 입력
- **전송 전 검사** 또는 **전송** 클릭
- 결과가 Allow/Warn/Block 팝업으로 표시됨

#### B안) 엑셀 기반 배치 시뮬레이터(로그 남기기)

(추천) PowerShell 스크립트로 실행:
```powershell
.\run_batch_simulator.ps1 -InputXlsx ..\external\sample_data_raw.xlsx
```

직접 실행:
```powershell
cd /d "E:\ax\상생\PoC\사전 차단(prevention)\internal"
python .\cpcex_internal_simulator.py ..\external\sample_data_raw.xlsx
```
- 결과 JSONL이 생성됩니다:
  - `internal_precheck_result_YYYYMMDD_HHMMSS.jsonl`

---

## 1) 파일 구성

- `cpcex_internal_precheck.py`
  - 핵심 로직
  - `precheck_mail(payload)` 함수 제공
  - LLM 호출 → risk_score/level 파싱 → policy_action 결정
  - block일 때 승인 라우팅(3단계) 생성
  - (옵션) 캐시 지원

- `internal_ui_server.py`
  - FastAPI 서버
  - `/ui` (메일 작성 1페이지), `/check`(사전검사), `/send`(전송 데모), `/approve`(승인요청 데모)
  - `/check`에서 **webhook 호출이 아니라** `precheck_mail()`을 직접 호출

- `cpcex_internal_simulator.py`
  - 샘플 엑셀을 한 행씩 읽어서 `precheck_mail()`을 호출하는 배치 시뮬레이터

- `prompt_context_detection.md`
  - LLM 프롬프트 템플릿 (PoC용)

- `approval_routing.json`
  - `발신자부서명(sender_dept)` 기반 3단계 승인 라우팅 매핑(기본값 포함)

- `.env.template`
  - 실행에 필요한 환경변수 템플릿

- `ui_mail_demo.html`
  - 웹 UI(메일 작성 화면) HTML

---

## 2) CPCex 연동 포인트(개발자용)

CPCex 서버(전송 직전)에서 아래 payload를 구성해 호출합니다.

### 입력 payload 예시
```json
{
  "mail_id": "DX260106-24040",
  "sender_dept": "부품품질그룹(MX)",
  "sender_id": "poc.user",
  "subject": "[검토요청] 도면 검토 및 회신 부탁드립니다",
  "body_text": "첨부 도면 검토 요청드립니다...",
  "recipients": [
    {"recipient_company": "(주)협력사", "is_external": true}
  ],
  "attachments": [
    {"filename": "Q8-PS-BTM BLOCK-V3.0-0106.x_t", "extension": "x_t"},
    {"filename": "spec_rev3.pdf", "extension": "pdf"}
  ],
  "timestamp": "2026-03-15T01:00:00"
}
```

### 호출
```python
from cpcex_internal_precheck import precheck_mail
result = precheck_mail(payload)
```

### 결과(result)로 분기
- `policy_action == "allow"` → 전송
- `policy_action == "warn"` → 팝업(사유/근거) + 전송은 허용(override 로그 남김)
- `policy_action == "block"` → 전송 중지 + `approval_route` 기반 3단계 승인 프로세스

---

## 3) 운영 시 주의사항(간단)

- **키 관리**: `.env` 대신 Secret Manager 권장
- **타임아웃/실패 정책**: 전송 직전이므로 `OPENAI_TIMEOUT_SECONDS`를 낮게(2~5초) + 실패 시 기본정책(보통 warn)
- **첨부 내용 미확보 제약**: 현재 PoC는 파일명/확장자 기반(내용 분석 없음)
- **로그/감사**: Warn override / 승인 이력 반드시 저장

---

## 4) .env 주요 설정(요약)

- `OPENAI_API_KEY` (필수)
- `OPENAI_MODEL=gpt-5.2`
- `OPENAI_TIMEOUT_SECONDS=5`
- `WARN_RISK_LEVEL_THRESHOLD=2`
- `BLOCK_RISK_LEVEL_THRESHOLD=4`
- `FAIL_OPEN_POLICY=warn`
- `PROMPT_FILE_PATH=./prompt_context_detection.md`
- `APPROVAL_ROUTING_PATH=./approval_routing.json`
- `UI_HTML_PATH=./ui_mail_demo.html`
