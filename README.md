from openai import OpenAI

client = OpenAI(
    api_key="你的-API-Key",  # 替换成你复制的 sk-xxx
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
)

print(response.choices[0].message.content)
