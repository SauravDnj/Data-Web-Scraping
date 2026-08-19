from sqlalchemy import BigInteger, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase

# Explicit, predictable constraint/index names instead of
# database-generated ones — required for Alembic autogenerate (T021)
# to produce stable migrations across runs.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Every table's `id` column should use this type. BIGINT everywhere
# per docs/04_DATABASE_DESIGN.md, but SQLite only auto-increments a
# primary key typed exactly INTEGER (not BIGINT) — this is
# SQLAlchemy's documented cross-dialect fix: real BIGINT on MySQL,
# plain INTEGER (still autoincrement-compatible) on SQLite, which is
# what this project's tests use in place of a live MySQL connection.
BigIntegerPK = BigInteger().with_variant(Integer(), "sqlite")
