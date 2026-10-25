"""align dsa submission and progress columns

Revision ID: 287fe9a1b02c
Revises: 142cd4b3a76b
Create Date: 2026-10-25 23:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '287fe9a1b02c'
down_revision = '142cd4b3a76b'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if "dsa_submissions" in existing_tables:
        sub_cols = [c["name"] for c in inspector.get_columns("dsa_submissions")]
        if "hints_viewed" not in sub_cols:
            op.add_column("dsa_submissions", sa.Column("hints_viewed", sa.Integer(), server_default="0", nullable=False))
        if "submitted_at" not in sub_cols:
            if "created_at" in sub_cols:
                op.alter_column("dsa_submissions", "created_at", new_column_name="submitted_at")
            else:
                op.add_column("dsa_submissions", sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))

    if "dsa_user_progress" in existing_tables:
        prog_cols = [c["name"] for c in inspector.get_columns("dsa_user_progress")]
        if "best_runtime_ms" not in prog_cols:
            op.add_column("dsa_user_progress", sa.Column("best_runtime_ms", sa.Integer(), nullable=True))
        if "solved_at" not in prog_cols:
            if "first_solved_at" in prog_cols:
                op.alter_column("dsa_user_progress", "first_solved_at", new_column_name="solved_at")
            else:
                op.add_column("dsa_user_progress", sa.Column("solved_at", sa.DateTime(timezone=True), nullable=True))
        if "last_attempted_at" not in prog_cols:
            if "last_attempt_at" in prog_cols:
                op.alter_column("dsa_user_progress", "last_attempt_at", new_column_name="last_attempted_at")
            else:
                op.add_column("dsa_user_progress", sa.Column("last_attempted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
        
        # Ensure status constraint allows 'UNSOLVED'
        try:
            op.drop_constraint("chk_dsa_progress_status", "dsa_user_progress", type_="check")
        except Exception:
            pass
        try:
            op.create_check_constraint(
                "chk_dsa_progress_status",
                "dsa_user_progress",
                "status IN ('UNSOLVED', 'ATTEMPTED', 'SOLVED')"
            )
        except Exception:
            pass


def downgrade():
    pass
