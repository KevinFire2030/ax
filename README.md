# AX / KIPRIS 작업 폴더

이 브랜치는 **KIPRIS API 실험 + 특허 문서 작성 산출물** 중심으로 정리되어 있습니다.

## 주요 목적
- KIPRIS Plus Open API 호출/검증
- 특허 아이디어 선행검색 및 유사특허 스캔
- 특허 제출용 문서(청구항/발표문/슬라이드 문안) 정리

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

## 실행 가이드
1. `.env`에 `KIPRIS_API_KEY` 설정
2. 테스트 호출
   - `python test_kipris.py --invention-title 센서 --astrt-cont 발명 --rows 20 --save`
3. 응답 파싱
   - `python parse_kipris_xml.py --input samples/advanced_search_xxx.xml`

## 비고
- 본 브랜치는 기존 PoC 실행 폴더(`PoC/`)를 제거하고, KIPRIS/특허 산출물 중심으로 정리한 상태입니다.
