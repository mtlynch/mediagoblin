"""initial revision

Revision ID: 52bf0ccbedc1
Revises: None
Create Date: 2015-11-07 17:00:28.191042
Description: This is an initial Alembic migration
"""

# revision identifiers, used by Alembic.
revision = '52bf0ccbedc1'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Well we already appear to have some of the core data, presumably because
    # this database precedes our alembic migrations with sqlalchemy-migrate, so
    # we can bail out early.
    if op.get_bind().engine.has_table("core__users"):
        return

    op.create_table(
        'core__clients',
        sa.Column('id', sa.Unicode(), nullable=True),
        sa.Column('secret', sa.Unicode(), nullable=False),
        sa.Column('expirey', sa.DateTime(), nullable=True),
        sa.Column('application_type', sa.Unicode(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('redirect_uri', sa.UnicodeText(),
                  nullable=True),
        sa.Column('logo_url', sa.Unicode(), nullable=True),
        sa.Column('application_name', sa.Unicode(), nullable=True),
        sa.Column('contacts', sa.UnicodeText(),
                  nullable=True),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'core__file_keynames',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'))

    op.create_table(
        'core__generators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('published', sa.DateTime(), nullable=True),
        sa.Column('updated', sa.DateTime(), nullable=True),
        sa.Column('object_type', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'core__generic_model_reference',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('obj_pk', sa.Integer(), nullable=False),
        sa.Column('model_type', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_type', 'obj_pk'))

    op.create_table(
        'core__locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=True),
        sa.Column('position', sa.UnicodeText(),
                  nullable=True),
        sa.Column('address', sa.UnicodeText(),
                  nullable=True),
        sa.PrimaryKeyConstraint('id'))

    # We should remove this in a future migration, though
    op.create_table(
        'core__migrations',
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('name'))

    op.create_table(
        'core__nonce_timestamps',
        sa.Column('nonce', sa.Unicode(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('nonce', 'timestamp'))

    op.create_table(
        'core__privileges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('privilege_name', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('privilege_name'))

    op.create_table(
        'core__tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'))

    op.create_table(
        'core__comment_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('added', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['comment_id'],
                                ['core__generic_model_reference.id']),
        sa.ForeignKeyConstraint(['target_id'],
                                ['core__generic_model_reference.id']),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'core__graveyard',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('public_id', sa.Unicode(), nullable=True),
        sa.Column('deleted', sa.DateTime(), nullable=False),
        sa.Column('object_type', sa.Unicode(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'],
                                ['core__generic_model_reference.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('public_id'))

    op.create_table(
        'core__users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Unicode(), nullable=True),
        sa.Column('bio', sa.UnicodeText(), nullable=True),
        sa.Column('name', sa.Unicode(), nullable=True),
        sa.Column('type', sa.Unicode(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('location', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['location'], ['core__locations.id']),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'core__activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('public_id', sa.Unicode(), nullable=True),
        sa.Column('actor', sa.Integer(), nullable=False),
        sa.Column('published', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('verb', sa.Unicode(), nullable=False),
        sa.Column('content', sa.Unicode(), nullable=True),
        sa.Column('title', sa.Unicode(), nullable=True),
        sa.Column('generator', sa.Integer(), nullable=True),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['actor'], ['core__users.id']),
        sa.ForeignKeyConstraint(['generator'], ['core__generators.id']),
        sa.ForeignKeyConstraint(['object_id'],
                                ['core__generic_model_reference.id']),
        sa.ForeignKeyConstraint(['target_id'],
                                ['core__generic_model_reference.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('public_id'))

    op.create_table(
        'core__collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('public_id', sa.Unicode(), nullable=True),
        sa.Column('title', sa.Unicode(), nullable=False),
        sa.Column('slug', sa.Unicode(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('description', sa.UnicodeText(), nullable=True),
        sa.Column('actor', sa.Integer(), nullable=False),
        sa.Column('num_items', sa.Integer(), nullable=True),
        sa.Column('type', sa.Unicode(), nullable=False),
        sa.Column('location', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['actor'], ['core__users.id']),
        sa.ForeignKeyConstraint(['location'], ['core__locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('actor', 'slug'),
        sa.UniqueConstraint('public_id'))

    op.create_index(
        op.f('ix_core__collections_created'),
        'core__collections', ['created'], unique=False)

    op.create_table(
        'core__local_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.Unicode(), nullable=False),
        sa.Column('email', sa.Unicode(), nullable=False),
        sa.Column('pw_hash', sa.Unicode(), nullable=True),
        sa.Column('wants_comment_notification', sa.Boolean(), nullable=True),
        sa.Column('wants_notifications', sa.Boolean(), nullable=True),
        sa.Column('license_preference', sa.Unicode(), nullable=True),
        sa.Column('uploaded', sa.Integer(), nullable=True),
        sa.Column('upload_limit', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['core__users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'))

    op.create_table(
        'core__media_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('public_id', sa.Unicode(), nullable=True),
        sa.Column('actor', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('content', sa.UnicodeText(), nullable=False),
        sa.Column('location', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['actor'], ['core__users.id']),
        sa.ForeignKeyConstraint(['location'], ['core__locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('public_id'))

    op.create_table(
        'core__media_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('public_id', sa.Unicode(), nullable=True),
        sa.Column('remote', sa.Boolean(), nullable=True),
        sa.Column('actor', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(), nullable=False),
        sa.Column('slug', sa.Unicode(), nullable=True),
        sa.Column('description', sa.UnicodeText(), nullable=True),
        sa.Column('media_type', sa.Unicode(), nullable=False),
        sa.Column('state', sa.Unicode(), nullable=False),
        sa.Column('license', sa.Unicode(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('location', sa.Integer(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('fail_error', sa.Unicode(), nullable=True),
        sa.Column('fail_metadata', sa.UnicodeText(), nullable=True),
        sa.Column('transcoding_progress', sa.SmallInteger(), nullable=True),
        sa.Column('queued_media_file', sa.Unicode(), nullable=True),
        sa.Column('queued_task_id', sa.Unicode(), nullable=True),
        sa.Column('media_metadata', sa.UnicodeText(), nullable=True),
        sa.ForeignKeyConstraint(['actor'], ['core__users.id']),
        sa.ForeignKeyConstraint(['location'], ['core__locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('actor', 'slug'),
        sa.UniqueConstraint('public_id'))

    op.create_index(
        op.f('ix_core__media_entries_actor'),
        'core__media_entries', ['actor'], unique=False)
    op.create_index(
        op.f('ix_core__media_entries_created'),
        'core__media_entries', ['created'], unique=False)

    op.create_table(
        'core__notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('seen', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['object_id'],
                                ['core__generic_model_reference.id']),
        sa.ForeignKeyConstraint(['user_id'], ['core__users.id']),
        sa.PrimaryKeyConstraint('id'))

    op.create_index(
        op.f('ix_core__notifications_seen'),
        'core__notifications', ['seen'], unique=False)

    op.create_index(
        op.f('ix_core__notifications_user_id'),
        'core__notifications', ['user_id'], unique=False)

    op.create_table(
        'core__privileges_users',
        sa.Column('user', sa.Integer(), nullable=False),
        sa.Column('privilege', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['privilege'], ['core__privileges.id']),
        sa.ForeignKeyConstraint(['user'], ['core__users.id']),
        sa.PrimaryKeyConstraint('user', 'privilege'))

    op.create_table(
        'core__remote_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webfinger', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['core__users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('webfinger'))

    op.create_table(
        'core__reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('report_content', sa.UnicodeText(), nullable=True),
        sa.Column('reported_user_id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('resolver_id', sa.Integer(), nullable=True),
        sa.Column('resolved', sa.DateTime(), nullable=True),
        sa.Column('result', sa.UnicodeText(), nullable=True),
        sa.Column('object_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['object_id'],
                                ['core__generic_model_reference.id']),
        sa.ForeignKeyConstraint(['reported_user_id'], ['core__users.id']),
        sa.ForeignKeyConstraint(['reporter_id'], ['core__users.id']),
        sa.ForeignKeyConstraint(['resolver_id'], ['core__users.id']),
        sa.PrimaryKeyConstraint('id'))
    op.create_table(
        'core__request_tokens',
        sa.Column('token', sa.Unicode(), nullable=False),
        sa.Column('secret', sa.Unicode(), nullable=False),
        sa.Column('client', sa.Unicode(), nullable=True),
        sa.Column('actor', sa.Integer(), nullable=True),
        sa.Column('used', sa.Boolean(), nullable=True),
        sa.Column('authenticated', sa.Boolean(), nullable=True),
        sa.Column('verifier', sa.Unicode(), nullable=True),
        sa.Column('callback', sa.Unicode(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['actor'], ['core__users.id']),
        sa.ForeignKeyConstraint(['client'], ['core__clients.id']),
        sa.PrimaryKeyConstraint('token'))

    op.create_table(
        'core__user_bans',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('reason', sa.UnicodeText(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['core__users.id']),
        sa.PrimaryKeyConstraint('user_id'))

    op.create_table(
        'core__access_tokens',
        sa.Column('token', sa.Unicode(), nullable=False),
        sa.Column('secret', sa.Unicode(), nullable=False),
        sa.Column('actor', sa.Integer(), nullable=True),
        sa.Column('request_token', sa.Unicode(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['actor'], ['core__users.id']),
        sa.ForeignKeyConstraint(['request_token'],
                                ['core__request_tokens.token']),
        sa.PrimaryKeyConstraint('token'))

    op.create_table(
        'core__attachment_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('filepath', sa.Unicode(),
                  nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id']),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'core__collection_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('collection', sa.Integer(), nullable=False),
        sa.Column('note', sa.UnicodeText(), nullable=True),
        sa.Column('added', sa.DateTime(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['collection'], ['core__collections.id']),
        sa.ForeignKeyConstraint(['object_id'],
                                ['core__generic_model_reference.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('collection', 'object_id'))

    op.create_index(
        op.f('ix_core__collection_items_object_id'), 'core__collection_items',
        ['object_id'], unique=False)

    op.create_table(
        'core__comment_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('media_entry_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notify', sa.Boolean(), nullable=False),
        sa.Column('send_email', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['media_entry_id'], ['core__media_entries.id']),
        sa.ForeignKeyConstraint(['user_id'], ['core__users.id']),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'core__media_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('tag', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id']),
        sa.ForeignKeyConstraint(['tag'], ['core__tags.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tag', 'media_entry'))

    op.create_index(
        op.f('ix_core__media_tags_media_entry'), 'core__media_tags',
        ['media_entry'], unique=False)

    op.create_index(
        op.f('ix_core__media_tags_tag'), 'core__media_tags',
        ['tag'], unique=False)

    op.create_table(
        'core__mediafiles',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('name_id', sa.SmallInteger(), nullable=False),
        sa.Column('file_path', sa.Unicode(), nullable=True),
        sa.Column('file_metadata', sa.UnicodeText(),
                  nullable=True),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id']),
        sa.ForeignKeyConstraint(['name_id'], ['core__file_keynames.id']),
        sa.PrimaryKeyConstraint('media_entry', 'name_id'))

    op.create_table(
        'core__processing_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('media_entry_id', sa.Integer(), nullable=False),
        sa.Column('callback_url', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['media_entry_id'], ['core__media_entries.id']),
        sa.PrimaryKeyConstraint('id'))

    op.create_index(
        op.f('ix_core__processing_metadata_media_entry_id'),
        'core__processing_metadata', ['media_entry_id'], unique=False)

def downgrade():
    # Downgrading from a first revision is nonsense.
    pass
