# Gauss Chat API quickcheck

Gauss Chat APIs(OpenAPI) 어댑터 설계/적용 전에 **기본 동작(모델조회/단건 메시지)**만 빠르게 확인하는 최소 코드입니다.

## 준비
1) `.env.template` → `.env`로 복사 후 값 채우기
2) 설치

### Windows
```powershell
.\run.ps1
```

### Linux/macOS
```bash
chmod +x run.sh
./run.sh
```

## 실행
### 1) 모델 목록 조회(TEXT)
```bash
python gauss_quickcheck.py models
```

### 2) 전체 모델 목록(TEXT/I2T/T2I)
```bash
python gauss_quickcheck.py all-models
```

### 3) 단건 대화 호출
- `.env`에 `GAUSS_TEXT_MODEL_ID`를 세팅했으면:
```bash
python gauss_quickcheck.py chat
```

- 모델을 직접 지정하면:
```bash
python gauss_quickcheck.py chat <MODEL_ID> "안녕하세요"
```

## 참고
- 헤더는 `.env`에서 아래 key로 직접 받습니다.
  - `x-generative-ai-client`
  - `x-openapi-token`
  - (옵션) `x-generative-ai-user-email`
- 기본 API
  - `GET /openapi/chat/v1/models`
  - `POST /openapi/chat/v1/messages`
