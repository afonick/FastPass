"""Add cascade delete to relationships

Revision ID: 259039c9cd8f
Revises: 8bdae53422b9
Create Date: 2024-11-24 01:48:49.422768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '259039c9cd8f'
down_revision: Union[str, None] = '8bdae53422b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('pereval_images_pereval_id_fkey', 'pereval_images', type_='foreignkey')
    op.create_foreign_key(None, 'pereval_images', 'pereval_added', ['pereval_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'pereval_images', type_='foreignkey')
    op.create_foreign_key('pereval_images_pereval_id_fkey', 'pereval_images', 'pereval_added', ['pereval_id'], ['id'])
    # ### end Alembic commands ###
