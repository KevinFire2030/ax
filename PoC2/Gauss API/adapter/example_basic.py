from __future__ import annotations

import json

from dotenv import load_dotenv

from gauss_client import GaussClient, load_config_from_env


def main() -> None:
    load_dotenv()
    client = GaussClient(load_config_from_env())

    # 1) models
    models = client.get_models()
    print("[models] count=", len(models) if isinstance(models, list) else type(models))

    # 2) basic chat
    resp = client.messages(contents=["안녕하세요. 연결 테스트입니다."], is_stream=False)
    print("[chat] responseCode=", resp.get("responseCode"), "status=", resp.get("status"))
    print("[chat] content=", resp.get("content"))

    # 3) JSON forcing example
    prompt = (
        "반드시 JSON만 출력해. 스키마: {\"ok\": true|false, \"reason\": string}. "
        "질문: '이 호출이 정상인가?'"
    )
    text = client.generate_text(prompt)
    print("[json raw text]", text)

    # If you expect strict JSON, use generate_json():
    # data = client.generate_json(prompt)
    # print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
