"""add google_id and nullable password_hash for OAuth

Revision ID: add_google_oauth
Revises: 0732e53269a0
Create Date: 2026-02-11

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_google_oauth'
down_revision = '0732e53269a0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash', existing_type=sa.String(255), nullable=True)
        batch_op.add_column(sa.Column('google_id', sa.String(255), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_google_id'), ['google_id'], unique=True)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_google_id'), table_name='users')
        batch_op.drop_column('google_id')
        batch_op.alter_column('password_hash', existing_type=sa.String(255), nullable=False)
