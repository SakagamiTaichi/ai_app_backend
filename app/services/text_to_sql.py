from dataclasses import Field
from typing import Any, Dict, List, Type
from langchain_openai import ChatOpenAI
from openai import BaseModel
from app.schemas.personal_information import PersonalInformation
from app.core.config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.language_models import BaseLanguageModel
from supabase import create_client
from app.schemas.text_to_sql import Column, PersonalInformationResponse, TableData
    
class TextToSQLService:
    def __init__(self):
        self.db = SQLDatabase.from_uri(settings.DATABASE_URL)
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
        )
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def get_init_data(self) -> PersonalInformationResponse:
        # 10行だけ取得する
        response = self.client.table('personal_information').select('*').limit(10).execute()

        # レスポンスから個人情報を取得
        informations = [
                PersonalInformation(
                    id=record['id'],
                    name=record['name'],
                    name_kana=record['name_kana'],
                    sex=record['sex'],
                    phone_number=record['phone_number'],
                    mail=record['mail'],
                    postcode=record['postcode'],
                    address=record['address'],
                    birthday=record['birthday'],
                    age=record['age'],
                    blood_type=record['blood_type']
                )
                for record in response.data
            ]

        return PersonalInformationResponse(informations=informations)
    
    def get_text_to_sql(self,input: str) -> TableData:


        # SQL文を生成するチェイン
        write_query:str = create_custom_sql_query_chain(self.llm, self.db, input)
        # SQL文を実行するツール
        execute_query = QuerySQLDataBaseTool(db=self.db)

        # クエリを実行
        response = execute_query.invoke({"query": write_query})

        return self._convert_to_structured_output(
            raw_result=response,
            sql_query=write_query,
        )
    
    def _convert_to_structured_output(self,raw_result: str, sql_query: str) -> TableData:
        # 文字列からPythonのデータ構造に変換
        data = eval(raw_result)
        
        # データが空の場合の処理
        if not data:
            return TableData(
                sql=sql_query,
                columns=[],
                rows=[]
            )
        
        # 最初の行からカラム数を取得して動的にカラムを生成
        num_columns = len(data[0])
        columns = [
            Column(
                field=f"column_{i}",  # プログラムでの参照用の名前
                headerName=f"列{i+1}",  # 表示用の名前
                width=150  # 日本語テキストを考慮して幅を広めに設定
            )
            for i in range(num_columns)
        ]
        
        # 各行のデータをカラムとマッピング
        rows = [
            {f"column_{i}": value for i, value in enumerate(row)}
            for row in data
        ]
        
        return TableData(
            sql=sql_query,
            columns=columns,
            rows=rows
        ) 

def create_custom_sql_query_chain(
    llm: BaseLanguageModel,
    db: SQLDatabase,
    input: str
) -> str:
    """Create a custom chain that generates SQL queries.

    Args:
        llm: The language model to use
        db: The SQLDatabase to generate the query for

    Returns:
        Generated SQL query as a string
    """
    # Get table information
    table_info = db.get_table_info()
    
    # Create a custom prompt template
    template = """あなたはSQLエキスパートです。以下の要件に従ってSQLクエリを生成してください：

1. クエリは必ずそのままで実行可能なものにしてください
2. 与えられたデータベースのテーブル情報のみを使用してください
3. 標準的なSQLの文法に従ってください
4. SQLクエリのみを出力してください。マークダウンのコードブロック(```)や説明文は含めないでください
5. クエリの前後に余分な空白や改行を含めないでください
6. クエリに変換することができない場合はレコード件数が0件になるようなクエリを作成してください

利用可能なテーブル情報:
{table_info}

ユーザーの質問: {input}

SQL: """

    prompt = ChatPromptTemplate.from_template(template)

    # Generate messages
    messages = prompt.format_messages(
        table_info=table_info,
        input=input
    )

    # Get response from LLM
    response = llm.invoke(messages)
    
    # Extract and clean the SQL query
    sql_query = response.content.strip()
    
    # Remove markdown code blocks if present
    sql_query = sql_query.replace('```sql', '').replace('```', '')
    
    # Remove any remaining whitespace and newlines from start/end
    sql_query = sql_query.strip()
    
    # Basic validation
    if not sql_query.lower().startswith(('select', 'with')):
        raise ValueError("Generated query must be a SELECT statement")
        
    return sql_query