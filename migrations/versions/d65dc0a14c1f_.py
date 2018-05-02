"""empty message

Revision ID: d65dc0a14c1f
Revises: 0307fcac75c6
Create Date: 2018-04-30 12:57:22.319895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd65dc0a14c1f'
down_revision = '0307fcac75c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sales', sa.Column('goods_id', sa.Integer(), nullable=True))
    op.add_column('stocks', sa.Column('goods_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stocks', 'goods_id')
    op.drop_column('sales', 'goods_id')
    # ### end Alembic commands ###
