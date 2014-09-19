from alembic import command
from alembic.config import Config


def upgrade():
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, "Automatic revision", autogenerate=True)
    command.upgrade(alembic_cfg, "head")
