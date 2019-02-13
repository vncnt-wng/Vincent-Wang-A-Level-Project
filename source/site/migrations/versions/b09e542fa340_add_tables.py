"""add tables

Revision ID: b09e542fa340
Revises: 
Create Date: 2019-02-12 14:10:38.071620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b09e542fa340'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prediction',
    sa.Column('dateTime', sa.DateTime(), nullable=False),
    sa.Column('pred15', sa.Float(), nullable=True),
    sa.Column('pred30', sa.Float(), nullable=True),
    sa.Column('pred60', sa.Float(), nullable=True),
    sa.Column('pred120', sa.Float(), nullable=True),
    sa.Column('pred240', sa.Float(), nullable=True),
    sa.Column('pred480', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('dateTime')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('emailHash', sa.String(length=32), nullable=True),
    sa.Column('apiKey', sa.String(length=16), nullable=True),
    sa.Column('dateJoined', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_apiKey'), 'user', ['apiKey'], unique=True)
    op.create_index(op.f('ix_user_emailHash'), 'user', ['emailHash'], unique=True)
    op.create_table('request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dateTime', sa.DateTime(), nullable=True),
    sa.Column('served', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('request')
    op.drop_index(op.f('ix_user_emailHash'), table_name='user')
    op.drop_index(op.f('ix_user_apiKey'), table_name='user')
    op.drop_table('user')
    op.drop_table('prediction')
    # ### end Alembic commands ###