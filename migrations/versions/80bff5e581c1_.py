"""empty message

Revision ID: 80bff5e581c1
Revises: 1a0cd191b12b
Create Date: 2021-02-20 09:59:19.238297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80bff5e581c1'
down_revision = '1a0cd191b12b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###