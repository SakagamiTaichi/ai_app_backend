
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from app.domain.practice.geneerated_conversation_value_object import GeneratedConversationValueObject, GeneratedMessageValueObject
from app.domain.practice.practice_api_repotiroy import PracticeApiRepository
from langchain_core.prompts import ChatPromptTemplate

class PracticeApiOpenAiRepository(PracticeApiRepository):
    """PostgreSQLを使用した練習機能のリポジトリ実装"""
    
    def __init__(self,llm : BaseChatModel):
        self.llm: BaseChatModel  = llm

    async def get_generated_conversation(self, user_phrase: str) -> GeneratedConversationValueObject:
        """AIによって生成された会話を取得する"""
        #  "1. Include 2-3 exchanges between speakers (conversation rounds)\n"
        prompt = ChatPromptTemplate.from_template(
            "Create a natural English conversation that includes the user's phrase\n"
            "The conversation should:\n"
            "1. Represent how native English speakers would naturally talk\n"
            "2. Include the target phrase in context, showing how it's commonly used\n"
            "3. Be presented with both English text and Japanese translations\n"
            "4. Here's an example of the format:\n"
            """{{
            "title": "ストレス解消法",
            "messages": [
              {{
                "message_en": "What's your way of relieving stress these days? I'm really into cooking and enjoying trying new recipes",
                "message_ja": "最近はどうやってストレス解消してるの？私は料理にハマっていて、新しいレシピを試すのが楽しいんだ。"
              }},
              {{
                "message_en": "That's cool! I've gotten really into hiking lately. There's something about being out in nature that just helps clear my head. What kind of things have you been cooking?",
                "message_ja": "いいね！僕は最近ハイキングにハマってるよ。自然の中にいると何だか頭がスッキリするんだ。どんな料理を作ってるの？"
              }},
              {{
                "message_en": "I've been exploring different Asian cuisines - made my first pad thai from scratch last week! It's nice to focus on following a recipe instead of thinking about work.",
                "message_ja": "いろんなアジア料理を試してるの - 先週は初めてパッタイを一から作ってみたわ！仕事のことを考える代わりにレシピに集中するのが良いのよね。"
              }},
              {{
                "message_en": "I get that completely. It's like you can't worry about deadlines when you're concentrating on not burning the noodles! Plus you get something delicious at the end.",
                "message_ja": "それ、すっごくわかる。麺を焦がさないように集中してると、締め切りのことなんて考えてる余裕ないもんね！しかも最後には美味しいものが出来上がるし。"
              }},
              {{
                "message_en": "Exactly! Though I've definitely had my share of kitchen disasters too. Last month I tried making macarons... let's just say they looked nothing like the picture!",
                "message_ja": "そうそう！でも私も料理の失敗はいっぱいあるわよ。先月マカロン作ってみたんだけど...写真とは似ても似つかないものができたの！"
              }}
            ]
            }}"""
            "user's phrase: {user_phrase}")
        
        chain = prompt | self.llm.with_structured_output(GeneratedConversationValueObject)
        generated_conversation = chain.invoke({"user_phrase": user_phrase})


        return GeneratedConversationValueObject(
            title=generated_conversation.title, # type: ignore
            messages=[
                GeneratedMessageValueObject(
                    message_en=message.message_en,
                    message_ja=message.message_ja
                )
                for message in generated_conversation.messages # type: ignore
            ]
        )