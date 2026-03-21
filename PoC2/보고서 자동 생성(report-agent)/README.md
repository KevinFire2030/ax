# 보고서 자동 생성 에이전트 PoC (웹 + DOCX 다운로드)

## 목적
- 사용자 입력(제목/키워드 + 링크(URL) 또는 본문 붙여넣기)을 받아
- 기존 보고서(샘플 13개 → 추후 300개)에서 유사 스타일을 찾아
- **AX 보고서 생성 규칙**(섹션 순서/불릿 문체)을 준수하는 보고서 초안을 생성합니다.
- 결과는 웹에서 미리보기 + DOCX 다운로드로 제공합니다.

## 폴더 구조
- `report_agent_server.py` : FastAPI 서버(웹 UI + 생성 API)
- `web/index.html` : 웹 데모(한 페이지)
- `data/existing_reports/*.docx` : 기존 보고서 샘플(현재 13개 복사됨)
- `prompts/tone_and_report_json.md` : LLM 프롬프트(출력은 JSON)
- `outputs/` : 생성된 DOCX 저장

## 준비
```powershell
cd /d "E:\ax\상생\PoC\보고서 자동 생성(report-agent)"
python -m pip install -r requirements.txt
```

## .env 준비
```powershell
Copy-Item .\.env.template .\.env
notepad .\.env
```
- `OPENAI_API_KEY` 입력

## 실행
```powershell
python .\report_agent_server.py
```

접속:
- http://127.0.0.1:8010/

## 사용법(데모)
1) 제목/키워드 입력
2) URL 입력 (가능하면)
3) URL 수집이 실패하면 **기사 본문 붙여넣기**에 본문을 붙여넣기
4) [보고서 생성] 클릭
5) 오른쪽에서
   - 유사 보고서 Top-K(선택 근거)
   - 보고서 미리보기
   - DOCX 다운로드

## PoC 한계
- 현재는 RAG가 TF-IDF 기반(로컬)이며, 추후 임베딩 인덱스로 확장 가능
- '자료 모음' 형태 docx(한 파일에 여러 보고서) 분할은 1차 PoC에서 미구현(추후 개선)
