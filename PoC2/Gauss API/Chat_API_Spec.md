# Gauss Chat APIs (OpenAPI) - Spec (원문)

> Source: 전하가 전달한 문서(file_125---d16c37dc-e782-4c57-a779-d2471b831479.md)


# 

1.1Chat APIs Overview

Chat APIs는 서비스 내 제공되는 모델을 대상으로 응답을 호출할 수 있는 API를 제공합니다. API를 통해 제공되는 답변은 서비스의 필터링을 적용하여 제공합니다.

Chat APIs 에서 제공하는 API는 다음과 같습니다.

GET /openapi/chat/v1/models

API로 사용할 수 있는 대화 모델의 리스트를 조회합니다.

POST /openapi/chat/v1/messages

messages API는 대화에 대한 모델 응답을 생성합니다.

GET /openapi/chat/v1/all-models

API로 사용할 수 있는 대화 모델과 이미지 모델의 리스트를 조회합니다.

POST /openapi/chat/v1/messages-with-models

messages-with-models API는 대화모델, 이미지 모델에 대한 응답을 생성합니다. Single/Multi-turn 대화와 이미지 분석을 위한 FileUpload 기능을 지원합니다.


# 

1.2API 명세

## 

GET /openapi/chat/v1/models

사용자 포털에서 권한을 가진 모델(Text)을 API로 조회할 수 있습니다.

Text : 대화모델

Header

|Field|Type|Required|Description|Value|
|---|---|---|---|---|
|Content-Type|string|optional|Type of content|application/json|
|x-generative-ai-client|string|required|Client authentication information|ex) eyJXXX|
|x-openapi-token|string|required|OpenAPI Token information|ex) Bearer eyJXXX|
|x-generative-ai-user-email|string|optional|Portal user email|ex) kim.samsung@samsung.com|

Response

|Field|Type|Description|Value|
|---|---|---|---|
|modelId|String|Model Id||
|name|list|Model Name|[<br><br>{<br><br>"languageCode": "ko",<br><br>"content": "모델명"<br><br>}<br><br>]|
|descrption|list|Model Description|[<br><br>{<br><br>"languageCode": "ko",<br><br>"content": "설명"<br><br>}<br><br>]|

호출 예시 (python)

import requests
YOUR_CLIENT_KEY = ""
YOUR_PASS_KEY = ""
ENDPOINT_URL = ""
YOUR_EMAIL = ""
headers = {
  "x-generative-ai-client": YOUR_CLIENT_KEY,
  "x-openapi-token": YOUR_PASS_KEY,
  "x-generative-ai-user-email": YOUR_EMAIL
}
api_endpoint_url = f"{ENDPOINT_URL}/openapi/chat/v1/models"
response=requests.get(
    api_endpoint_url,
    headers=headers
)
# 응답 반환
print(response.json())

※ Endpoint URL은 Open API 신청시 발급되는 URL로 적용하여 사용할 수 있습니다.

## 

POST /openapi/chat/v1/messages

사용자 입력에 대한 대한 모델의 응답을 생성합니다.

Header

|Field|Type|Required|Description|Value|
|---|---|---|---|---|
|Content-Type|string|optional|Type of content|application/json|
|x-generative-ai-client|string|required|Client authentication information|ex) eyJXXX|
|x-openapi-token|string|required|OpenAPI Token information|ex) Bearer eyJXXX|
|x-generative-ai-user-email|string|optional|Portal user email|ex)kim.samsung@samsung.com|

Request

|Field|Type|Required|Description|Value|
|---|---|---|---|---|
|modelIds|array|required|model id list|ex) ["0196f1fc-2858-70a9-a232-74dbddb971d0"]|
|contents|list[string]|required|contents|ex) [“Hello”]|
|isStream|boolean|optional|Stream or not (default: True)|ex) False / True|
|llmConfig|object|optional|LLM Config info|Properties 참고|
|systemPrompt|string|optional|System prompt for LLM to use|ex) 예시 참고|

> llmConfig Properties

|Name|Description|
|---|---|
|temperature|모델의 확률 분포를 조절합니다. 값이 1보다 크면 확률 분포가 더욱 고르게 퍼지게 되고, 값이 1보다 작으면 확률 분포가 더욱 뾰족하게 집중됩니다. (0<temperature<1)|
|repetion_penalty|반복된 단어의 출현 확률을 조절합니다. 값이 1보다 크면 반복된 단어가 나타날 확률이 줄어들게 되고, 값이 1보다 작으면 반복된 단어가 나타날 확률이 증가하게 됩니다.|
|decoder_input_details|디코더의 입력 형태를 결정합니다. use_cache를 True로 설정하고 past_key_values를 None으로 설정하면, 디코더는 이전 타임스텝의 캐시값을 이용하여 다음 타임스텝의 입력을 생성합니다. use_cache를 False로 설정하고 past_key_values를 None으로 설정하면, 디코더는 이전 타임스텝의 마지막 히든 상태를 이용하여 다음 타임스텝의 입력을 생성합니다. past_key_values를 임의의 값으로 설정하면, 디코더는 해당 값을 이용하여 다음 타임스텝의 입력을 생성합니다.|
|seed|모델의 난수 발생기를 시드하는 데 사용됩니다. 동일한 시드를 사용하면 모델은 항상 동일한 순서로 출력을 생성합니다.|
|top_k|모델이 고려할 후보 단어의 수를 제한합니다. 큰 값을 사용하면 더 다양한 단어를 선택할 수 있지만, 계산 시간이 오래 걸릴 수 있습니다. (1<=top_k)|
|top_p|확률 분포의 상위 p%를 고려하여 단어를 선택합니다. 이렇게 하면 선택된 단어들이 확률 분포를 고르게 대표하도록 하여 다양성을 높일 수 있습니다. (`top_p` must be > 0.0 and < 1.0)|
|max_new_tokens|생성된 텍스트의 최대 길이를 결정합니다. 예를 들어, max_new_tokens=10으로 설정하면 모델은 최대 10개의 토큰을 생성할 수 있습니다.|

> Request Body 예시

{
    "modelIds": ["0196f1fc-2858-70a9-a232-74dbddb971d0"],
    "contents":["안녕하세요?","네 안녕하세요", "내 이름은 LCY인데 너 이름은 뭐니?"],
    "isStream": true,
    "llmConfig": {
        "max_new_tokens": 2024,
        "seed": null,
        "top_k": 14,
        "top_p": 0.94,
        "temperature": 0.4,
        "repetition_penalty": 1.04
    },
    "systemPrompt": "안녕하세요. 사용자 질문에 친절히 대답해주세요."
}

Response

※ Stream 으로 응답을 받을경우 Field 명이 카멜케이스가 아닌 스네이크케이스로 표시됩니다.

예) modelType -> model_type

|Field|Type|Description||
|---|---|---|---|
|id|integer|openapi message Id|**DEPRECATED**|
|parentMessageId|string|openapi message parent id|**DEPRECATED**|
|parentMessageCreatedAt|DateTime|parentMessage creation time|**DEPRECATED**|
|chatId|integer|chat Id|**DEPRECATED**|
|userId|integer|user Id||
|modelId|string|LLM ModelId|**DEPRECATED**|
|modelType|string|LLM ModelType||
|content|string|Answer||
|createdAt|DateTime|Message creation time|**DEPRECATED**|
|completionToken|integer|Answer Token Usage|**DEPRECATED**|
|promptToken|integer|Question Token Usage|**DEPRECATED**|
|truncated|string|Whether the question is truncated or not||
|finishReason|string|FinishReason ( stop : normal, length : Answer length exceeded )||
|filterBlockReason.ko|string|Filter block reason(ko)||
|filterBlockReason.en|string|Filter block reason(en)||
|filterBlockReason.policy_id|string|Filter block reason(policy_id)||
|filterBlockReason.message|string|Filter block reason(message)||
|filterBlockReason.result_code|string|Filter block reason(result_code)||
|filterBlockReason.filter_log_id|string|Filter block reason(filter_log_id)||
|status|string|Status||
|responseCode|string|ResponseCode||
|plugins|list[str]|Requested plugin||
|references|list[str]|References used while generating the answer|**DEPRECATED**|
|catalogs|list[int]|Requested Catalog|**DEPRECATED**|
|eventStatus|string|Event status||
|eventData|string|EventData||
|filterValidation|boolean|Filter success or not|**DEPRECATED**|
|successYn|boolean|Success or failure|**DEPRECATED**|
|reasoning_content|string|추론 과정||
|processing_content|list|스트리밍 일경우 중간 처리 과정||
|content_references|list|References used while generating the answer||


## 

GET /openapi/chat/v1/all-models

사용자 포털에서 권한을 가진 모델(Text, I2T, T2I)을 API로 조회할 수 있습니다.

Text : 대화모델

I2T : Image To Text 모델

T2I : Text To Image 모델

Header

|Field|Type|Required|Description|Value|
|---|---|---|---|---|
|Content-Type|string|optional|Type of content|application/json|
|x-generative-ai-client|string|required|Client authentication information|ex) eyJXXX|
|x-openapi-token|string|required|OpenAPI Token information|ex) Bearer eyJXXX|
|x-generative-ai-user-email|string|optional|Portal user email|ex) kim.samsung@samsung.com|

Response

|Field|Type|Description|Value|
|---|---|---|---|
|modelId|String|Model Id||
|name|list|Model Name|[<br><br>{<br><br>"languageCode": "ko",<br><br>"content": "모델명"<br><br>}<br><br>]|
|descrption|list|Model Description|[<br><br>{<br><br>"languageCode": "ko",<br><br>"content": "설명"<br><br>}<br><br>]|
|modelName|String|Model Name|**DEPRECATED**|
|modelLabel.en|String|English model Label|**DEPRECATED**|
|modelLabel.ko|String|Korean model Label|**DEPRECATED**|
|modelDescription.en|String|Model Description en|**DEPRECATED**|
|modelDescription.ko|String|Model Description ko|**DEPRECATED**|
|types|list|Model Type|["TEXT"]<br><br>TEXT : 대화모델<br><br>I2T(ImageToText) : 이미지 분석모델<br><br>T2I(TextToImage) : 이미지 생성모델|

> 호출 예시 (python)

import requests
YOUR_CLIENT_KEY = ""
YOUR_PASS_KEY = ""
ENDPOINT_URL = ""
YOUR_EMAIL = ""
headers = {
  "x-generative-ai-client": YOUR_CLIENT_KEY,
  "x-openapi-token": YOUR_PASS_KEY,
  "x-generative-ai-user-email": YOUR_EMAIL
}
api_endpoint_url = f"{ENDPOINT_URL}/openapi/chat/v1/all-models"
response=requests.get(
    api_endpoint_url,
    headers=headers
)
# 응답 반환
print(response.json())

## 

POST /openapi/chat/v1/messages-with-models

사용자 입력에 대한 대한 모델의 응답(대화, 이미지 생성, 이미지분석)을 생성합니다.

Header

|Field|Type|Required|Description|Value|
|---|---|---|---|---|
|Content-Type|string|optional|Type of content|multipart/form-data|
|x-generative-ai-client|string|required|Client authentication information|ex) eyJXXX|
|x-openapi-token|string|required|OpenAPI Token information|ex) Bearer eyJXXX|
|x-generative-ai-user-email|string|optional|Portal user email|ex)kim.samsung@samsung.com|

Request

※ 이미지 분석 모델(I2T) 을 사용할 때에는 1개의 파일만 지원합니다.

|Field|Type|Required|Description|Value|
|---|---|---|---|---|
|llmId|int|optional|LLM Id (default: basic LLM)|**DEPRECATED**|
|llmName|string|optional [Deprecated]|LLM Name (default basic LLM)|**DEPRECATED**|
|modelIds|list|required|model id list<br><br> <br><br>**이미지 생성시**<br><br>**- TEXT, T2I 모델 필요**<br><br>**이미지 분석시**<br><br>**- TEXT, I2T 모델 필요**|ex) ["0196f1fc-2858-70a9-a232-74dbddb971d0","0196f1fc-2858-70a9-a232-74dbddb971232"]|
|contents|list[string]|required|contents|ex) [“Hello”]|
|isStream|boolean|optional|Stream or not (default: True)|ex) False / True|
|llmConfig|object|optional|LLM Config info|Properties 참고|
|systemPrompt|string|optional|System prompt for LLM to use|ex) 예시 참고|
|files|list|optional|Upload file||
|messageConfig|object|optional|T2I Image Size(Only Flux Model)|ex) {"width":64,"height":64}|

... (이하 원문 그대로)

# 

1.3FAQ

(원문 그대로)
