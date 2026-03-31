from sqlalchemy import text
from connect_sql import SessionLocal

def extract_siniestros(limit: int = 100):
    """
    Lee registros de ecosistema_clientes.t_siniestros en Postgres (stage).
    """
    print("Extrayendo siniestros...")
    
    # 1. Abrimos la sesión usando la configuración limpia de connect_sql.py
    db = SessionLocal()
    
    try:
        # 2. Definimos y ejecutamos la consulta
        query = text('SELECT "NUMERO_POLIZA","NOMBRE_RAMO_EMISION","NOMBRE_PRODUCTO","NUMERO_SINIESTRO","FECHA_SINIESTRO","FECHA_AVISO","DESCRIPCION_CAUSA","DESCRIPCION_SINIESTRO","MUNICIPIO_SINIESTRO","DEPARTAMENTO_SINIESTRO" FROM "ecosistema_clientes"."t_siniestros" LIMIT :limit')
        result = db.execute(query, {"limit": limit})
        
        # 3. Transformamos el resultado a una lista de diccionarios
        siniestros = [dict(row._mapping) for row in result]
        
        print(f"Filas obtenidas: {len(siniestros)}")
        return siniestros
        
    except Exception as e:
        print(f"Error durante la extracción de datos: {e}")
        return []
        
    finally:
        # 4. Aseguramos el cierre de la conexión
        db.close()