"""Remove state city models

Revision ID: 93722d1f6db9
Revises: d89d6af9abfc
Create Date: 2020-05-13 21:21:05.223731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93722d1f6db9'
down_revision = 'd89d6af9abfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('city')
    op.drop_table('state')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('state',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('state_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('state_code', sa.VARCHAR(length=2), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='state_pkey'),
    sa.UniqueConstraint('state_code', name='state_state_code_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('city',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('state_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], name='city_state_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='city_pkey')
    )
    # ### end Alembic commands ###