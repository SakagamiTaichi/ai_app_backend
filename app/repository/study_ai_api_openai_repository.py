from langchain_core.language_models.chat_models import (
    BaseChatModel,
)

from langchain_core.prompts import ChatPromptTemplate

from app.domain.userAnswer.ai_evaluation_value_object import AIEvaluationValueObject
from app.domain.userAnswer.study_ai_api_repository import StudyAiApiRepository


class StudyAIAPIOpenAIRepository(StudyAiApiRepository):
    """"""

    def __init__(self, llm: BaseChatModel):
        self.llm: BaseChatModel = llm

    async def get_ai_evaluation(
        self, question: str, userAnswer: str
    ) -> AIEvaluationValueObject:
        """AIによってクイズを採点する。"""
        #  "1. Include 2-3 exchanges between speakers (conversation rounds)\n"
        prompt = ChatPromptTemplate.from_template(
            "あなたは優秀な英語の教師です。\n"
            "与えられた問題に対するユーザーの回答を採点してください。\n"
            "採点には以下の要素を含めてください。\n"
            "1. スコア（0点から100点）\n"
            "2. 模範解答\n"
            "3. 日本語のフィードバックコメント（良かった点、改善が必要な点を日本語で教えてください。）\n"
            "問題: {question}\n"
            "ユーザーの回答: {userAnswer}"
        )

        chain = prompt | self.llm.with_structured_output(AIEvaluationValueObject)
        evaluation = chain.invoke({"question": question, "userAnswer": userAnswer})

        return AIEvaluationValueObject(
            score=evaluation.score,  # type: ignore
            modelAnswer=evaluation.modelAnswer,  # type: ignore
            feedback=evaluation.feedback,  # type: ignore
        )
