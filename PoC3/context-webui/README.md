# PoC3 - 문맥 검출 WebUI (DRM 업로드 없음)

## 목표
- 웹 UI에서 문맥 기반 점검 데모
- DRM 때문에 업로드 없이 **서버가 로컬 파일 경로의 엑셀**을 읽어서 사용
- 내부망 접근: 서버를 `10.246.72.83:8000`에서 띄우고 다른 사내 PC에서 접속

## 실행(Windows)
1) `.env.template` → `.env` 복사 후 값 채우기
2) 실행

```powershell
cd .\PoC3\context-webui
.\run_web.ps1 -SampleXlsx .\sample.xlsx -Host 0.0.0.0 -Port 8000
```

접속:
- 서버PC 로컬: `http://127.0.0.1:8000`
- 다른 사내 PC: `http://10.246.72.83:8000`

## LLM
- `LLM_PROVIDER=gauss|openai`
- GAUSS는 `GAUSS_RPM`(trial 3 / prd 60) 설정 가능

## 주의
- 방화벽/보안 정책으로 8000 포트 인바운드가 막혀있으면 외부 PC에서 접속이 안 됩니다.
