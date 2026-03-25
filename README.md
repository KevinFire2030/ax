# AX / KIPRIS 작업 폴더

이 브랜치는 **KIPRIS API 실험 + 특허 문서 작성 + 보안 LLM Gateway PoC MVP** 중심으로 정리되어 있습니다.

## 주요 목적
- KIPRIS Plus Open API 호출/검증
- 특허 아이디어 선행검색 및 유사특허 스캔
- 특허 제출용 문서(청구항/발표문/슬라이드 문안) 정리
- 보안 LLM Gateway MVP 데모 및 실시예 로그 캡처

## 디렉터리/파일 구조
- `samples/`  
  KIPRIS 검색 응답(XML/JSON) 및 스캔 결과 샘플
- `test_kipris.py`  
  KIPRIS `getAdvancedSearch` 테스트 스크립트
- `parse_kipris_xml.py`  
  KIPRIS XML 응답을 CSV/JSON으로 변환
- `REST_사용법.md`  
  KIPRIS REST 사용법 정리
- `특허_제출패키지_보안LLM게이트웨이_v*.md`  
  특허 제출 패키지 문서
- `선행특허_충돌차별_매트릭스_v1.md`  
  선행특허 대비 충돌/차별 분석
- `발표 맨트(90초_임원용 45초_변리사용 2분).md`  
  발표 멘트 통합본
- `미팅용 1장 슬라이드 문안.md`  
  미팅용 슬라이드 1장 문안
- `PoC/`
  - `00_mvp/`: FastAPI+WebUI MVP 코드
  - `01_구현흐름도/`: 도 1~7 정리
  - `02_실시예_로그캡처/`: 정상/차단/폴백/혼합 로그

## PoC MVP 빠른 실행
- 경로: `PoC/00_mvp`
- 실행: `powershell -ExecutionPolicy Bypass -File .\run.ps1`
- 접속: `http://127.0.0.1:8070`
- 시나리오 캡처: `python run_cases.py`
- 결과: `PoC/02_실시예_로그캡처/*/result.json`

## UI 구성(최신)
- 왼쪽: 입력(모드 설명 포함)
- 가운데: 처리 과정(동적 단계 표시)
- 오른쪽: 출력(결과 요약, 결과 JSON, 최근 로그)

## 비고
- 본 브랜치는 KIPRIS/특허 문서와 PoC MVP 검증 산출물을 중심으로 정리되어 있습니다.
