# TA E10 – Perfiles nutricionales y auditoría de la ficha (Puericultorio Pérez Araníbar)

**Curso:** Análisis de Datos 1INF03 (PUCP), 2026-2 · **Equipo:** E10 · **Entrega:** KDD Steps 1–6 (enfoque de clustering)

El Puericultorio registra a mano el estado nutricional de cada NNA en la ficha nominal mensual. Este proyecto
(1) agrupa a los NNA en **perfiles nutricionales** a partir de cuánto se alejan su IMC y su talla de lo esperado para su edad y sexo
(puntajes z de la OMS), **sin usar la etiqueta de la ficha**, y
(2) **audita** en qué niños y meses la ficha y la clasificación OMS de las mediciones no coinciden, y en qué perfiles se concentran esas discrepancias.
Se sigue el proceso KDD de Fayyad et al.; cada notebook corresponde a un paso.

> **Cambio de enfoque.** El avance planteaba una clasificación supervisada de la etiqueta de la ficha (regresión logística, AUC ≈ 0,85).
> Esa versión queda en el historial de git (commit `f34c0d9`). La etiqueta manual se actualiza con rezago y discrepa de las mediciones
> en un tercio de los casos, así que ahora solo se usa para validar los grupos y para la auditoría.

## Estructura

```
TA_Analisis_Datos/
├── README.md                  este archivo (incluye la declaración de uso de IA)
├── requirements.txt           versiones de las librerías
├── run_all.py                 ejecuta todos los notebooks desde cero y verifica el resultado
├── actualizar_entregables.py  entregables del AVANCE (pendiente de adaptar al clustering, ver abajo)
├── src/oms.py                 puntajes z OMS (método LMS) de IMC y talla para la edad
├── datos/
│   ├── 0_crudos/              originales, solo lectura (hashes.json verifica que no cambien)
│   │   └── referencias/oms_lms/   tablas LMS oficiales de la OMS (who.int): 0–5 años (2006) y 5–19 años (2007)
│   ├── 1_consolidados/        Step2a: Bloque 2 consolidado desde los 6 Excel mensuales
│   ├── 2_limpios/             Step3: ficha limpia, Bloque 2 limpio, mediciones, evaluaciones y tabla por niño
│   ├── 3_transformados/       Step4: mediciones con z y tabla por niño (insumo del clustering)
│   └── 4_resultados/          Step5 y Step6: auditoría, selección de k, grupos, perfiles y cifras_*.json
├── notebooks/                 un notebook por paso KDD (ver orden)
├── figuras/                   prefijo = paso que la genera
└── entregables/               FichaTecnica_E10.xlsx, Gantt_E10.xlsx, Avance_TA_E10.pptx (+ plantillas/ originales)
```

## Notebooks y orden de ejecución

| # | Notebook | Paso KDD | Qué hace |
|---|---|---|---|
| 1 | `Step1_Entendimiento_del_Dominio` | 1 | Caso, conocimiento previo (OMS/INS, indicadores), objetivos (clustering + auditoría), inventario de fuentes |
| 2 | `Step2a_Consolidacion_Bloque2` | 2 | Une los 6 Excel de nutrición con un mapeo de columnas explícito y verificado |
| 3 | `Step2b_Seleccion_y_Entendimiento` | 2 | Calidad de datos, población, unidad de análisis y criterios de inclusión |
| 4 | `Step3_Limpieza_y_Preprocesamiento` | 3 | Limpieza, etiquetas, cruce ficha × medición; **tabla de mediciones** (376, sin exigir etiqueta) y tabla por niño de la ficha |
| 5 | `Step4_Reduccion_y_Proyeccion` | 4 | **z OMS** de IMC y talla (verificados contra las tablas), unidad = niño, cambio anual, escalado, Hopkins |
| 6 | `Step5_Seleccion_Tarea_de_Mineria` | 5 | Tarea por objetivo (clustering) y auditoría de discrepancias para la nutricionista |
| 7 | `Step6_Seleccion_de_Algoritmos` | 6 | K-Means, GMM, Ward, Gower y HDBSCAN; elección de k, referencia nula, estabilidad bootstrap; perfiles, validación externa y cruce con la auditoría |

Cada notebook explica cada celda de código, interpreta sus resultados y verifica con `assert` las cifras que cita.

## Cómo ejecutar

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python run_all.py                 # ≈5 min; se detiene ante cualquier error o assert fallido
```

`Step2a` compara el consolidado nuevo con el anterior (`../Output/datos/raw/Nutricion_Consolidado_2026.xlsx`) si ese archivo existe; si no, omite la comparación.

## Resultados principales

- **Datos:** 376 mediciones de **139 NNA** en 2026 (el avance usaba 324 de 121, porque exigía la etiqueta del mismo mes).
- **Estado nutricional:** en promedio la población pesa más y mide menos de lo esperado (z de IMC medio +0,98; z de talla −0,94).
  La clasificación OMS que registra la institución sigue el orden del z (Spearman 0,85 en IMC y 0,79 en talla), pero con cortes más laxos (solo 51 de 85 "talla baja" registradas tienen z < −2).
- **No hay grupos naturales:** Hopkins igual al de una sola nube normal (0,64 frente a 0,66; *p* = 0,81), el BIC elige una sola gaussiana,
  ninguna silueta supera con claridad a la referencia nula y HDBSCAN marca entre 34 % y 100 % de ruido. Ni el cambio en el tiempo ni las variables de la ficha (Gower) agregan estructura.
- **Segmentación elegida:** K-Means con k = 4 sobre los z, la más estable de las 35 evaluadas (ARI bootstrap 0,70, "patrón débil"):
  **G1 retraso de talla** (32), **G2 dentro de lo esperado** (43), **G3 exceso con talla en riesgo** (45, la "doble carga" que la regla OMS no separa) y **G4 exceso de peso** (19).
  ARI 0,31 con los cortes OMS: no es una copia de la regla.
- **Validación y auditoría:** sin usar la etiqueta, los grupos ordenan la alteración registrada (10 % en G2 frente a 43–68 % en los demás).
  La ficha subregistra sobre todo en **G1**: en el 43 % de esos niños dice "sin alteración" cuando la medición OMS indica exceso o talla baja.

## Pendiente para la entrega final (Steps 7–9)

- **Step 7 – Minería:** fijar la segmentación con todas las mediciones del año y medir si los niños se mantienen en su grupo de un mes a otro; centroides con intervalos bootstrap.
- **Step 8 – Interpretación:** validar los nombres de los perfiles y la lista de G1 con la nutricionista.
- **Step 9 – Consolidación:** informe final, ficha técnica y Gantt finales.
- `actualizar_entregables.py` todavía genera los entregables del **avance** con sus cifras (`cifras_anexo4`, `cifras_anexo6`, AUC del Step 6), que ya no existen.
  Hay que adaptarlo a las cifras nuevas (`cifras_step4.json`, `cifras_step6.json`) antes de regenerar la presentación.

## Declaración de uso de IA generativa

Conforme a los lineamientos del curso, el equipo declara el uso de IA generativa:

- **Herramienta:** Claude (Anthropic), usado mediante **Claude Code**.
- **Usos:**
  - revisión de los notebooks anteriores (auditoría de pasos innecesarios, errores y fugas de información);
  - auditoría del consolidado de nutrición contra los 6 Excel originales;
  - diseño y reconstrucción del proyecto: estructura de carpetas, código de los notebooks y redacción de sus interpretaciones;
  - scripts `run_all.py` y `actualizar_entregables.py`, y actualización de la ficha técnica, el Gantt y la presentación;
  - reorientación del pipeline a clustering: cálculo de z OMS (`src/oms.py`), tabla por niño, selección de algoritmos con referencia nula y estabilidad, perfiles y redacción de las interpretaciones.
- **Justificación:** acelerar el trabajo operativo y detectar errores de ejecución. Las decisiones de análisis (objetivo, unidad de análisis, variables, algoritmo elegido) son responsabilidad del equipo y deben revisarse antes de la entrega.
