"""Added Admin Database

Revision ID: 143b69fe59c0
Revises: 
Create Date: 2022-04-08 02:50:16.532584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '143b69fe59c0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=20), nullable=False),
    sa.Column('first_name', sa.String(length=20), nullable=False),
    sa.Column('middle_name', sa.String(length=20), nullable=False),
    sa.Column('last_name', sa.String(length=20), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin')
    # ### end Alembic commands ###
