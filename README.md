# TA E10 – Estructura de la atención y prioridad de seguimiento (Puericultorio Pérez Araníbar)

**Curso:** Análisis de Datos 1INF03 (PUCP), 2026-2 · **Equipo:** E10 · **Entrega:** KDD Steps 1–6

El Puericultorio registra cada mes, en la ficha nominal, la atención que recibe cada NNA (soporte psicoemocional, salud mental,
plan de trabajo individual, situación legal) y, aparte, sus mediciones de peso y talla. Este proyecto:
1. **descubre cómo se organiza la atención** registrada en 19 meses de ficha y construye un **índice de prioridad** de seguimiento;
2. describe el **estado nutricional** con puntajes z de la OMS y prueba si se asocia con la atención;
3. **audita** las evaluaciones en que la ficha y la clasificación OMS de las mediciones no coinciden.

Se sigue el proceso KDD de Fayyad et al.; cada notebook corresponde a un paso.

> **Cómo se llegó aquí.** El avance clasificaba la etiqueta nutricional de la ficha (AUC ≈ 0,85; commit `f34c0d9`), pero imitaba un registro
> manual con rezago. Después se probó clustering, primero con la nutrición y luego con la atención, como en la literatura de acogimiento
> residencial. Ninguno encontró grupos que no estuvieran ya escritos en la ficha. El PCA sí encontró estructura real, estable y no trivial.
> Los entregables del avance (presentación, ficha técnica, Gantt y su script) quedan en el historial de git, commit `f34c0d9`.

## Estructura

```
TA_Analisis_Datos/
├── README.md                  este archivo (incluye la declaración de uso de IA)
├── requirements.txt           versiones de las librerías
├── run_all.py                 ejecuta todos los notebooks desde cero y verifica el resultado
├── src/oms.py                 puntajes z OMS (método LMS) de IMC y talla para la edad
├── datos/
│   ├── 0_crudos/              originales, solo lectura (hashes.json verifica que no cambien)
│   │   └── referencias/oms_lms/   tablas LMS oficiales de la OMS (who.int): 0–5 años (2006) y 5–19 años (2007)
│   ├── 1_consolidados/        Step2a: Bloque 2 consolidado desde los 6 Excel mensuales
│   ├── 2_limpios/             Step3: ficha limpia, Bloque 2 limpio, mediciones, evaluaciones, trayectoria de atención por niño
│   ├── 3_transformados/       Step4: variables de atención por niño, mediciones con z y estado nutricional por niño
│   └── 4_resultados/          Step5, Step6 y anexo: auditoría, comparación de métodos, mapa e índice de prioridad, cifras_*.json
├── notebooks/                 un notebook por paso KDD (ver orden)
└── figuras/                   prefijo = paso que la genera
```

## Notebooks y orden de ejecución

| # | Notebook | Paso KDD | Qué hace |
|---|---|---|---|
| 1 | `Step1_Entendimiento_del_Dominio` | 1 | Caso, conocimiento previo, objetivos (estructura de la atención, nutrición, auditoría) y cómo se llegó a ellos |
| 2 | `Step2a_Consolidacion_Bloque2` | 2 | Une los 6 Excel de nutrición con un mapeo de columnas explícito y verificado |
| 3 | `Step2b_Seleccion_y_Entendimiento` | 2 | Calidad de datos, población, unidad de análisis y criterios de inclusión |
| 4 | `Step3_Limpieza_y_Preprocesamiento` | 3 | Limpieza, etiquetas, cruce ficha × medición; **trayectoria de atención por niño** (162) y tabla de mediciones (376) |
| 5 | `Step4_Reduccion_y_Proyeccion` | 4 | z OMS de IMC y talla (verificados contra las tablas); variables de atención, redundancia y Hopkins frente a dos nulas |
| 6 | `Step5_Seleccion_Tarea_de_Mineria` | 5 | Tarea por objetivo y auditoría de discrepancias para la nutricionista |
| 7 | `Anexo_Step6_clustering_nutricional` | 6 | Antecedente: clustering por z OMS (sin grupos naturales) |
| 8 | `Step6_Seleccion_de_Algoritmos` | 6 | Compara clustering (K-Means, Ward, Gower, LCA, HDBSCAN, secuencias) y **PCA**; elige el PCA; mapa de la atención e índice de prioridad |

Cada notebook explica cada celda de código, interpreta sus resultados y verifica con `assert` las cifras que cita.

## Cómo ejecutar

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python run_all.py                 # ≈5 min; se detiene ante cualquier error o assert fallido
```

`Step2a` compara el consolidado nuevo con el anterior (`../Output/datos/raw/Nutricion_Consolidado_2026.xlsx`) si ese archivo existe; si no, omite la comparación.

## Resultados principales

- **El clustering no descubre nada nuevo en estos datos.** Con la nutrición (z OMS) no hay grupos naturales (anexo). Con la atención,
  ninguna combinación de K-Means, Ward, Gower, LCA o HDBSCAN cumple la regla de estabilidad y referencias nulas. La más estable repite la
  situación legal (ARI 0,75), y el clustering de secuencias repite el estado predominante de cada niño (ARI 0,99).
- **El PCA encuentra dos dimensiones reales y estables** (análisis paralelo de Horn; congruencia de Tucker 0,93 y 0,86), que explican el 40,9 %:
  **permanencia** (situación definitiva, tiempo en el hogar, sin PTI) e **intensidad psicosocial** (salud mental, acompañamiento, talleres, discapacidad).
  Son independientes: **la atención psicosocial no aumenta con la permanencia**.
- **Índice de prioridad:** 51 niños (32 %) tienen permanencia alta e intensidad baja. Llevan en promedio 8 años en el hogar, el 84 % pasó la mitad
  de los meses o más sin soporte psicoemocional, el 63 % sin PTI y ninguno recibió salud mental especializada (`step6_mapa_atencion.csv`).
- **La permanencia difiere entre UPE** (*p* < 0,001); la intensidad psicosocial no depende de la edad ni de la UPE.
- **Nutrición:** la población pesa más y mide menos de lo esperado (z de IMC +0,98; z de talla −0,94). El exceso de peso (≈ 40 %) es igual en todos los
  hogares, sexos, edades y perfiles de atención: es un problema **institucional**, no focalizado.
- **Auditoría:** la ficha y la clasificación OMS concuerdan en el 68,8 % de las evaluaciones, y la institución usa cortes más laxos que la OMS.

## Pendiente para la entrega final (Steps 7–9)

- **Step 7 – Minería:** recalcular el índice con los meses nuevos de ficha y medir cuánto se mueve cada niño en el mapa.
- **Step 8 – Interpretación:** validar los nombres de las dimensiones y la lista de prioridad con el equipo del Puericultorio; revisar la diferencia entre UPE.
- **Step 9 – Consolidación:** informe final, ficha técnica y Gantt finales.

## Declaración de uso de IA generativa

Conforme a los lineamientos del curso, el equipo declara el uso de IA generativa:

- **Herramienta:** Claude (Anthropic), usado mediante **Claude Code**.
- **Usos:**
  - revisión de los notebooks anteriores (auditoría de pasos innecesarios, errores y fugas de información);
  - auditoría del consolidado de nutrición contra los 6 Excel originales;
  - diseño y reconstrucción del proyecto: estructura de carpetas, código de los notebooks y redacción de sus interpretaciones;
  - script `run_all.py`;
  - reorientación del pipeline: cálculo de z OMS (`src/oms.py`), trayectoria de atención por niño, comparación de clustering y PCA con referencias nulas y estabilidad, índice de prioridad y redacción de las interpretaciones.
- **Justificación:** acelerar el trabajo operativo y detectar errores de ejecución. Las decisiones de análisis (objetivo, unidad de análisis, variables, algoritmo elegido) son responsabilidad del equipo y deben revisarse antes de la entrega.
