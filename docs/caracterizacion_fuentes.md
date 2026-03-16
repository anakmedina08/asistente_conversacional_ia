## Caracterización de la Fuente de Datos (ETL)

Se detalla el origen y la estructura de los datos operativos utilizados para el entrenamiento y consulta del asistente conversacional del sector asegurador.

---

### Catálogo de Orígenes de Datos

| Fuente de Datos | Tipo de Sistema | Recolector | Tecnología | Datos Principales | Frecuencia |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pólizas** | Transaccional | Tronador | Oracle, BigQuery, PostgreSQL | `NUMERO_POLIZA`, `NOMBRE_RAMO_EMISION`, `NOMBRE_PRODUCTO`,`NUMERO_SINIESTRO`, `FECHA_SINIESTRO`, `FECHA_AVISO`, `DESCRIPCION_CAUSA`, `DESCRIPCION_SINIESTRO`, `MUNICIPIO_SINIESTRO`, `DEPARTAMENTO_SINIESTRO` | Diario |
| **Siniestros** | Transaccional | Tronador | Oracle, BigQuery, PostgreSQL | Pendiente | Diario |
| **Clientes** | Transaccional | Tronador | Oracle, BigQuery, PostgreSQL | Pendiente  | Diario |
| **Asistencias** | Transaccional | Tronador | Oracle, BigQuery, PostgreSQL | Pendiente | Diario |

---

### Notas de Implementación ETL
* **Almacenamiento:** Los datos se consolidan en BigQuery y en PostgreSql para optimizar las consultas de lenguaje natural del asistente.
