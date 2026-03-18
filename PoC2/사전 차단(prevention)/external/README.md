# CPCex 사전 차단 PoC (외부 호출 방식: 훅/에이전트 서버)

이 폴더는 **CPCex 전송 직전 훅 → 외부(에이전트) 서버가 LLM 호출 → allow/warn/block 리턴** 흐름을 PoC로 재현합니다.

- ✅ CPCex는 전송 직전 payload를 **HTTP POST**로 보냄
- ✅ 외부 서버(`detection_agent_webhook.py`)가 LLM(gpt-5.2)로 문맥 판단
- ✅ 결과(policy_action)에 따라 CPCex가 Allow/Warn/Block 분기
- ✅ 웹 UI 데모(`/ui`)로 실제 메일 전송처럼 팝업/승인 라우팅까지 시연 가능

---

## 0) 빠른 시작 (5분)

### (1) 의존성 설치
```bash
pip install fastapi uvicorn openai python-dotenv pandas openpyxl requests
```

### (2) 환경변수(.env) 준비
- `.env` 파일에 `OPENAI_API_KEY`가 필요합니다.
- (추천) 아래 스크립트로 `.env`를 생성하세요:
```powershell
.\create_env.ps1
```
- 또는 `.env.template`을 복사해서 `.env`를 만든 뒤 `OPENAI_API_KEY`를 채웁니다.

### (3) 서버 실행

#### A) PowerShell(추천: run_server.ps1)
```powershell
cd /d "E:\ax\상생\PoC\사전 차단(prevention)\external"
.\run_server.ps1
```

#### B) Python 직접 실행
```powershell
cd /d "E:\ax\상생\PoC\사전 차단(prevention)\external"
python .\detection_agent_webhook.py
```

정상 확인:
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/ui

(선택) UI만 열기:
```powershell
.\run_ui.ps1
```

### (4) 훅 시뮬레이터 실행(샘플 엑셀)

#### A) PowerShell(추천: run_simulator.ps1)
```powershell
cd /d "E:\ax\상생\PoC\사전 차단(prevention)\external"
.\run_simulator.ps1 -InputXlsx .\sample_data_raw.xlsx -AgentUrl http://127.0.0.1:8000/check
```

#### B) Python 직접 실행
```powershell
cd /d "E:\ax\상생\PoC\사전 차단(prevention)\external"
$env:PYTHONIOENCODING="utf-8"
python .\cpcex_hook_simulator.py .\sample_data_raw.xlsx http://127.0.0.1:8000/check
```
- 실행 시 같은 폴더에 JSONL 로그가 생성됩니다:
  - `cpcex_sim_result_YYYYMMDD_HHMMSS.jsonl`

---

## 1) 파일 구성

- `detection_agent_webhook.py`
  - FastAPI 웹훅 서버
  - `/check` : LLM 호출 후 policy_action(allow/warn/block) 리턴
  - `/ui` : 메일 작성/전송 데모 1페이지
  - `/sample/random` : 샘플데이터에서 랜덤 1행 로드(폼 자동 채움)
  - `/send` : 전송(데모, 로그만 가정)
  - `/approve` : 승인 요청 생성(데모)

- `cpcex_hook_simulator.py`
  - 샘플 엑셀을 한 행씩 읽어서 `/check` 호출
  - 결과에 따라 Allow/Warn/Block 분기 문구를 콘솔 출력
  - JSONL 로그를 UTF-8로 저장

- `ui_mail_demo.html`
  - 메일 작성 UI(한글)
  - Allow/Warn/Block 팝업 + Block이면 전송 버튼 비활성

- `prompt_context_detection.md`
  - LLM 프롬프트 템플릿

- `approval_routing.json`
  - block일 때 표시할 3단계 승인 라우팅 매핑(기본값 포함)

- `sample_data_raw.xlsx`
  - 테스트용 샘플 데이터

- `.env`
  - 실행 설정(OPENAI_API_KEY, 모델/파라미터, 임계값, 파일 경로)

---

## 2) CPCex 연동 포인트(개발자용)

CPCex 전송 직전, 아래 payload를 외부 서버에 POST 합니다.

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
    {"filename": "Q8-PS-BTM BLOCK-V3.0-0106.x_t", "extension": "x_t"}
  ],
  "timestamp": "2026-03-15T01:00:00"
}
```

### 호출
- POST `http://<agent-host>:8000/check`

### 결과로 분기
- allow → 전송
- warn → 팝업 + 전송 허용(override 로그)
- block → 전송 중지 + 승인(3단계)

---

## 3) 운영 시 주의사항(간단)

- **서버 가용성**: 외부 서버 다운 시 CPCex 전송이 영향받을 수 있음 → 타임아웃/기본정책(warn) 설계 필요
- **키 관리**: `.env`의 OPENAI_API_KEY 보호
- **로그/감사**: warn override / 승인 이력 저장
- **성능**: 실시간 전송 직전 호출이므로 타임아웃(2~5초) 권장
