from extract import extract_siniestros
from transform import transform_data_siniestros
from load import load_siniestros_to_postgres


def main():
    """
    Extrae siniestros desde Postgres (stage) y los guarda en data/processed como CSV.
    """
    print("Iniciando pipeline de extracción de siniestros...")
    siniestros = extract_siniestros()
    print("Extracción de siniestros completada.")

    print("Iniciando transformación de siniestros...    ")
    siniestros_csv = transform_data_siniestros(siniestros)
    print(f"Siniestros transformados y guardados en: {siniestros_csv}")
    print("Transformación de siniestros completada.")

    if siniestros_csv:
        print("Iniciando carga a Postgres...")
        load_siniestros_to_postgres(siniestros_csv)
        print("Carga a Postgres completada.")

    print("Pipeline de extracción de siniestros completada.")

if __name__ == "__main__":
    main()
