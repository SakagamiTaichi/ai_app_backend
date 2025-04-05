from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from supabase import Client

from app.domain.practice.conversation import ConversationEntity
from app.domain.practice.test_result import MessageScore, TestResult
from app.domain.practice.practice_repository import PracticeRepository
from app.model.practice.practice import Conversation, MessageResponse

class PracticeSupabaseRepository(PracticeRepository):
    """SupabaseをバックエンドとしたEnglishRepositoryの実装"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def get_conversations(self, user_id: str) -> List[ConversationEntity]:
        """特定ユーザーの会話セットの一覧を取得する"""
        try:
            response = self.client.table('en_conversations') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .execute()
    
            # レスポンスから履歴リストを作成
            sets = [
                ConversationEntity(
                    id=UUID(record['id']),
                    user_id=UUID(record['user_id']),
                    title=record['title'],
                    order=record['order'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'),)
                )
                for record in response.data
            ]

            return sets
        except Exception as e:
            print(f"Error fetching conversations: {str(e)}")
            raise
    
    async def get_conversation(self, conversation_id: UUID, user_id: str) -> List[MessageResponse]:
        """特定の会話セットに属するメッセージを取得する（アクセス権の確認あり）"""
        try:
            # まず会話セットの所有者を確認
            owner_check = self.client.table('en_conversations') \
                .select('user_id') \
                .eq('id', str(conversation_id)) \
                .execute()
                
            # 会話セットが存在しない、または所有者が異なる場合
            if not owner_check.data or str(owner_check.data[0]['user_id']) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="このリソースにアクセスする権限がありません"
                )
            
            # メッセージを取得
            response = self.client.table('en_messages') \
                .select('*') \
                .eq('conversation_id', str(conversation_id)) \
                .order('message_order') \
                .execute()
    
            # レスポンスからメッセージリストを作成
            messages = [
                MessageResponse(
                    conversation_id=UUID(record['conversation_id']),
                    message_order=record['message_order'],
                    speaker_number=record['speaker_number'],
                    message_en=record['message_en'],
                    message_ja=record['message_ja'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                )
                for record in response.data
            ]

            return messages
        except HTTPException:
            # HTTPExceptionはそのまま伝播
            raise
        except Exception as e:
            print(f"Error fetching messages: {str(e)}")
            raise
    
    async def create_message(self, message: MessageResponse) -> MessageResponse:
        """メッセージを作成する"""
        try:
            # Messageオブジェクトから辞書を作成
            message_data = {
                'conversation_id': str(message.conversation_id),
                'message_order': message.message_order,
                'speaker_number': message.speaker_number,
                'message_en': message.message_en,
                'message_ja': message.message_ja,
                'created_at': message.created_at.isoformat()
            }
            
            # データを挿入
            response = self.client.table('en_messages').insert(message_data).execute()
            
            if not response.data:
                raise Exception("Failed to create message")
                
            return message
        except Exception as e:
            print(f"Error creating message: {str(e)}")
            raise
    
    async def create_conversation_set(self, conversation_set: Conversation) -> Conversation:
        """会話セットを作成する"""
        try:
            # ConversationSetオブジェクトから辞書を作成
            set_data = {
                'id': str(conversation_set.id),
                'user_id': str(conversation_set.user_id),
                'title': conversation_set.title,
                'created_at': conversation_set.created_at.isoformat()
            }
            
            # データを挿入
            response = self.client.table('en_conversations').insert(set_data).execute()
            
            if not response.data:
                raise Exception("Failed to create conversation set")
                
            return conversation_set
        except Exception as e:
            print(f"Error creating conversation set: {str(e)}")
            raise

    async def save_test_result(self, test_result: TestResult) -> TestResult:
        """テスト結果をデータベースに保存する"""
        try:
            # 会話テストスコアを保存
            conversation_score_data = {
                'conversation_id': str(test_result.conversation_id),
                'test_number': test_result.test_number,
                'test_score': test_result.overall_score,
                'is_pass': test_result.is_passing,
                'created_at': test_result.created_at.isoformat()
            }
            
            score_response = self.client.table('en_conversation_test_scores').insert(conversation_score_data).execute()
            
            # メッセージごとのスコアを保存
            if test_result.message_scores:
                message_score_data = [
                    {
                        'conversation_id': str(test_result.conversation_id),
                        'test_number': test_result.test_number,
                        'message_order': score.message_order,
                        'score': score.score
                    }
                    for score in test_result.message_scores
                ]
                
                self.client.table('en_message_test_scores').insert(message_score_data).execute()
            
            return test_result
            
        except Exception as e:
            print(f"Error saving test results: {str(e)}")
            raise
    
    async def get_latest_test_result(self, conversation_id: UUID) -> Optional[TestResult]:
        """指定された会話の最新のテスト結果を取得する"""
        try:
            # 最新のテスト結果を取得
            response = self.client.table('en_conversation_test_scores') \
                .select('*') \
                .eq('conversation_id', str(conversation_id)) \
                .order('test_number', desc=True) \
                .limit(1) \
                .execute()
            
            if not response.data:
                return None
            
            last_test = response.data[0]
            test_number = last_test['test_number']
            
            # 対応するメッセージスコアを取得
            msg_response = self.client.table('en_message_test_scores') \
                .select('*') \
                .eq('conversation_id', str(conversation_id)) \
                .eq('test_number', test_number) \
                .execute()
            
            # メッセージスコアのリストを作成
            message_scores = []
            for item in msg_response.data:
                # メッセージの詳細を取得（正解内容など）
                message_response = self.client.table('en_messages') \
                    .select('*') \
                    .eq('conversation_id', str(conversation_id)) \
                    .eq('message_order', item['message_order']) \
                    .limit(1) \
                    .execute()
                
                if message_response.data:
                    msg = message_response.data[0]
                    score = MessageScore(
                        message_order=item['message_order'],
                        score=item['score'],
                        is_correct=item['score'] >= 90.0,
                        user_answer="",  # データベースには保存されていない
                        correct_answer=msg['message_en']
                    )
                    message_scores.append(score)
            
            # TestResultエンティティを作成して返す
            return TestResult(
                conversation_id=UUID(last_test['conversation_id']),
                test_number=last_test['test_number'],
                message_scores=message_scores,
                created_at=datetime.fromisoformat(last_test['created_at'].replace('Z', '+00:00'))
            )
        except Exception as e:
            print(f"Error fetching last test result: {str(e)}")
            return None