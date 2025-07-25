"""models.pyの変更を反映

Revision ID: 26925ff832fd
Revises: 696490ef5f6d
Create Date: 2025-07-13 08:11:27.225283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '26925ff832fd'
down_revision: Union[str, None] = '696490ef5f6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_table('learning_histories',
    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('learning_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('date', 'user_id')
    )
    op.create_index(op.f('ix_learning_histories_user_id'), 'learning_histories', ['user_id'], unique=False)
    op.create_table('recall_cards',
    sa.Column('recall_card_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('question', sa.String(), nullable=False, comment='質問'),
    sa.Column('answer', sa.String(), nullable=False, comment='答案'),
    sa.Column('correct_point', sa.Integer(), nullable=False, comment='正解ポイント'),
    sa.Column('review_deadline', sa.DateTime(timezone=True), nullable=False, comment='復習期限'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='作成日時'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('recall_card_id')
    )
    op.create_index(op.f('ix_recall_cards_user_id'), 'recall_cards', ['user_id'], unique=False)
    op.create_table('conversation_test_scores',
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('test_number', sa.Integer(), nullable=False),
    sa.Column('test_score', sa.Float(), nullable=False),
    sa.Column('is_pass', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('conversation_id', 'test_number')
    )
    op.create_table('messages',
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('message_order', sa.Integer(), nullable=False),
    sa.Column('speaker_number', sa.Integer(), nullable=False),
    sa.Column('message_en', sa.String(), nullable=False),
    sa.Column('message_ja', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('conversation_id', 'message_order')
    )
    op.create_table('message_test_scores',
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('test_number', sa.Integer(), nullable=False),
    sa.Column('message_order', sa.Integer(), nullable=False),
    sa.Column('score', sa.Float(), nullable=False),
    sa.Column('user_answer', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id', 'test_number'], ['conversation_test_scores.conversation_id', 'conversation_test_scores.test_number'], ),
    sa.PrimaryKeyConstraint('conversation_id', 'test_number', 'message_order')
    )
    # 外部キー制約のあるテーブルを正しい順序で削除
    op.drop_table('en_message_test_scores')
    op.drop_table('en_messages')
    op.drop_table('en_conversation_test_scores')
    op.drop_index(op.f('ix_en_conversations_user_id'), table_name='en_conversations')
    op.drop_table('en_conversations')
    op.drop_index(op.f('ix_en_learning_histories_user_id'), table_name='en_learning_histories')
    op.drop_table('en_learning_histories')
    op.drop_index(op.f('ix_en_recall_cards_user_id'), table_name='en_recall_cards')
    op.drop_table('en_recall_cards')
    # quizzes テーブルに model_answer カラムを追加（既存データがある場合の対応）
    op.add_column('quizzes', sa.Column('model_answer', sa.String(length=300), nullable=True, comment='模範解答'))
    # 既存データにデフォルト値を設定
    op.execute("UPDATE quizzes SET model_answer = '未設定' WHERE model_answer IS NULL")
    # NOT NULL制約を追加
    op.alter_column('quizzes', 'model_answer', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('quizzes', 'model_answer')
    op.create_table('en_recall_cards',
    sa.Column('recall_card_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('question', sa.VARCHAR(), autoincrement=False, nullable=False, comment='質問'),
    sa.Column('answer', sa.VARCHAR(), autoincrement=False, nullable=False, comment='答案'),
    sa.Column('correct_point', sa.INTEGER(), autoincrement=False, nullable=False, comment='正解ポイント'),
    sa.Column('review_deadline', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False, comment='復習期限'),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False, comment='作成日時'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('en_recall_cards_user_id_fkey')),
    sa.PrimaryKeyConstraint('recall_card_id', name=op.f('en_recall_cards_pkey'))
    )
    op.create_index(op.f('ix_en_recall_cards_user_id'), 'en_recall_cards', ['user_id'], unique=False)
    op.create_table('en_conversation_test_scores',
    sa.Column('conversation_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('test_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('test_score', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('is_pass', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['en_conversations.id'], name='en_conversation_test_scores_conversation_id_fkey'),
    sa.PrimaryKeyConstraint('conversation_id', 'test_number', name='en_conversation_test_scores_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('en_messages',
    sa.Column('conversation_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('message_order', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('speaker_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('message_en', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('message_ja', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['en_conversations.id'], name=op.f('en_messages_conversation_id_fkey')),
    sa.PrimaryKeyConstraint('conversation_id', 'message_order', name=op.f('en_messages_pkey'))
    )
    op.create_table('en_conversations',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='en_conversations_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='en_conversations_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index(op.f('ix_en_conversations_user_id'), 'en_conversations', ['user_id'], unique=False)
    op.create_table('en_message_test_scores',
    sa.Column('conversation_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('test_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('message_order', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('score', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('user_answer', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['conversation_id', 'test_number'], ['en_conversation_test_scores.conversation_id', 'en_conversation_test_scores.test_number'], name=op.f('en_message_test_scores_conversation_id_test_number_fkey')),
    sa.PrimaryKeyConstraint('conversation_id', 'test_number', 'message_order', name=op.f('en_message_test_scores_pkey'))
    )
    op.create_table('en_learning_histories',
    sa.Column('date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('learning_time', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('en_learning_histories_user_id_fkey')),
    sa.PrimaryKeyConstraint('date', 'user_id', name=op.f('en_learning_histories_pkey'))
    )
    op.create_index(op.f('ix_en_learning_histories_user_id'), 'en_learning_histories', ['user_id'], unique=False)
    op.drop_table('message_test_scores')
    op.drop_table('messages')
    op.drop_table('conversation_test_scores')
    op.drop_index(op.f('ix_recall_cards_user_id'), table_name='recall_cards')
    op.drop_table('recall_cards')
    op.drop_index(op.f('ix_learning_histories_user_id'), table_name='learning_histories')
    op.drop_table('learning_histories')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_table('conversations')
    # ### end Alembic commands ###
