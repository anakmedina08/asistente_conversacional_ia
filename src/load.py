from pathlib import Path
from datetime import datetime, date
import csv
import os

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    MetaData,
    Table,
    Text,
    inspect,
    text,
)

from connect_sql import engine


WRITE_MODE_MAP = {
    "append": "append",
    "truncate": "truncate",
    "replace": "replace",
}

INT32_MIN = -2147483648
INT32_MAX = 2147483647


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _qualified_table(schema: str | None, table: str) -> str:
    if schema:
        return f"{_quote_ident(schema)}.{_quote_ident(table)}"
    return _quote_ident(table)


def _resolve_table_name(table: str | None) -> str:
    if table:
        return table
    env_table = os.getenv("PG_TABLE")
    if env_table:
        return env_table
    raise ValueError("Table no definido. Usa table o PG_TABLE.")


def _resolve_schema(schema: str | None) -> str:
    return schema or os.getenv("PG_SCHEMA") or "public"


def _resolve_write_mode(write_mode: str | None) -> str:
    mode = (write_mode or os.getenv("PG_WRITE_MODE") or "append").lower()
    if mode not in WRITE_MODE_MAP:
        raise ValueError(
            "write_mode invalido. Usa: append, truncate, replace."
        )
    return mode


def _clean_value(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def _all_parse(values, parser) -> bool:
    for value in values:
        if value is None:
            continue
        try:
            parser(value)
        except Exception:
            return False
    return True


def _parse_int(value: str) -> int:
    return int(value)


def _parse_float(value: str) -> float:
    return float(value)


def _parse_datetime(value: str) -> datetime:
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    return datetime.fromisoformat(cleaned)


def _looks_like_date_only(value: str) -> bool:
    cleaned = value.strip()
    return len(cleaned) == 10 and cleaned[4] == "-" and cleaned[7] == "-"


def _parse_date(value: str) -> date:
    return date.fromisoformat(value.strip())


def _infer_int_column(values: list[str | None]):
    parsed = []
    for value in values:
        if value is None:
            continue
        try:
            parsed.append(_parse_int(value))
        except Exception:
            return None
    if not parsed:
        return Text(), _clean_value
    min_val = min(parsed)
    max_val = max(parsed)
    if INT32_MIN <= min_val <= INT32_MAX and INT32_MIN <= max_val <= INT32_MAX:
        col_type = Integer()
    else:
        col_type = BigInteger()
    return col_type, (lambda v: None if v is None else _parse_int(v))


def _infer_column(values: list[str | None]):
    if not values or all(v is None for v in values):
        return Text(), _clean_value

    inferred_int = _infer_int_column(values)
    if inferred_int is not None:
        return inferred_int

    if _all_parse(values, _parse_float):
        return Float(), (lambda v: None if v is None else _parse_float(v))

    if all(v is None or _looks_like_date_only(v) for v in values) and _all_parse(
        values, _parse_date
    ):
        return Date(), (lambda v: None if v is None else _parse_date(v))

    if _all_parse(values, _parse_datetime):
        return DateTime(), (lambda v: None if v is None else _parse_datetime(v))

    return Text(), _clean_value


def _read_csv_rows(csv_path: Path):
    with csv_path.open("r", newline="", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        if not reader.fieldnames:
            raise ValueError("CSV sin encabezados.")
        rows = []
        for row in reader:
            cleaned = {k: _clean_value(v) for k, v in row.items()}
            rows.append(cleaned)
    return reader.fieldnames, rows


def load_siniestros_to_postgres(
    csv_path: str,
    table: str | None = None,
    schema: str | None = None,
    write_mode: str | None = None,
    infer_types: bool = True,
    batch_size: int = 500,
) -> str:
    """
    Carga CSV limpio a Postgres.
    """
    if not csv_path:
        raise ValueError("csv_path es requerido.")

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    table_name = _resolve_table_name(table)
    schema = _resolve_schema(schema)
    write_mode = _resolve_write_mode(write_mode)
    qualified = _qualified_table(schema, table_name)

    columns, rows = _read_csv_rows(path)

    converters = {}
    column_defs = []
    if infer_types:
        values_by_col = {col: [] for col in columns}
        for row in rows:
            for col in columns:
                values_by_col[col].append(row.get(col))
        for col in columns:
            col_type, converter = _infer_column(values_by_col[col])
            column_defs.append(Column(col, col_type))
            converters[col] = converter
    else:
        for col in columns:
            column_defs.append(Column(col, Text()))
            converters[col] = _clean_value

    metadata = MetaData()
    table_obj = Table(table_name, metadata, *column_defs, schema=schema)

    typed_rows = []
    for row in rows:
        typed_rows.append({col: converters[col](row.get(col)) for col in columns})

    inspector = inspect(engine)
    exists = inspector.has_table(table_name, schema=schema)

    with engine.begin() as conn:
        if write_mode == "replace":
            conn.execute(text(f"DROP TABLE IF EXISTS {qualified}"))
            exists = False

        if not exists:
            table_obj.create(bind=conn, checkfirst=True)
            exists = True

        if write_mode == "truncate":
            conn.execute(text(f"TRUNCATE TABLE {qualified}"))

        if typed_rows:
            for start in range(0, len(typed_rows), batch_size):
                chunk = typed_rows[start : start + batch_size]
                conn.execute(table_obj.insert(), chunk)

    print(
        f"Postgres OK: {schema}.{table_name} | filas_cargadas={len(typed_rows)}"
    )
    return f"{schema}.{table_name}"


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Carga un CSV limpio a Postgres."
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Ruta al CSV limpio (ej: data/processed/archivo.csv).",
    )
    parser.add_argument(
        "--table",
        default=None,
        help="Nombre de la tabla destino (opcional, usa PG_TABLE).",
    )
    parser.add_argument(
        "--schema",
        default=None,
        help="Schema destino (opcional, usa PG_SCHEMA o public).",
    )
    parser.add_argument(
        "--write-mode",
        choices=["append", "truncate", "replace"],
        default=None,
        help="Modo de escritura en Postgres.",
    )
    parser.add_argument(
        "--no-infer-types",
        action="store_true",
        help="Desactiva inferencia de tipos y usa TEXT.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Tamano de lote para inserts.",
    )

    args = parser.parse_args()
    load_siniestros_to_postgres(
        args.csv,
        table=args.table,
        schema=args.schema,
        write_mode=args.write_mode,
        infer_types=not args.no_infer_types,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
