# PoC 00_mvp 실행 가이드

## 1) 실행
```powershell
cd E:\ax\kipris\PoC\00_mvp
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

접속: http://127.0.0.1:8070

## 2) API
- `POST /api/analyze`
- `GET /api/logs`

## 3) 시나리오 로그 생성
```powershell
python run_cases.py
```

생성 결과:
- `E:\ax\kipris\PoC\02_실시예_로그캡처\정상\result.json`
- `E:\ax\kipris\PoC\02_실시예_로그캡처\차단\result.json`
- `E:\ax\kipris\PoC\02_실시예_로그캡처\폴백\result.json`
- `E:\ax\kipris\PoC\02_실시예_로그캡처\혼합라우팅\result.json`

## 4) MVP 포함 기능
- 규칙 기반 DLP + 위험도 점수
- 정책 기반 라우팅(auto/internal/external/hybrid)
- 세그먼트(문장 단위) 혼합 라우팅
- 응답 2차 재검사(post-check)
- 감사로그(JSONL)
