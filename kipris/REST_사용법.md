# KIPRIS Plus REST 사용법 (특허·실용 공개·등록공보)

기준 페이지:  
`https://plus.kipris.or.kr/portal/popup/service/DBII_000000000000001/view.do`

---

## 1) 이 서비스가 제공하는 기능(페이지 분석 결과)
해당 페이지는 **특허·실용 공개·등록공보** API의 기능 목록을 카테고리로 보여줍니다.

- 일반검색
  - 단어(폐기예정), 번호(폐기예정)
- 항목별검색
  - 전체검색, 자유검색, 출원번호, CPC, 발명의명칭, 초록, 청구범위, IPC 등
- 서지정보
  - 서지상세/요약, IPC/CPC, 출원인/발명자, 패밀리, 청구항, 우선권 등
- 도면/전문
  - 공개전문 PDF, 공고전문 PDF, 대표도면, 전문파일정보 등
- 부가기능
  - 변동정보, IPC코드 조회, 속보서비스 등

즉, 단순 키워드 검색뿐 아니라 **번호 조회, 서지 상세, PDF/도면, 변동이력**까지 조회 가능한 구조입니다.

---

## 2) REST 호출 준비

### (1) 인증키 준비
- KIPRIS Plus에서 발급된 API 키를 `.env`에 저장

```env
KIPRIS_API_KEY=발급받은키
```

### (2) 호출 방식
- KIPRIS Plus는 항목마다 호출 URL/파라미터가 다릅니다.
- **각 API 항목 상세 화면의 “REST 요청 URL/요청 파라미터”를 기준**으로 호출해야 합니다.
- 같은 서비스 내에서도 API마다 필수 파라미터가 다릅니다.

---

## 3) 권장 사용 순서 (실무형)

1. **검색 API**로 후보 문헌 목록 확보  
   - 예: 자유검색/발명의명칭/출원번호 검색
2. 목록 결과의 식별자(출원번호/공개번호/등록번호) 추출
3. **서지정보 API**로 상세 데이터 확장
4. 필요 시 **전문/PDF API**로 원문/첨부 조회
5. 최종적으로 내부 리포트용 스키마로 정규화

---

## 4) Python 기본 호출 템플릿
> 아래는 공통 패턴 예시입니다.  
> 실제 `base_url`, 파라미터명(q, applicationNumber 등)은 **해당 API 상세 문서 값으로 교체**하세요.

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("KIPRIS_API_KEY")

base_url = "<각 API 상세의 REST URL>"
params = {
    "serviceKey": API_KEY,
    # "pageNo": 1,
    # "numOfRows": 10,
    # "q": "AI",
    # "applicationNumber": "...",
    # "_type": "json",  # 지원 시 사용
}

resp = requests.get(base_url, params=params, timeout=30)
resp.raise_for_status()
print(resp.text[:1000])
```

---

## 5) 자주 발생하는 오류/주의사항

1. **인증키 인코딩 문제**
   - 인코딩/디코딩 키 혼용 시 401/인증 오류 발생 가능
2. **월 호출량 초과**
   - 현재 무료 플랜: 월 1,000건
3. **폐기예정 API 사용**
   - “단어/번호(폐기예정)” 대신 항목별검색 API 사용 권장
4. **응답 포맷 혼동(XML/JSON)**
   - API별 지원 포맷이 다를 수 있으므로 상세 문서 확인 필수

---

## 6) 빠른 스타트 체크리스트

- [ ] `.env`에 `KIPRIS_API_KEY` 저장
- [ ] KIPRIS Plus 상세 화면에서 사용할 API 1개 선택
- [ ] REST URL/필수 파라미터 복사
- [ ] Postman 또는 Python으로 1건 테스트
- [ ] 성공 응답 스키마 확인 후 코드에 반영

---

## 7) 현재 프로젝트 폴더 권장 파일 구성

- `E:\ax\kipris\.env`
- `E:\ax\kipris\REST_사용법.md`  ← 현재 파일
- `E:\ax\kipris\test_kipris.py` (테스트 스크립트)
- `E:\ax\kipris\samples\` (샘플 응답 저장)

---

## 8) getAdvancedSearch 샘플 테스트 (현재 반영 완료)

`test_kipris.py`는 아래 오퍼레이션 기준으로 맞춰져 있습니다.
- Operation: `getAdvancedSearch`
- URL: `http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch`

실행 예시:

```powershell
cd E:\ax\kipris
python test_kipris.py --invention-title 센서 --astrt-cont 발명 --rows 20 --save
```

샘플 문서와 유사한 요청 예시:

```powershell
python test_kipris.py --invention-title 센서 --astrt-cont 발명 --sort-spec PD --desc-sort true --save
```

응답은 기본 XML이며 `samples/advanced_search_*.xml`로 저장됩니다.

> 주의: 실행 전 `.env`의 `KIPRIS_API_KEY`를 반드시 입력해야 합니다.
