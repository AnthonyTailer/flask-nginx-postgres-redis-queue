"""empty message

Revision ID: 45c4ea852fb0
Revises: 
Create Date: 2018-09-29 02:54:31.866232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45c4ea852fb0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('birth', sa.Date(), nullable=False),
    sa.Column('sex', sa.String(length=1), nullable=True),
    sa.Column('school', sa.String(length=255), nullable=False),
    sa.Column('school_type', sa.String(length=3), nullable=True),
    sa.Column('caregiver', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=False),
    sa.Column('state', sa.String(length=2), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('revoked_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jti', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=120), nullable=False),
    sa.Column('fullname', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('type', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_fullname'), 'users', ['fullname'], unique=False)
    op.create_index(op.f('ix_users_type'), 'users', ['type'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('words',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(length=255), nullable=False),
    sa.Column('tip', sa.String(length=255), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('word')
    )
    op.create_table('evaluations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('type', sa.String(length=1), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('evaluator_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['evaluator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tasks',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_name'), 'tasks', ['name'], unique=False)
    op.create_table('transcription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transcription', sa.String(length=255), nullable=False),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('word_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transcription')
    )
    op.create_table('word_evaluation',
    sa.Column('evaluation_id', sa.Integer(), nullable=False),
    sa.Column('word_id', sa.Integer(), nullable=False),
    sa.Column('transcription_target_id', sa.Integer(), nullable=True),
    sa.Column('transcription_eval', sa.String(length=255), nullable=True),
    sa.Column('repetition', sa.Boolean(), nullable=True),
    sa.Column('audio_path', sa.String(length=255), nullable=False),
    sa.Column('ml_eval', sa.Boolean(), nullable=True),
    sa.Column('api_eval', sa.Boolean(), nullable=True),
    sa.Column('therapist_eval', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'], ),
    sa.ForeignKeyConstraint(['transcription_target_id'], ['transcription.id'], ),
    sa.ForeignKeyConstraint(['word_id'], ['words.id'], ),
    sa.PrimaryKeyConstraint('evaluation_id', 'word_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('word_evaluation')
    op.drop_table('transcription')
    op.drop_index(op.f('ix_tasks_name'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('evaluations')
    op.drop_table('words')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_type'), table_name='users')
    op.drop_index(op.f('ix_users_fullname'), table_name='users')
    op.drop_table('users')
    op.drop_table('revoked_tokens')
    op.drop_table('patients')
    # ### end Alembic commands ###