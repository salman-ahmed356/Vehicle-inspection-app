"""Increase expertise feature status column length

Revision ID: increase_status_length
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'increase_status_length'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Increase the status column length from 50 to 255 characters
    op.alter_column('expertise_features', 'status',
                    existing_type=sa.String(50),
                    type_=sa.String(255),
                    existing_nullable=True)

def downgrade():
    # Revert back to 50 characters
    op.alter_column('expertise_features', 'status',
                    existing_type=sa.String(255),
                    type_=sa.String(50),
                    existing_nullable=True)