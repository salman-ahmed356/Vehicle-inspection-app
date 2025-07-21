"""Add report_id to expertise_reports

Revision ID: e08be89e2b9e
Revises: 81044d8c04fa
Create Date: 2025-07-21 19:08:54.477767
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e08be89e2b9e'
down_revision = '81044d8c04fa'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Drop obsolete column on company in batch mode
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.drop_column('my_business_address_link')

    # 2) Make branch.company_id non-nullable (SQLite needs batch)
    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.alter_column(
            'company_id',
            existing_type=sa.INTEGER(),
            nullable=False
        )
    op.create_index(
        op.f('ix_branch_company_id'),
        'branch', ['company_id'],
        unique=False
    )

    # 3) Add report_id to expertise_reports with a default for existing rows
    op.add_column(
        'expertise_reports',
        sa.Column('report_id', sa.Integer(),
                  nullable=False,
                  server_default='1')
    )
    op.create_index(
        op.f('ix_expertise_reports_report_id'),
        'expertise_reports', ['report_id'],
        unique=False
    )
    op.create_foreign_key(
        'fk_expertise_reports_report_id',
        'expertise_reports', 'report',
        ['report_id'], ['id']
    )
    # Remove the server_default now that existing rows are populated
    with op.batch_alter_table('expertise_reports', schema=None) as batch_op:
        batch_op.alter_column(
            'report_id',
            existing_type=sa.INTEGER(),
            server_default=None
        )

    # 4) Index on staff.branch_id
    op.create_index(
        op.f('ix_staff_branch_id'),
        'staff', ['branch_id'],
        unique=False
    )


def downgrade():
    # 4) Drop staff.branch_id index
    op.drop_index(op.f('ix_staff_branch_id'), table_name='staff')

    # 3) Remove report_id from expertise_reports
    with op.batch_alter_table('expertise_reports', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_expertise_reports_report_id',
            type_='foreignkey'
        )
        batch_op.drop_column('report_id')
    op.drop_index(
        op.f('ix_expertise_reports_report_id'),
        table_name='expertise_reports'
    )

    # 2) Revert branch.company_id to nullable
    op.drop_index(op.f('ix_branch_company_id'), table_name='branch')
    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.alter_column(
            'company_id',
            existing_type=sa.INTEGER(),
            nullable=True
        )

    # 1) Re-add company.my_business_address_link
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('my_business_address_link',
                      sa.VARCHAR(length=255),
                      nullable=True)
        )
