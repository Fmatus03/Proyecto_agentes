from alembic import op
import sqlalchemy as sa

revision = '0001_brewmaster_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('rol', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_estado', 'users', ['estado'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    op.create_table('roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('estado', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_roles_estado', 'roles', ['estado'])
    op.create_index('ix_roles_created_at', 'roles', ['created_at'])

    op.create_table('permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(255), nullable=True),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('modulo', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_permissions_created_at', 'permissions', ['created_at'])

    op.create_table('role_permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('permission_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_role_permissions_created_at', 'role_permissions', ['created_at'])

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(255), nullable=True),
        sa.Column('entity', sa.String(255), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('detail', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    op.create_table('settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(255), nullable=True),
        sa.Column('value', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_settings_created_at', 'settings', ['created_at'])

    op.create_table('password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('token_hash', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_password_reset_tokens_created_at', 'password_reset_tokens', ['created_at'])


def downgrade():
    op.drop_index('ix_password_reset_tokens_created_at', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index('ix_settings_created_at', table_name='settings')
    op.drop_table('settings')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index('ix_role_permissions_created_at', table_name='role_permissions')
    op.drop_table('role_permissions')
    op.drop_index('ix_permissions_created_at', table_name='permissions')
    op.drop_table('permissions')
    op.drop_index('ix_roles_created_at', table_name='roles')
    op.drop_index('ix_roles_estado', table_name='roles')
    op.drop_table('roles')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_estado', table_name='users')
    op.drop_table('users')
