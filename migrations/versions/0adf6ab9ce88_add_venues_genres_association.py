"""Add venues-genres association

Revision ID: 0adf6ab9ce88
Revises: be68cb0bfcc1
Create Date: 2020-05-13 20:32:40.271903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0adf6ab9ce88'
down_revision = 'be68cb0bfcc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venue_genres',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'genre_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('venue_genres')
    # ### end Alembic commands ###