import os
import json
import sqlalchemy
from urllib.parse import quote_plus
from sqlalchemy.orm import sessionmaker
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector, IPTypes


# Identificadores fijos para stage
STAGE_SECRET_ID = "postgres-db-stage-credentials-usr_dev_stage"
STAGE_PROJECT_ID = "911414108629"


def get_secret(secret_id: str, project_id: str, version_id: str = "latest") -> dict:
    """
    Recupera las credenciales desde Secret Manager y las retorna como diccionario.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return json.loads(response.payload.data.decode("UTF-8"))


def get_engine():
    """
    Crea el engine de SQLAlchemy usando Google Cloud SQL Connector (solo stage).
    """
    creds = get_secret(STAGE_SECRET_ID, STAGE_PROJECT_ID)

    instance_connection_name = creds["host"]
    db_user = creds["user"]
    db_pass = creds["password"]
    db_name = creds["database"]
    proxy_host = os.getenv("DB_PROXY_HOST")
    proxy_port = os.getenv("DB_PROXY_PORT", "5432")

    # Si se define DB_PROXY_HOST, conectamos vía proxy (localhost o túnel) sin Cloud SQL Connector
    if proxy_host:
        print(f"[connect_sql] proxy mode host={proxy_host}:{proxy_port}")
        user_enc = quote_plus(db_user)
        pass_enc = quote_plus(db_pass)
        engine = sqlalchemy.create_engine(
            f"postgresql+pg8000://{user_enc}:{pass_enc}@{proxy_host}:{proxy_port}/{db_name}"
        )
        return engine
    # Permite elegir el tipo de IP vía variable de entorno (PUBLIC/PRIVATE)
    ip_pref = os.getenv("DB_IP_TYPE", "PRIVATE").upper()
    ip_type = IPTypes.PUBLIC if ip_pref == "PUBLIC" else IPTypes.PRIVATE

    print(f"[connect_sql] host={instance_connection_name} ip_type={ip_type}")
    connector = Connector()

    def getconn():
        """
        Retorna la conexión pg8000 para SQLAlchemy.
        """
        return connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine


# Crear engine y sesión
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency para FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
