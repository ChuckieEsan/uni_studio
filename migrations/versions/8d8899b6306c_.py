"""empty message

Revision ID: 8d8899b6306c
Revises: 5f9c9b10a313
Create Date: 2021-05-02 18:26:37.808431

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d8899b6306c'
down_revision = '5f9c9b10a313'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vote_info', sa.Column('show_raw_vote_on_voted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vote_info', 'show_raw_vote_on_voted')
    # ### end Alembic commands ###
