"""empty message

Revision ID: c9bf543e5769
Revises: f6766021dbf6
Create Date: 2022-04-09 09:50:28.922310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9bf543e5769'
down_revision = 'f6766021dbf6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'admin_members', ['username'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'admin_members', type_='unique')
    # ### end Alembic commands ###