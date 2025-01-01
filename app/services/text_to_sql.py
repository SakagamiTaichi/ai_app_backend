from dataclasses import Field
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from openai import BaseModel
from app.schemas.personal_information import PersonalInformationResponse
from app.core.config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.language_models import BaseLanguageModel

from app.schemas.text_to_sql import TableData
    
class TextToSQLService:
    def __init__(self):
        self.db = SQLDatabase.from_uri(settings.DATABASE_URL)
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
        )
    def get_text_to_sql(self,input: str) -> TableData:

        # SQL文を実行するツール
        execute_query = QuerySQLDataBaseTool(db=self.db)

        # SQL文を生成するチェイン
        write_query:str = create_custom_sql_query_chain(self.llm, self.db, input)

        # クエリを実行
        response = execute_query.invoke({"query": write_query})

        return self._convert_to_structured_output(
            table_info=self.db.get_table_info(),
            raw_result=response,
            sql_query=write_query,
            original_input=input
        )
    
    def _convert_to_structured_output(
        self, 
        table_info: str,
        raw_result: List[tuple], 
        sql_query: str, 
        original_input: str
    ) -> TableData:
        # 構造化出力用のプロンプトテンプレート
        template = """
あなたはデータベースの結果をフロントエンド用に整形する専門家です。
以下のデータとコンテキストから、適切な形式のレスポンスを生成してください。

テーブルの情報: {table_info}
ユーザーの入力: {original_input}
実行されたSQL: {sql_query}
クエリの結果: {raw_result}

以下の形式で結果を整形してください：

class Column(BaseModel):
    //テーブルのカラムを表現するモデル
    field: str = Field(description="カラム名")
    headerName: str = Field(description="カラムのヘッダー名")
    width: int = Field(description="カラムに必要と思われる幅")

class TableData(BaseModel):
    //テーブル形式のデータを表現するモデル
    columns: List[Column] = Field(description="テーブルのカラム名のリスト")
    rows: List[Dict[str, Any]] = Field(description="各行のデータを含む辞書のリスト")

```

結果は必ずこの形式に従ってください。
"""
        # プロンプトの作成と実行
        prompt = ChatPromptTemplate.from_template(template)
        
        format_chain = (
            prompt 
            | self.llm.with_structured_output(TableData)
        )
        
        # 構造化データの生成
        structured_output = format_chain.invoke({
            "table_info": table_info,
            "original_input": original_input,
            "sql_query": sql_query,
            "raw_result": str(raw_result)
        })
        
        return structured_output        

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