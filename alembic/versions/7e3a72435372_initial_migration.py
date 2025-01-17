"""Initial migration

Revision ID: 7e3a72435372
Revises: 
Create Date: 2024-11-18 21:35:10.554844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e3a72435372'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coords',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('levels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('winter', sa.String(), nullable=True),
    sa.Column('summer', sa.String(), nullable=True),
    sa.Column('autumn', sa.String(), nullable=True),
    sa.Column('spring', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fam', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('otc', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('pereval_added',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('coord_id', sa.Integer(), nullable=False),
    sa.Column('level_id', sa.Integer(), nullable=True),
    sa.Column('beauty_title', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('other_titles', sa.String(), nullable=True),
    sa.Column('connect', sa.String(), nullable=True),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('new', 'pending', 'accepted', 'rejected', name='status'), nullable=True),
    sa.ForeignKeyConstraint(['coord_id'], ['coords.id'], ),
    sa.ForeignKeyConstraint(['level_id'], ['levels.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pereval_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pereval_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['pereval_id'], ['pereval_added.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pereval_images')
    op.drop_table('pereval_added')
    op.drop_table('users')
    op.drop_table('levels')
    op.drop_table('coords')
    # ### end Alembic commands ###
