"""add api_keys table

Revision ID: 002
Revises: 001
Create Date: 2026-03-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """创建 api_keys 表"""
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=True, index=True),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('api_key', sa.Text(), nullable=False),
        sa.Column('base_url', sa.String(255), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # 创建索引
    op.create_index('ix_api_keys_provider', 'api_keys', ['provider'])
    op.create_index('ix_api_keys_user_provider', 'api_keys', ['user_id', 'provider'])


def downgrade():
    """删除 api_keys 表"""
    op.drop_index('ix_api_keys_user_provider', table_name='api_keys')
    op.drop_index('ix_api_keys_provider', table_name='api_keys')
    op.drop_table('api_keys')
