# Gauss API Adapter (PoC)

PoC에서 ChatGPT(OpenAI) 대신 **Gauss Chat APIs(OpenAPI)** 를 호출하기 위한 최소 어댑터입니다.

- 대상 API
  - `GET /openapi/chat/v1/models`
  - `POST /openapi/chat/v1/messages`
- 의도적으로 단순화
  - `isStream=false`만 지원 (스트리밍 파싱 제외)
  - 멀티턴은 `contents` 리스트로만 지원

## Setup
1) `.env.template` → `.env` 복사 후 값 채우기
2) 설치

### Windows
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Quick test
```bash
python example_basic.py
```

## PoC 기본 모델
- PoC에서는 우선 `GaussO`(속도 우선)로 고정해서 사용 권장
- `GAUSS_TEXT_MODEL_ID`는 `../quickcheck/gauss_quickcheck.py models`로 조회한 modelId를 사용
