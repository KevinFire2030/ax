# AX PoC Demos (메일 기술자료 리스크 탐지/차단)

이 레포는 **메일 기술자료 수발신 리스크**를 AI로 탐지/등급화하고, 사전 차단(Allow/Warn/Block) UX까지 시연하기 위한 PoC 데모 모음입니다.

## 구성

### 1) PoC Playbook (비개발자 포함)
- `PoC/PoC Playbook.md`

### 2) 사후 탐지 (post-detection)
- 키워드 기반: `PoC/사후 탐지(post-detection)/keyword-based/`
- 문맥 기반(LLM): `PoC/사후 탐지(post-detection)/context-based/`

각 폴더에 `README.md`, `run.ps1`, `requirements.txt`가 있어 바로 실행 흐름을 확인할 수 있습니다.

### 3) 사전 차단 (prevention)
- 외부 훅/에이전트 서버 방식: `PoC/사전 차단(prevention)/external/`
- CPCex 내부 호출 방식: `PoC/사전 차단(prevention)/internal/`

각 폴더에 `README.md`, `run_server.ps1`, `run_ui.ps1` 등이 있으며,
`create_env.ps1`(또는 `.env.template`)로 `.env`를 생성한 뒤 `OPENAI_API_KEY`를 입력해 실행합니다.

## 보안/주의
- `.env`(API Key), `*.xlsx`(메일 데이터), `*.jsonl`(로그)는 민감할 수 있어 커밋 대상에서 제외했습니다.
- PoC 실행 시 생성되는 결과 파일/로그는 내부 공유 정책에 따라 관리하세요.
