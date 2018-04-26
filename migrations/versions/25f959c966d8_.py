"""empty message

Revision ID: 25f959c966d8
Revises: fa67e8808702
Create Date: 2018-04-25 10:52:58.792250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25f959c966d8'
down_revision = 'fa67e8808702'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quantity_check',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=True),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quantity_check_goods',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('goods_id', sa.Integer(), nullable=True),
    sa.Column('quantity_check_id', sa.Integer(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('count_check', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['goods_id'], ['goodsed.id'], ),
    sa.ForeignKeyConstraint(['quantity_check_id'], ['quantity_check.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('quantity_check_goods')
    op.drop_table('quantity_check')
    # ### end Alembic commands ###
