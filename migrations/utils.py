from sqlalchemy.engine.reflection import Inspector
from alembic import op


def inspector():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    return inspector


def exists_table(table_name: str):
    tables = inspector().get_table_names()
    return table_name in tables


def not_exists_table(table_name: str):
    return not exists_table(table_name)


def has_index(table_name: str, index_name: str):
    indexes = inspector().get_indexes(table_name)
    indexes_names = map(lambda index: index["name"], indexes)
    return index_name in indexes_names


def has_not_index(table_name: str, index_name: str):
    return not has_index(table_name, index_name)


def exists_column(table_name: str, column_name: str):
    has_column = False
    for column in inspector().get_columns(table_name):
        if column_name not in column["name"]:
            continue
        has_column = True
    return has_column


def not_exists_column(table_name: str, column_name: str):
    return not exists_column(table_name, column_name)
