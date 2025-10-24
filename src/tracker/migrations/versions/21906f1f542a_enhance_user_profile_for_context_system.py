"""enhance_user_profile_for_context_system

Revision ID: 21906f1f542a
Revises: 3d67267873c5
Create Date: 2025-10-22 18:20:46.167629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21906f1f542a'
down_revision: Union[str, Sequence[str], None] = '3d67267873c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old columns from user_profiles if they exist
    with op.batch_alter_table('user_profiles', schema=None) as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column('nickname', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('preferred_tone', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('context_depth', sa.String(length=20), nullable=False, server_default='basic'))
        batch_op.add_column(sa.Column('work_info_encrypted', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('financial_info_encrypted', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('goals_encrypted', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('lifestyle_encrypted', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('calming_activities', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('baseline_energy', sa.Integer(), nullable=False, server_default='5'))
        batch_op.add_column(sa.Column('detected_patterns_encrypted', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('reminder_preferences', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('last_monthly_checkin', sa.Date(), nullable=True))
        
        # Drop old columns that are being replaced
        try:
            batch_op.drop_column('financial_personality')
            batch_op.drop_column('typical_income_range')
            batch_op.drop_column('debt_situation')
            batch_op.drop_column('money_stressors')
            batch_op.drop_column('money_wins')
            batch_op.drop_column('work_style')
            batch_op.drop_column('side_hustle_status')
            batch_op.drop_column('career_goals')
            batch_op.drop_column('work_challenges')
            batch_op.drop_column('stress_pattern')
            batch_op.drop_column('coping_mechanisms')
            batch_op.drop_column('priorities')
            batch_op.drop_column('recurring_themes')
            batch_op.drop_column('celebration_moments')
            batch_op.drop_column('ongoing_challenges')
            batch_op.drop_column('short_term_goals')
            batch_op.drop_column('long_term_aspirations')
            batch_op.drop_column('recent_growth')
            batch_op.drop_column('feedback_preferences')
        except Exception:
            # Columns might not exist in all databases
            pass


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('user_profiles', schema=None) as batch_op:
        # Add back old columns
        batch_op.add_column(sa.Column('financial_personality', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('typical_income_range', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('debt_situation', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('money_stressors', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('money_wins', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('work_style', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('side_hustle_status', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('career_goals', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('work_challenges', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('stress_pattern', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('coping_mechanisms', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('priorities', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('recurring_themes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('celebration_moments', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('ongoing_challenges', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('short_term_goals', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('long_term_aspirations', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('recent_growth', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('feedback_preferences', sa.String(length=500), nullable=True))
        
        # Drop new columns
        batch_op.drop_column('last_monthly_checkin')
        batch_op.drop_column('reminder_preferences')
        batch_op.drop_column('detected_patterns_encrypted')
        batch_op.drop_column('baseline_energy')
        batch_op.drop_column('calming_activities')
        batch_op.drop_column('lifestyle_encrypted')
        batch_op.drop_column('goals_encrypted')
        batch_op.drop_column('financial_info_encrypted')
        batch_op.drop_column('work_info_encrypted')
        batch_op.drop_column('context_depth')
        batch_op.drop_column('preferred_tone')
        batch_op.drop_column('nickname')
