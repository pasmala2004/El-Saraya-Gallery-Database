"""Foundation hardening: check constraints, unique keys, and query indexes.

Revision ID: b2c4e8f91a03
Revises: a18031e1652d
Create Date: 2026-07-18 14:45:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b2c4e8f91a03"
down_revision: Union[str, None] = "a18031e1652d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- customers ---
    op.create_index("ix_customers_phone_number", "customers", ["phone_number"], unique=False)
    op.create_index("ix_customers_full_name", "customers", ["full_name"], unique=False)

    # --- products ---
    op.create_unique_constraint(
        "uq_products_category_id_name",
        "products",
        ["category_id", "name"],
    )

    # --- quotations ---
    op.create_check_constraint(
        "ck_quotations_total_price_nonneg",
        "quotations",
        "total_price >= 0",
    )
    op.create_check_constraint(
        "ck_quotations_discount_nonneg",
        "quotations",
        "discount >= 0",
    )
    op.create_check_constraint(
        "ck_quotations_final_price_nonneg",
        "quotations",
        "final_price >= 0",
    )
    op.create_index("ix_quotations_status", "quotations", ["status"], unique=False)
    op.create_index("ix_quotations_quotation_date", "quotations", ["quotation_date"], unique=False)

    # --- quotation_items ---
    op.create_check_constraint(
        "ck_quotation_items_quantity_positive",
        "quotation_items",
        "quantity > 0",
    )
    op.create_check_constraint(
        "ck_quotation_items_unit_price_nonneg",
        "quotation_items",
        "unit_price >= 0",
    )
    op.create_check_constraint(
        "ck_quotation_items_total_price_nonneg",
        "quotation_items",
        "total_price >= 0",
    )

    # --- jobs ---
    op.create_index("ix_jobs_status", "jobs", ["status"], unique=False)

    # --- measurements ---
    op.create_unique_constraint(
        "uq_measurements_job_id_measurement_number",
        "measurements",
        ["job_id", "measurement_number"],
    )
    op.create_check_constraint(
        "ck_measurements_measurement_number_positive",
        "measurements",
        "measurement_number > 0",
    )

    # --- measurement_items ---
    op.create_check_constraint(
        "ck_measurement_items_quantity_positive",
        "measurement_items",
        "quantity > 0",
    )
    op.create_check_constraint(
        "ck_measurement_items_width_nonneg",
        "measurement_items",
        "width IS NULL OR width >= 0",
    )
    op.create_check_constraint(
        "ck_measurement_items_height_nonneg",
        "measurement_items",
        "height IS NULL OR height >= 0",
    )

    # --- payments ---
    op.create_unique_constraint(
        "uq_payments_job_id_payment_order",
        "payments",
        ["job_id", "payment_order"],
    )
    op.create_check_constraint(
        "ck_payments_payment_order_positive",
        "payments",
        "payment_order > 0",
    )
    op.create_check_constraint(
        "ck_payments_amount_nonneg",
        "payments",
        "amount >= 0",
    )
    op.create_check_constraint(
        "ck_payments_percentage_range",
        "payments",
        "percentage >= 0 AND percentage <= 100",
    )
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)
    op.create_index("ix_payments_due_date", "payments", ["due_date"], unique=False)

    # --- activity_logs ---
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"], unique=False)
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_activity_logs_action", table_name="activity_logs")
    op.drop_index("ix_activity_logs_created_at", table_name="activity_logs")

    op.drop_index("ix_payments_due_date", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_constraint("ck_payments_percentage_range", "payments", type_="check")
    op.drop_constraint("ck_payments_amount_nonneg", "payments", type_="check")
    op.drop_constraint("ck_payments_payment_order_positive", "payments", type_="check")
    op.drop_constraint("uq_payments_job_id_payment_order", "payments", type_="unique")

    op.drop_constraint("ck_measurement_items_height_nonneg", "measurement_items", type_="check")
    op.drop_constraint("ck_measurement_items_width_nonneg", "measurement_items", type_="check")
    op.drop_constraint("ck_measurement_items_quantity_positive", "measurement_items", type_="check")

    op.drop_constraint(
        "ck_measurements_measurement_number_positive",
        "measurements",
        type_="check",
    )
    op.drop_constraint(
        "uq_measurements_job_id_measurement_number",
        "measurements",
        type_="unique",
    )

    op.drop_index("ix_jobs_status", table_name="jobs")

    op.drop_constraint("ck_quotation_items_total_price_nonneg", "quotation_items", type_="check")
    op.drop_constraint("ck_quotation_items_unit_price_nonneg", "quotation_items", type_="check")
    op.drop_constraint("ck_quotation_items_quantity_positive", "quotation_items", type_="check")

    op.drop_index("ix_quotations_quotation_date", table_name="quotations")
    op.drop_index("ix_quotations_status", table_name="quotations")
    op.drop_constraint("ck_quotations_final_price_nonneg", "quotations", type_="check")
    op.drop_constraint("ck_quotations_discount_nonneg", "quotations", type_="check")
    op.drop_constraint("ck_quotations_total_price_nonneg", "quotations", type_="check")

    op.drop_constraint("uq_products_category_id_name", "products", type_="unique")

    op.drop_index("ix_customers_full_name", table_name="customers")
    op.drop_index("ix_customers_phone_number", table_name="customers")
