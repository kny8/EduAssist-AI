"""add chat_id to relevant_content

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-03-16 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add the new column
    op.add_column('relevant_content', sa.Column('chat_id', sa.BigInteger(), nullable=True))
    
    # Add the foreign key
    op.create_foreign_key(
        'fk_relevant_content_chat',
        'relevant_content',
        'chats',
        ['chat_id'],
        ['id']
    )

    # Update existing records if any
    op.execute("""
        UPDATE relevant_content rc
        SET chat_id = cm.chat_id
        FROM chat_messages cm
        WHERE rc.chat_message_id = cm.id
    """)

    # Make the column not nullable
    op.alter_column('relevant_content', 'chat_id', nullable=False)

def downgrade():
    op.drop_constraint('fk_relevant_content_chat', 'relevant_content', type_='foreignkey')
    op.drop_column('relevant_content', 'chat_id') 