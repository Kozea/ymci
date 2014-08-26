from ymci.model import engine, Table
Table.metadata.drop_all(engine)
Table.metadata.create_all(engine)

from alembic.config import Config
from alembic import command
alembic_cfg = Config('alembic.ini')
command.stamp(alembic_cfg, 'head')
