from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)    

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "あなたは優秀なエンジニアです"},
        {"role": "user", "content": "こんにちは、ポリモーフィズムについて教えてください"},
    ],
)

print(response.choices[0].message.content)