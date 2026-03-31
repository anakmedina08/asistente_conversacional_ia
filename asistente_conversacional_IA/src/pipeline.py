from extract import extract_siniestros
from transform import transform_data_siniestros


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

    print("Pipeline de extracción de siniestros completada.")

if __name__ == "__main__":
    main()
