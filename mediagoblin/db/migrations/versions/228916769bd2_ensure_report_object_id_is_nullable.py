"""ensure Report.object_id is nullable

Revision ID: 228916769bd2
Revises: 3145accb8fe3
Create Date: 2016-02-29 18:54:37.295185

"""

# revision identifiers, used by Alembic.
revision = '228916769bd2'
down_revision = '3145accb8fe3'

from alembic import op
from sqlalchemy import MetaData
from mediagoblin.db.migration_tools import inspect_table

def upgrade():
    """
    This ensures that the Report.object_id field is nullable, it seems for a
    short period of time it could have been NOT NULL but was fixed later.
    """
    db = op.get_bind()
    metadata = MetaData(bind=db)
    report_table = inspect_table(metadata, "core__reports")

    # Check if the field has nullable on
    object_id_field = report_table.columns["object_id"]
    if object_id_field.nullable != True:
        # We have to alter this.
        object_id_field.alter(nullable=True)

def downgrade():
    pass
