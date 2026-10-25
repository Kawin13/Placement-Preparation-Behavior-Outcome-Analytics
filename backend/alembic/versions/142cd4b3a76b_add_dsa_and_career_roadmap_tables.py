"""add_dsa_and_career_roadmap_tables

Revision ID: 142cd4b3a76b
Revises: 3c082f8c7dad
Create Date: 2026-10-25 22:45:13.868864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '142cd4b3a76b'
down_revision: Union[str, None] = '3c082f8c7dad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # Ensure DSA tables exist (creates them on fresh databases)
    if "dsa_topics" not in existing_tables:
        op.create_table(
            "dsa_topics",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("slug", sa.String(length=80), nullable=False),
            sa.Column("name", sa.String(length=150), nullable=False),
            sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_dsa_topics_slug"), "dsa_topics", ["slug"], unique=True)

    if "dsa_problems" not in existing_tables:
        op.create_table(
            "dsa_problems",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("problem_number", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=150), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("difficulty", sa.String(length=20), server_default="MEDIUM", nullable=False),
            sa.Column("topic_id", sa.UUID(), nullable=True),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("constraints", sa.Text(), nullable=True),
            sa.Column("input_format", sa.Text(), nullable=True),
            sa.Column("output_format", sa.Text(), nullable=True),
            sa.Column("examples", sa.JSON(), nullable=False),
            sa.Column("starter_code", sa.JSON(), nullable=False),
            sa.Column("expected_time_complexity", sa.String(length=50), nullable=True),
            sa.Column("expected_space_complexity", sa.String(length=50), nullable=True),
            sa.Column("hints", sa.JSON(), nullable=False),
            sa.Column("editorial", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=30), server_default="PUBLISHED", nullable=False),
            sa.Column("is_problem_of_the_day", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("sheet_tags", sa.JSON(), nullable=False),
            sa.Column("author_id", sa.UUID(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.CheckConstraint("difficulty IN ('EASY', 'MEDIUM', 'HARD')", name="chk_dsa_problem_difficulty"),
            sa.CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')", name="chk_dsa_problem_status"),
            sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["topic_id"], ["dsa_topics.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_dsa_problems_problem_number"), "dsa_problems", ["problem_number"], unique=True)
        op.create_index(op.f("ix_dsa_problems_slug"), "dsa_problems", ["slug"], unique=True)
        op.create_index(op.f("ix_dsa_problems_topic_id"), "dsa_problems", ["topic_id"], unique=False)

    if "dsa_test_cases" not in existing_tables:
        op.create_table(
            "dsa_test_cases",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("problem_id", sa.UUID(), nullable=False),
            sa.Column("input_data", sa.Text(), nullable=False),
            sa.Column("expected_output", sa.Text(), nullable=False),
            sa.Column("is_hidden", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
            sa.Column("time_limit_ms", sa.Integer(), server_default="2000", nullable=False),
            sa.Column("memory_limit_mb", sa.Integer(), server_default="256", nullable=False),
            sa.ForeignKeyConstraint(["problem_id"], ["dsa_problems.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_dsa_test_cases_problem_id"), "dsa_test_cases", ["problem_id"], unique=False)

    if "dsa_submissions" not in existing_tables:
        op.create_table(
            "dsa_submissions",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("user_id", sa.UUID(), nullable=False),
            sa.Column("problem_id", sa.UUID(), nullable=False),
            sa.Column("language", sa.String(length=20), nullable=False),
            sa.Column("code", sa.Text(), nullable=False),
            sa.Column("verdict", sa.String(length=30), nullable=False),
            sa.Column("runtime_ms", sa.Integer(), nullable=True),
            sa.Column("memory_kb", sa.Integer(), nullable=True),
            sa.Column("test_cases_passed", sa.Integer(), server_default="0", nullable=False),
            sa.Column("total_test_cases", sa.Integer(), server_default="0", nullable=False),
            sa.Column("failed_test_case_index", sa.Integer(), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("stdout_sample", sa.Text(), nullable=True),
            sa.Column("hints_viewed", sa.Integer(), server_default="0", nullable=False),
            sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["problem_id"], ["dsa_problems.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_dsa_submissions_problem_id"), "dsa_submissions", ["problem_id"], unique=False)
        op.create_index(op.f("ix_dsa_submissions_user_id"), "dsa_submissions", ["user_id"], unique=False)

    if "dsa_user_progress" not in existing_tables:
        op.create_table(
            "dsa_user_progress",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("user_id", sa.UUID(), nullable=False),
            sa.Column("problem_id", sa.UUID(), nullable=False),
            sa.Column("status", sa.String(length=20), server_default="UNSOLVED", nullable=False),
            sa.Column("attempts_count", sa.Integer(), server_default="0", nullable=False),
            sa.Column("best_runtime_ms", sa.Integer(), nullable=True),
            sa.Column("solved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_attempted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.CheckConstraint("status IN ('UNSOLVED', 'ATTEMPTED', 'SOLVED')", name="chk_dsa_progress_status"),
            sa.ForeignKeyConstraint(["problem_id"], ["dsa_problems.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "problem_id", name="uq_dsa_user_problem_progress"),
        )
        op.create_index(op.f("ix_dsa_user_progress_problem_id"), "dsa_user_progress", ["problem_id"], unique=False)
        op.create_index(op.f("ix_dsa_user_progress_user_id"), "dsa_user_progress", ["user_id"], unique=False)
    op.create_table('career_paths',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('target_role', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_paths_code'), 'career_paths', ['code'], unique=True)
    op.create_table('roadmap_subjects',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('career_path_id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('icon', sa.String(length=50), nullable=False),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['career_path_id'], ['career_paths.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roadmap_subjects_career_path_id'), 'roadmap_subjects', ['career_path_id'], unique=False)
    op.create_table('roadmap_topics',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('subject_id', sa.UUID(), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('learning_objectives', sa.Text(), nullable=True),
    sa.Column('difficulty', sa.String(length=20), nullable=False),
    sa.Column('estimated_minutes', sa.Integer(), nullable=False),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.UUID(), nullable=True),
    sa.Column('dsa_topic_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("difficulty IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')", name='chk_roadmap_topic_difficulty'),
    sa.ForeignKeyConstraint(['dsa_topic_id'], ['dsa_topics.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['subject_id'], ['roadmap_subjects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roadmap_topics_dsa_topic_id'), 'roadmap_topics', ['dsa_topic_id'], unique=False)
    op.create_index(op.f('ix_roadmap_topics_skill_id'), 'roadmap_topics', ['skill_id'], unique=False)
    op.create_index(op.f('ix_roadmap_topics_slug'), 'roadmap_topics', ['slug'], unique=False)
    op.create_index(op.f('ix_roadmap_topics_subject_id'), 'roadmap_topics', ['subject_id'], unique=False)
    op.create_table('student_behavior_events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('entity_id', sa.String(length=100), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=False),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("event_type IN ('SESSION_START', 'SESSION_COMPLETE', 'SESSION_ABANDONED', 'PRACTICE_ATTEMPT', 'MISTAKE_REVIEWED', 'RESOURCE_OPENED', 'RESOURCE_COMPLETED', 'CODING_SUBMIT', 'TOPIC_SWITCH')", name='chk_behavior_event_type'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_behavior_events_created_at'), 'student_behavior_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_student_behavior_events_event_type'), 'student_behavior_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_student_behavior_events_user_id'), 'student_behavior_events', ['user_id'], unique=False)
    op.create_table('student_career_goals',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('career_path_id', sa.UUID(), nullable=False),
    sa.Column('target_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('ACTIVE', 'COMPLETED', 'PAUSED')", name='chk_career_goal_status'),
    sa.ForeignKeyConstraint(['career_path_id'], ['career_paths.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_career_goals_career_path_id'), 'student_career_goals', ['career_path_id'], unique=False)
    op.create_index(op.f('ix_student_career_goals_user_id'), 'student_career_goals', ['user_id'], unique=True)
    op.create_table('roadmap_subtopics',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('topic_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['topic_id'], ['roadmap_topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roadmap_subtopics_topic_id'), 'roadmap_subtopics', ['topic_id'], unique=False)
    op.create_table('student_topic_progress',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('topic_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('completion_percentage', sa.Integer(), nullable=False),
    sa.Column('questions_attempted', sa.Integer(), nullable=False),
    sa.Column('questions_correct', sa.Integer(), nullable=False),
    sa.Column('coding_problems_solved', sa.Integer(), nullable=False),
    sa.Column('resources_completed', sa.Integer(), nullable=False),
    sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'NEEDS_REVISION')", name='chk_student_topic_status'),
    sa.ForeignKeyConstraint(['topic_id'], ['roadmap_topics.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'topic_id', name='uq_user_topic_progress')
    )
    op.create_index(op.f('ix_student_topic_progress_topic_id'), 'student_topic_progress', ['topic_id'], unique=False)
    op.create_index(op.f('ix_student_topic_progress_user_id'), 'student_topic_progress', ['user_id'], unique=False)
    op.create_table('learning_resources',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('topic_id', sa.UUID(), nullable=False),
    sa.Column('subtopic_id', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('resource_type', sa.String(length=30), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('external_url', sa.String(length=500), nullable=True),
    sa.Column('difficulty', sa.String(length=20), nullable=False),
    sa.Column('estimated_duration_min', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('author_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("difficulty IN ('EASY', 'MEDIUM', 'HARD')", name='chk_resource_difficulty'),
    sa.CheckConstraint("resource_type IN ('ARTICLE', 'VIDEO', 'DOCUMENT', 'EXERCISE', 'CHEATSHEET')", name='chk_resource_type'),
    sa.CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')", name='chk_resource_status'),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['subtopic_id'], ['roadmap_subtopics.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['topic_id'], ['roadmap_topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_resources_subtopic_id'), 'learning_resources', ['subtopic_id'], unique=False)
    op.create_index(op.f('ix_learning_resources_topic_id'), 'learning_resources', ['topic_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_learning_resources_topic_id'), table_name='learning_resources')
    op.drop_index(op.f('ix_learning_resources_subtopic_id'), table_name='learning_resources')
    op.drop_table('learning_resources')
    op.drop_index(op.f('ix_student_topic_progress_user_id'), table_name='student_topic_progress')
    op.drop_index(op.f('ix_student_topic_progress_topic_id'), table_name='student_topic_progress')
    op.drop_table('student_topic_progress')
    op.drop_index(op.f('ix_roadmap_subtopics_topic_id'), table_name='roadmap_subtopics')
    op.drop_table('roadmap_subtopics')
    op.drop_index(op.f('ix_student_career_goals_user_id'), table_name='student_career_goals')
    op.drop_index(op.f('ix_student_career_goals_career_path_id'), table_name='student_career_goals')
    op.drop_table('student_career_goals')
    op.drop_index(op.f('ix_student_behavior_events_user_id'), table_name='student_behavior_events')
    op.drop_index(op.f('ix_student_behavior_events_event_type'), table_name='student_behavior_events')
    op.drop_index(op.f('ix_student_behavior_events_created_at'), table_name='student_behavior_events')
    op.drop_table('student_behavior_events')
    op.drop_index(op.f('ix_roadmap_topics_subject_id'), table_name='roadmap_topics')
    op.drop_index(op.f('ix_roadmap_topics_slug'), table_name='roadmap_topics')
    op.drop_index(op.f('ix_roadmap_topics_skill_id'), table_name='roadmap_topics')
    op.drop_index(op.f('ix_roadmap_topics_dsa_topic_id'), table_name='roadmap_topics')
    op.drop_table('roadmap_topics')
    op.drop_index(op.f('ix_roadmap_subjects_career_path_id'), table_name='roadmap_subjects')
    op.drop_table('roadmap_subjects')
    op.drop_index(op.f('ix_career_paths_code'), table_name='career_paths')
    op.drop_table('career_paths')
    # ### end Alembic commands ###
