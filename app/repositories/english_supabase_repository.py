from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from supabase import Client

from app.repositories.english_repository import EnglishRepository
from app.schemas.english_chat import Conversation, Message

class EnglishSupabaseRepository(EnglishRepository):
    """SupabaseをバックエンドとしたEnglishRepositoryの実装"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def get_conversation_sets(self, user_id: str) -> List[Conversation]:
        """特定ユーザーの会話セットの一覧を取得する"""
        try:
            response = self.client.table('en_conversations') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .execute()
    
            # レスポンスから履歴リストを作成
            sets = [
                Conversation(
                    id=UUID(record['id']),
                    user_id=UUID(record['user_id']),
                    title=record['title'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                )
                for record in response.data
            ]

            return sets
        except Exception as e:
            print(f"Error fetching conversation sets: {str(e)}")
            raise
    
    async def get_messages(self, conversation_id: UUID, user_id: str) -> List[Message]:
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
                Message(
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
    
    async def create_message(self, message: Message) -> Message:
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