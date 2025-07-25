import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# モデルをインポート
from app.core.database import Base
from app.core.config import settings
from app.schema.models import Users  # type: ignore
import app.schema.models  # type: ignore
from app.schema.models import RecallCards  # type: ignore


# このパスを追加して、アプリケーションのモジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Alembic設定
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# SQLAlchemyのURLを環境変数から設定
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# ログの設定
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# メタデータに対象のモデルを追加
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# メタデータに対象のモデルを追加
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """アプリケーションの外でマイグレーションを実行する場合"""
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """アプリケーション内でマイグレーションを実行する場合（通常のケース）"""
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
