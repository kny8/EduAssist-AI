"""add search results table

Revision ID: add_search_results_table
Revises: previous_revision_id
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_search_results_table'
down_revision = None  # Update this with your previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'search_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code_exercise_id', sa.Integer(), nullable=False),
        sa.Column('query', sa.String(), nullable=False),
        sa.Column('context', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('link', sa.String(), nullable=False),
        sa.Column('snippet', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('date', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('last_accessed', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['code_exercise_id'], ['code_exercises.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_search_results_query'), 'search_results', ['query'], unique=False)
    op.create_index(op.f('ix_search_results_code_exercise_id'), 'search_results', ['code_exercise_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_search_results_code_exercise_id'), table_name='search_results')
    op.drop_index(op.f('ix_search_results_query'), table_name='search_results')
    op.drop_table('search_results') 