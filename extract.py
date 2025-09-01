from babel.dates import format_date
from datetime import date

def extract_general(cursor):

  query = """
      WITH prestaciones_alumnos AS (
        SELECT 
          prestacion_coordi,
          CONCAT(coordi_apellido, ', ', coordi_nombre) as coordi_nombre_apellido,
          COUNT(DISTINCT alumno_id) AS alumnos,
          COUNT(DISTINCT prestacion_id) AS prestaciones,
          COUNT(DISTINCT CASE WHEN prestacion_pa IS NOT NULL THEN prestacion_id END) AS prestaciones_con_pa,
          COUNT(DISTINCT CASE WHEN prestacion_pa IS NULL THEN prestacion_id END) AS prestaciones_sin_pa,
          COUNT(DISTINCT CASE WHEN calcpagopamod_nombre = "COMPLETO" THEN prestacion_id END) AS completa,
          COUNT(DISTINCT CASE WHEN calcpagopamod_nombre = "PARCIAL" THEN prestacion_id END) AS parcial,
          COUNT(DISTINCT CASE WHEN calcpagopamod_nombre = "PACIAL 2 DÍAS" THEN prestacion_id END) AS parcial_2,
          COUNT(DISTINCT CASE WHEN calcpagopamod_nombre = "PACIAL 3 DÍAS" THEN prestacion_id END) AS parcial_3,
          COUNT(DISTINCT CASE WHEN calcpagopamod_nombre = "PACIAL 4 DÍAS" THEN prestacion_id END) AS parcial_4,
          COUNT(DISTINCT CASE WHEN calcpagopamod_nombre = "AL DÍA" THEN prestacion_id END) AS al_dia,
          COUNT(DISTINCT CASE WHEN calcpagopamod_nombre = "POLETTI AT" THEN prestacion_id END) AS poletti_at
        FROM v_prestaciones
        WHERE
          prestacion_estado IN (0, 1)
          AND prestipo_nombre_corto != 'TERAPIAS'
          AND coordi_apellido IS NOT NULL
        GROUP BY coordi_nombre, coordi_apellido
    ),
    -- Informes (solo de la coordinadora asignada)
    informes AS (
        SELECT 
          c.coordi_id,
          COUNT(DISTINCT i.alumnoinforme_id) AS informes
        FROM v_prestaciones p
        JOIN v_coordinadores c
          ON p.prestacion_coordi = c.coordi_id
        JOIN v_informes i
          ON p.alumno_id = i.alumno_id
        JOIN v_users u
          ON u.user_name = i.usuario
        AND u.user_email = c.coordi_mail
        WHERE
          i.alumnoinforme_anio = '2025'
          AND p.prestipo_nombre_corto != 'TERAPIAS'
        GROUP BY c.coordi_id
    ),
    -- Seguimientos (sin depender de informes)
    seguimientos AS (
        SELECT 
          c.coordi_id,
          COUNT(DISTINCT s.segalum_id) AS seguimientos
        FROM v_prestaciones p
        JOIN v_coordinadores c
          ON p.prestacion_coordi = c.coordi_id
        JOIN v_seguimientos s
          ON p.alumno_id = s.segalum_alumno
        JOIN v_users u
          ON u.user_id = s.usuario_carga_id
        AND u.user_email = c.coordi_mail
        WHERE
          p.prestacion_estado IN (0, 1)
          AND p.prestipo_nombre_corto != 'TERAPIAS'
          AND YEAR(segalum_fec_carga) = 2025
        GROUP BY c.coordi_id
    )
    -- Unir todo
    SELECT 
        pa.coordi_nombre_apellido,
        pa.alumnos,
        pa.prestaciones,
        COALESCE(i.informes, 0) AS informes,
        COALESCE(s.seguimientos, 0) AS seguimientos,
        pa.prestaciones_con_pa,
        pa.prestaciones_sin_pa,
        pa.completa,
        pa.parcial,
        pa.parcial_2,
        pa.parcial_3,
        pa.parcial_4,
        pa.al_dia,
        pa.poletti_at
    FROM prestaciones_alumnos pa
    LEFT JOIN informes i
        ON pa.prestacion_coordi = i.coordi_id
    LEFT JOIN seguimientos s
        ON pa.prestacion_coordi = s.coordi_id
    ORDER BY pa.coordi_nombre_apellido;
  """
  cursor.execute(query)
  return cursor.fetchall()

def extract_prest_sin_pa(cursor):
  query = """ 
    SELECT 
    p.prestacion_id,
    p.prestacion_alumno,
    DATE_FORMAT(COALESCE(MAX(a.asignpa_pa_fec_baja), a.asignpa_fec1), '%d-%m%-%Y') AS ultima_fecha_sin_pa,
    DATEDIFF(CURDATE(), COALESCE(MAX(a.asignpa_pa_fec_baja), a.asignpa_fec1)) AS dias_sin_pa
    FROM 
        v_prestaciones p
    LEFT JOIN 
        v_asignaciones_pa a 
        ON p.prestacion_id = a.asignpa_prest
    WHERE 
        p.prestipo_nombre_corto != 'TERAPIAS'
        AND p.prestacion_pa IS NULL
        AND p.prestacion_estado = 1
    GROUP BY 
        p.prestacion_id, p.prestacion_alumno
    HAVING 
        dias_sin_pa > 30;
    """
  cursor.execute(query)
  return cursor.fetchall()

def extract_informes(cursor):
  query = """ 
    SELECT 
        CONCAT(c.coordi_apellido, ', ', c.coordi_nombre) AS nombre_coordi,
        CONCAT(p.alumno_apellido, ', ', p.alumno_nombre) AS nombre_alumno,
        p.alumno_dni,
        COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe Inicial - ADMISIÓN" THEN i.alumnoinforme_id END) AS inf_admision,
        COUNT(DISTINCT CASE WHEN (i.informecat_nombre IN ("Informe Diagnóstico", "Informe Semestral", "Informe Medio")) 
            THEN i.alumnoinforme_id END) AS inf_diagnostico,
        COUNT(DISTINCT CASE WHEN i.informecat_nombre = "OTRO" THEN i.alumnoinforme_id END) AS otro,
        COUNT(DISTINCT CASE WHEN i.informecat_nombre = "AA" THEN i.alumnoinforme_id END) AS aa,
        COUNT(DISTINCT CASE WHEN i.informecat_nombre = "PPI / PI" THEN i.alumnoinforme_id END) AS ppi,
        COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe Final" THEN i.alumnoinforme_id END) AS inf_final
    FROM v_prestaciones p
    JOIN v_coordinadores c
        ON p.prestacion_coordi = c.coordi_id
    LEFT JOIN v_informes i 
        ON p.alumno_id = i.alumno_id 
    AND i.alumnoinforme_anio = '2025'
    WHERE
        p.prestipo_nombre_corto != 'TERAPIAS'
        AND p.prestacion_estado IN (0, 1)
    GROUP BY p.alumno_id, p.alumno_dni
    ORDER BY nombre_coordi;
    """
  cursor.execute(query)
  return cursor.fetchall()

def extract_seguim(cursor):
  query = """ 
    SELECT 
        CONCAT(c.coordi_apellido, ', ', c.coordi_nombre) AS nombre_coordi,
        s.segalum_prestacion,
        CONCAT(p.alumno_apellido, ', ', p.alumno_nombre) AS nombre_alumno,
        s.segalum_mesanio,
        DATE_FORMAT(s.segalum_fec_carga, '%d-%m-%Y') AS fec_carga,
        s.segcat_nombre
    FROM
        v_prestaciones p
    JOIN v_seguimientos s
        ON p.prestacion_id = s.segalum_prestacion
    JOIN v_users u
        ON s.usuario_carga_id = u.user_id
    JOIN v_coordinadores c
        ON u.user_email = c.coordi_mail
    WHERE
        p.prestacion_estado IN (0, 1)
        AND p.prestipo_nombre_corto != 'TERAPIAS'
        AND s.segalum_rol_carga = 'COORDI'
        AND YEAR(s.segalum_fec_carga) = 2025 
    ORDER BY nombre_coordi
    """
  cursor.execute(query)
  return cursor.fetchall()

def extract_prest(cursor):
  query = """ 
    SELECT 
      prestacion_id, 
      CONCAT(alumno_apellido, ", ",alumno_nombre), 
      DATE_FORMAT(prestacion_fec_aut_OS, '%d-%m%-%Y') as fec_act
    FROM
      v_prestaciones
    WHERE 
      prestacion_estado = 1
      AND prestipo_nombre_corto != "TERAPIAS"
      AND prestacion_fec_aut_OS >= CURDATE() - INTERVAL 14 DAY
    ORDER BY prestacion_fec_aut_OS ASC;
  """
  cursor.execute(query)
  return cursor.fetchall()

def extract_altas_bajas(cursor):
  query = """ 
    SELECT 
    anio,
    mes,
    SUM(altas) AS total_altas,
    SUM(bajas) AS total_bajas
    FROM (
        -- Altas
        SELECT 
            YEAR(asignpa_pa_fec_alta) AS anio,
            MONTH(asignpa_pa_fec_alta) AS mes,
            1 AS altas,
            0 AS bajas
        FROM v_asignaciones_pa
        WHERE YEAR(asignpa_pa_fec_alta) IN (2025, 2024)

        UNION ALL

        -- Bajas
        SELECT 
            YEAR(asignpa_pa_fec_baja) AS anio,
            MONTH(asignpa_pa_fec_baja) AS mes,
            0 AS altas,
            1 AS bajas
        FROM v_asignaciones_pa
        WHERE YEAR(asignpa_pa_fec_baja) IN (2025, 2024)
    ) t
    GROUP BY anio, mes
    ORDER BY anio, mes;
    """
  cursor.execute(query)
  rows = cursor.fetchall()

  # Transformar el número de mes en nombre en español
  result = []
  for anio, mes, total_altas, total_bajas in rows:
      fecha = date(anio, mes, 1)
      nombre_mes = format_date(fecha, "MMMM", locale='es').capitalize()   
      result.append([anio, nombre_mes, total_altas, total_bajas])

  return result
