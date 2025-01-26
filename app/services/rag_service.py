from uuid import UUID
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from langchain_postgres import PGVector
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from supabase import create_client
from langchain_core.messages import HumanMessage, AIMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory

from app.schemas.rag import InformationResponse, InformationsResponse
from app.schemas.recipe import RecipeHistories

class RagService:

    def __init__(self):

        self.vector_store = PGVector(
            connection=settings.DATABASE_URL,
            embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
            collection_metadata={"description": "Document embeddings"},
            create_extension=False,
        )
        
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            streaming=True
        )
        
        self.prompt = ChatPromptTemplate.from_template('''
            以下の文脈だけを踏まえて質問に200文字程度で回答してください。
            
            文脈: """{context}"""
            
            質問：{question}
        ''')


    def _format_docs(self, docs):
        """Retrieved documents をフォーマットする"""
        return "\n\n".join(doc.page_content for doc in docs)

    def embedding_model(self, information: str) -> str:
        """情報をEmbeddingモデルに登録します
        
        Args:
            information (str): ベクトルストアに保存する情報テキスト
            
        Returns:
            str: 処理の結果を示すステータスメッセージ
        """
        # テキストをチャンクに分割する
        text_splitter = RecursiveCharacterTextSplitter(
            # デフォルトの区切り文字を使用
            separators=["\n\n", "\n", " ", ""],
            # チャンクサイズなどの追加パラメータは必要に応じて設定可能
            # 1つの文または短い段落が1チャンクになるよう設定
            chunk_size=100,
            # 短いテキストの場合、オーバーラップは最小限に
            chunk_overlap=10
        )
        
        # テキストを分割してチャンクのリストを取得
        chunks = text_splitter.split_text(information)
        
        # 分割したテキストをベクトルストアに追加
        try:
            self.vector_store.add_texts(chunks)
            return "Success"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_information(self) -> RecipeHistories:
        """過去に登録された情報の一覧を取得します"""
        try:
            # recipeテーブルから全レコードを取得（作成日時の降順）
            response = self.client.table('langchain_pg_embedding') \
                .select('*') \
                .execute()

            # レスポンスから履歴リストを作成
            histories = [
                InformationResponse(
                    id=UUID(record['id']),
                    document=record['document'],
                )
                for record in response.data
            ]

            return InformationsResponse(informations=histories)

        except Exception as e:
            print(f"Error fetching recipe histories: {str(e)}")
            raise

    async def  retriver(self, question: str) -> str:
        retriever = self.vector_store.as_retriever( search_type="mmr",
                                                    search_kwargs={
                                                        "k": 4,
                                                        "fetch_k": 20,     # より多くのドキュメントを検討
                                                        "lambda_mult": 0.3  # 多様性の重み付けを強く
                                                    }
                                                   )
        
        
        chain = (
            {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        output = chain.invoke(question)


        return output