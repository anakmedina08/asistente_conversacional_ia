from pathlib import Path
from datetime import datetime
import csv


def _processed_dir() -> Path:
    """
    Retorna el directorio data/processed, creándolo si no existe.
    """
    base_dir = Path(__file__).resolve().parent.parent
    processed = base_dir / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    return processed


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
    columns = sorted({k for row in rows for k in row.keys()})

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
    return save_siniestros_to_csv(rows, filename)
