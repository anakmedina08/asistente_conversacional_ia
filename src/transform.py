from pathlib import Path
from datetime import datetime, date
from collections import Counter
from decimal import Decimal
import csv
import math
import statistics


def _processed_dir() -> Path:
    """
    Retorna el directorio data/processed, creándolo si no existe.
    """
    base_dir = Path(__file__).resolve().parent.parent
    processed = base_dir / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    return processed


def _is_null(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _normalize_value(value):
    if _is_null(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    return value


def _normalize_rows(rows: list[dict]) -> list[dict]:
    normalized = []
    for row in rows:
        normalized.append({k: _normalize_value(v) for k, v in row.items()})
    return normalized


def _collect_columns(rows: list[dict]) -> list[str]:
    columns = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                columns.append(key)
                seen.add(key)
    return columns


def _is_numeric(value) -> bool:
    if _is_null(value):
        return False
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float, Decimal))


def _to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _percentile(sorted_values: list[float], pct: float) -> float | None:
    if not sorted_values:
        return None
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    k = (n - 1) * pct
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)


def _make_hashable(value):
    if _is_null(value):
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_make_hashable(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted(_make_hashable(v) for v in value))
    return value


def _format_top_values(counter: Counter, limit: int = 3) -> str:
    if not counter:
        return "-"
    parts = []
    for value, count in counter.most_common(limit):
        value_str = str(value)
        if len(value_str) > 40:
            value_str = value_str[:37] + "..."
        parts.append(f"{value_str}({count})")
    return ", ".join(parts)


def _analyze_rows(rows: list[dict]) -> None:
    if not rows:
        print("No hay datos para analizar.")
        return

    columns = _collect_columns(rows)
    row_count = len(rows)
    col_count = len(columns)

    print("Resumen de datos:")
    print(f"- Filas: {row_count}")
    print(f"- Columnas: {col_count}")
    print(f"- Campos: {', '.join(columns)}")

    print("\nValidación de nulos y tipos:")
    null_counts = {}
    type_counts = {}
    for col in columns:
        counter = Counter()
        nulls = 0
        for row in rows:
            value = row.get(col)
            if _is_null(value):
                nulls += 1
                continue
            counter[type(value).__name__] += 1
        null_counts[col] = nulls
        type_counts[col] = counter
        types_str = _format_top_values(counter, limit=5)
        warning = " [!]" if len(counter) > 1 else ""
        print(f"- {col}: nulos={nulls}, tipos={types_str}{warning}")

    total_nulls = sum(null_counts.values())
    print(f"Total de valores nulos: {total_nulls}")

    print("\nValidación de duplicados:")
    unique_rows = set()
    for row in rows:
        signature = tuple(_make_hashable(row.get(col)) for col in columns)
        unique_rows.add(signature)
    duplicates = row_count - len(unique_rows)
    dup_pct = (duplicates / row_count) * 100 if row_count else 0
    print(f"- Filas duplicadas: {duplicates} ({dup_pct:.2f}%)")

    numeric_cols = []
    for col in columns:
        numeric_values = []
        for row in rows:
            value = row.get(col)
            if _is_numeric(value):
                numeric_values.append(_to_float(value))
        if numeric_values:
            numeric_cols.append((col, numeric_values))

    if numeric_cols:
        print("\nAnalítica descriptiva (numéricas):")
        for col, values in numeric_cols:
            values_sorted = sorted(values)
            count = len(values_sorted)
            mean = statistics.mean(values_sorted)
            median = statistics.median(values_sorted)
            std = statistics.pstdev(values_sorted) if count > 1 else 0.0
            vmin = values_sorted[0]
            vmax = values_sorted[-1]
            q1 = _percentile(values_sorted, 0.25)
            q3 = _percentile(values_sorted, 0.75)
            iqr = q3 - q1 if q1 is not None and q3 is not None else 0
            lower = q1 - 1.5 * iqr if q1 is not None else None
            upper = q3 + 1.5 * iqr if q3 is not None else None
            if lower is not None and upper is not None and iqr > 0:
                outliers = sum(1 for v in values_sorted if v < lower or v > upper)
            else:
                outliers = 0
            print(
                f"- {col}: n={count}, media={mean:.4f}, mediana={median:.4f}, "
                f"std={std:.4f}, min={vmin:.4f}, p25={q1:.4f}, p75={q3:.4f}, "
                f"max={vmax:.4f}, outliers={outliers}"
            )

    text_cols = []
    for col in columns:
        values = []
        for row in rows:
            value = row.get(col)
            if _is_null(value):
                continue
            if isinstance(value, (str, datetime, date)):
                values.append(value)
        if values:
            text_cols.append((col, values))

    if text_cols:
        print("\nAnalítica descriptiva (categóricas/texto):")
        for col, values in text_cols:
            total = len(values)
            unique = len(set(values))
            top = _format_top_values(Counter(values), limit=3)
            print(f"- {col}: total={total}, únicos={unique}, top={top}")


def save_siniestros_to_csv(rows: list[dict], filename: str | None = None) -> str | None:
    """
    Guarda los siniestros en data/processed como CSV.
    Retorna la ruta del archivo o None si no hay datos.
    """
    if not rows:
        print("No hay siniestros para guardar.")
        return None

    processed = _processed_dir()
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"siniestros_{ts}.csv"

    path = processed / filename

    # Conjunto de columnas
    columns = _collect_columns(rows)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV guardado en: {path}")
    return str(path)


def transform_data_siniestros(rows: list[dict], filename: str | None = None) -> str | None:
    """
    Punto de entrada de transformación para siniestros.
    Actualmente solo guarda a CSV en data/processed.
    """
    normalized_rows = _normalize_rows(rows)
    print("Normalización aplicada: trim de strings y vacíos a null.")
    _analyze_rows(normalized_rows)
    return save_siniestros_to_csv(normalized_rows, filename)
