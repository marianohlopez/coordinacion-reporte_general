# 📊 Pipeline de Reportes Automáticos – Coordinación Escolar

Este proyecto implementa un pipeline ETL en Python que extrae datos desde una base de datos de gestión de inclusión escolar, los transforma en reportes claros en Excel y los envía automáticamente por correo electrónico a la coordinación general en un momento definido del mes.

Su objetivo es facilitar la supervisión de la carga de informes y seguimientos mensuales por alumno, permitiendo a la coordinación detectar rápidamente faltantes y evaluar el nivel de cumplimiento de cada coordinadora.

---

## 🚀 Características principales

- **Extracción (Extract):**

  - Consulta datos de prestaciones, informes y seguimientos directamente desde la base de datos (MySQL).
  - Obtiene también métricas de altas, bajas y prestaciones sin profesional asignado (PA).

- **Transformación (Transform):**

  - Procesa los datos en Python con consultas SQL optimizadas.
  - Genera un reporte Excel con varias hojas, entre ellas:
    - **Resumen general:** métricas por coordinadora (alumnos, informes cargados, seguimientos, prestaciones con/sin PA, etc.).
    - **Prestaciones sin PA:** casos abiertos hace más de 30 días sin asignación.
    - **Detalle de informes:** qué alumnos tienen informes cargados o pendientes.
    - **Detalle de seguimientos:** seguimiento mensual cargado por alumno.
    - **Últimas prestaciones activadas.**
    - **Altas y bajas mensuales.**

- **Carga y Envío (Load):**
  - Exporta automáticamente el archivo Excel con fecha en el nombre.
  - Envía el archivo a la coordinadora general por correo electrónico mediante `yagmail` y credenciales seguras cargadas desde variables de entorno.

---

## 🛠️ Tecnologías utilizadas

- **Lenguaje:** Python 3.10
- **Librerías principales:**
  - `openpyxl` → generación de archivos Excel
  - `yagmail` → envío de correos vía Gmail
  - `python-dotenv` → gestión de credenciales en variables de entorno
  - `babel` → formato de fechas en español
- **Base de datos:** MySQL (consultas SQL)
- **Entorno:** Script ejecutable programado (cron job o Task Scheduler)
