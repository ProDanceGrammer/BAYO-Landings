"""Initial migration - create tables

Revision ID: 001
Revises:
Create Date: 2026-04-27 08:44:40.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create affiliates table
    op.create_table(
        'affiliates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_affiliates_id'), 'affiliates', ['id'], unique=False)

    # Create offers table
    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offers_id'), 'offers', ['id'], unique=False)

    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=False),
        sa.Column('offer_id', sa.Integer(), nullable=False),
        sa.Column('affiliate_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['affiliate_id'], ['affiliates.id'], ),
        sa.ForeignKeyConstraint(['offer_id'], ['offers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_affiliate_id'), 'leads', ['affiliate_id'], unique=False)
    op.create_index(op.f('ix_leads_created_at'), 'leads', ['created_at'], unique=False)
    op.create_index(op.f('ix_leads_id'), 'leads', ['id'], unique=False)
    op.create_index(op.f('ix_leads_offer_id'), 'leads', ['offer_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_leads_offer_id'), table_name='leads')
    op.drop_index(op.f('ix_leads_id'), table_name='leads')
    op.drop_index(op.f('ix_leads_created_at'), table_name='leads')
    op.drop_index(op.f('ix_leads_affiliate_id'), table_name='leads')
    op.drop_table('leads')
    op.drop_index(op.f('ix_offers_id'), table_name='offers')
    op.drop_table('offers')
    op.drop_index(op.f('ix_affiliates_id'), table_name='affiliates')
    op.drop_table('affiliates')
