"""Initial schema with all 11 tables

Revision ID: a18031e1652d
Revises: 
Create Date: 2026-07-16 23:26:22.257047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a18031e1652d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    # IMPORTANT: create_type=False prevents SQLAlchemy from auto-creating
    # the type when the enum is used in a column definition. We create it
    # explicitly with .create() instead, giving us full control.
    quotation_status_enum = postgresql.ENUM(
        'draft', 'sent', 'approved', 'rejected', 'cancelled',
        name='quotation_status',
        create_type=False
    )
    quotation_status_enum.create(op.get_bind(), checkfirst=True)

    job_status_enum = postgresql.ENUM(
        'pending', 'measuring', 'in_production', 'ready_for_installation',
        'installed', 'completed', 'cancelled',
        name='job_status',
        create_type=False
    )
    job_status_enum.create(op.get_bind(), checkfirst=True)

    payment_type_enum = postgresql.ENUM(
        'deposit', 'production', 'final',
        name='payment_type',
        create_type=False
    )
    payment_type_enum.create(op.get_bind(), checkfirst=True)

    payment_method_enum = postgresql.ENUM(
        'cash', 'bank_transfer', 'instapay', 'cheque', 'other',
        name='payment_method',
        create_type=False
    )
    payment_method_enum.create(op.get_bind(), checkfirst=True)

    payment_status_enum = postgresql.ENUM(
        'pending', 'paid', 'overdue', 'cancelled',
        name='payment_status',
        create_type=False
    )
    payment_status_enum.create(op.get_bind(), checkfirst=True)

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=False),
        sa.Column('alternative_phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('location_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_categories table
    op.create_table(
        'product_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['product_categories.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)

    # Create quotations table
    op.create_table(
        'quotations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('quotation_number', sa.String(length=50), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quotation_date', sa.Date(), nullable=False),
        sa.Column('status', quotation_status_enum, nullable=False, server_default='draft'),
        sa.Column('total_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text("'0.00'")),
        sa.Column('discount', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text("'0.00'")),
        sa.Column('final_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text("'0.00'")),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quotation_number')
    )
    op.create_index(op.f('ix_quotations_customer_id'), 'quotations', ['customer_id'], unique=False)
    op.create_index(op.f('ix_quotations_quotation_number'), 'quotations', ['quotation_number'], unique=True)

    # Create quotation_items table
    op.create_table(
        'quotation_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('quotation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.SmallInteger(), nullable=False, server_default=sa.text('1')),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text("'0.00'")),
        sa.Column('total_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text("'0.00'")),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['quotation_id'], ['quotations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quotation_items_product_id'), 'quotation_items', ['product_id'], unique=False)
    op.create_index(op.f('ix_quotation_items_quotation_id'), 'quotation_items', ['quotation_id'], unique=False)

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('quotation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', job_status_enum, nullable=False, server_default='pending'),
        sa.Column('measurement_date', sa.Date(), nullable=True),
        sa.Column('production_start', sa.Date(), nullable=True),
        sa.Column('production_end', sa.Date(), nullable=True),
        sa.Column('installation_date', sa.Date(), nullable=True),
        sa.Column('delivery_date', sa.Date(), nullable=True),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['quotation_id'], ['quotations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quotation_id')
    )
    op.create_index(op.f('ix_jobs_quotation_id'), 'jobs', ['quotation_id'], unique=True)

    # Create measurements table
    op.create_table(
        'measurements',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('measurement_number', sa.SmallInteger(), nullable=False, server_default=sa.text('1')),
        sa.Column('visit_date', sa.Date(), nullable=True),
        sa.Column('measured_by', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_measurements_job_id'), 'measurements', ['job_id'], unique=False)

    # Create measurement_items table
    op.create_table(
        'measurement_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('measurement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quotation_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('room_name', sa.String(length=100), nullable=True),
        sa.Column('piece_number', sa.String(length=100), nullable=True),
        sa.Column('width', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('height', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('quantity', sa.SmallInteger(), nullable=False, server_default=sa.text('1')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['measurement_id'], ['measurements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quotation_item_id'], ['quotation_items.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_measurement_items_measurement_id'), 'measurement_items', ['measurement_id'], unique=False)
    op.create_index(op.f('ix_measurement_items_quotation_item_id'), 'measurement_items', ['quotation_item_id'], unique=False)

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_order', sa.SmallInteger(), nullable=False),
        sa.Column('payment_type', payment_type_enum, nullable=False),
        sa.Column('payment_method', payment_method_enum, nullable=False),
        sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default=sa.text("'0.00'")),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text("'0.00'")),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('paid_date', sa.Date(), nullable=True),
        sa.Column('status', payment_status_enum, nullable=False, server_default='pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_job_id'), 'payments', ['job_id'], unique=False)

    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_job_id'), 'activity_logs', ['job_id'], unique=False)

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_report_date'), 'reports', ['report_date'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_index(op.f('ix_reports_report_date'), table_name='reports')
    op.drop_table('reports')

    op.drop_index(op.f('ix_activity_logs_job_id'), table_name='activity_logs')
    op.drop_table('activity_logs')

    op.drop_index(op.f('ix_payments_job_id'), table_name='payments')
    op.drop_table('payments')

    op.drop_index(op.f('ix_measurement_items_quotation_item_id'), table_name='measurement_items')
    op.drop_index(op.f('ix_measurement_items_measurement_id'), table_name='measurement_items')
    op.drop_table('measurement_items')

    op.drop_index(op.f('ix_measurements_job_id'), table_name='measurements')
    op.drop_table('measurements')

    op.drop_index(op.f('ix_jobs_quotation_id'), table_name='jobs')
    op.drop_table('jobs')

    op.drop_index(op.f('ix_quotation_items_quotation_id'), table_name='quotation_items')
    op.drop_index(op.f('ix_quotation_items_product_id'), table_name='quotation_items')
    op.drop_table('quotation_items')

    op.drop_index(op.f('ix_quotations_quotation_number'), table_name='quotations')
    op.drop_index(op.f('ix_quotations_customer_id'), table_name='quotations')
    op.drop_table('quotations')

    op.drop_index(op.f('ix_products_category_id'), table_name='products')
    op.drop_table('products')

    op.drop_table('product_categories')
    op.drop_table('customers')

    # Drop enum types
    sa.Enum(name='payment_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='payment_method').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='payment_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='job_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='quotation_status').drop(op.get_bind(), checkfirst=True)
