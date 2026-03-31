# Estado del Arte

En los últimos años, la inteligencia artificial conversacional ha experimentado un crecimiento significativo debido al avance en técnicas de procesamiento de lenguaje natural (NLP), aprendizaje automático y modelos generativos. Estas tecnologías han permitido desarrollar asistentes virtuales capaces de comprender y responder preguntas complejas en lenguaje natural, automatizando tareas de consulta y análisis de información en diferentes sectores, incluido el asegurador.

---

## Evolución de los asistentes conversacionales

Los sistemas conversacionales han evolucionado drásticamente desde los tradicionales chatbots basados en árboles de decisión y reglas estáticas, hacia sistemas cognitivos basados en modelos neuronales profundos. El punto de inflexión en esta evolución fue la introducción de la arquitectura **Transformer (Vaswani et al., 2017)**, la cual permitió el desarrollo de los Grandes Modelos de Lenguaje (LLMs). 

En la actualidad, el ecosistema de IA conversacional ha trascendido las simples interfaces de preguntas y respuestas, dando paso a **Agentes Autónomos** que utilizan LLMs como motores de razonamiento para interpretar la intención del usuario, trazar planes de ejecución y generar respuestas coherentes utilizando herramientas externas en tiempo real.

---

## Asistentes conversacionales en el sector asegurador: Del B2C al B2E

El sector asegurador ha adoptado progresivamente la inteligencia artificial, inicialmente enfocándose en soluciones de cara al cliente (B2C) para mejorar la experiencia del usuario. Estudios recientes demuestran que el uso de chatbots en atención al cliente logra reducir significativamente los tiempos de respuesta en consultas de pólizas y cotizaciones.

Sin embargo, la frontera actual de la innovación y el mayor valor agregado se encuentra en el ámbito **B2E (Business-to-Employee)**. En este enfoque, los asistentes conversacionales no actúan como soporte al cliente, sino como herramientas de inteligencia de negocios para analistas, actuarios y gerentes operativos. Estos sistemas permiten automatizar procesos internos como:

* Análisis de siniestralidad en tiempo real.
* Detección temprana de anomalías o posibles fraudes.
* Generación de reportes operativos cruzando múltiples bases de datos.
* Optimización de recursos operativos dentro de la organización.

---

## Integración con analítica avanzada: RAG y Text-to-SQL

En los sistemas corporativos modernos, los asistentes conversacionales no se limitan a generar texto libre, sino que se integran con plataformas de datos empresariales mediante dos enfoques arquitectónicos principales:

1. **Retrieval-Augmented Generation (RAG):** Utilizado para consultar bases de conocimiento no estructuradas (como manuales, PDFs de pólizas y normativas legales). La inyección de contexto mediante RAG actúa como un ancla de conocimiento, reduciendo drásticamente las alucinaciones de los modelos y mejorando la precisión en respuestas técnicas.
2. **Text-to-SQL y Agentes de Datos:** Dado que el análisis de datos operativos requiere interactuar con bases de datos relacionales y Data Warehouses, la industria ha adoptado arquitecturas que traducen consultas complejas en lenguaje natural a código estructurado (SQL o Python/Pandas). 

Mediante estas técnicas, el asistente no solo recupera información cualitativa, sino que automatiza tareas analíticas cuantitativas, transformando al asistente en un verdadero analista de datos virtual.

---

## Tendencias actuales

Las principales tendencias en el desarrollo de asistentes conversacionales corporativos incluyen:

* **Orquestación de Agentes** mediante frameworks especializados (ej. LangChain, LlamaIndex).
* **Uso de arquitecturas híbridas** (RAG + Text-to-SQL) para consultas unificadas.
* **Integración con plataformas de datos** bajo enfoques DataOps y AIOps.
* **Implementación de barreras de seguridad (Guardrails)** para proteger información sensible y asegurar la privacidad de los datos operativos.

---

## Brecha de investigación

A pesar de la madurez de los asistentes conversacionales en la atención al cliente (B2C), aún existen desafíos significativos en su aplicación para la inteligencia de negocios interna (B2E). En el contexto específico del sector asegurador, se identifican las siguientes brechas:

* **Integración eficiente con esquemas complejos:** La traducción precisa de consultas en lenguaje natural a lenguajes de consulta estructurados suele fallar cuando se enfrenta a bases de datos empresariales masivas con nomenclaturas específicas del negocio.
* **Orquestación de fuentes híbridas:** La dificultad de combinar en una sola respuesta datos estructurados (bases de datos de siniestros) y no estructurados (condicionados de pólizas en texto).
* **Gobernanza y confianza:** Garantizar la calidad, consistencia y trazabilidad de los datos utilizados por el asistente para que las respuestas sean auditables por los equipos de operaciones.

Por lo tanto, se identifica la necesidad de desarrollar soluciones que integren asistentes conversacionales con arquitecturas de datos empresariales, permitiendo consultas inteligentes y análisis automatizado de información operativa, de forma segura y escalable, en el sector asegurador.
