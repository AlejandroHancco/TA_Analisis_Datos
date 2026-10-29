# TA E10 – Auditoría y estimación del estado nutricional (Puericultorio Pérez Araníbar)

**Curso:** Análisis de Datos 1INF03 (PUCP), 2026-2 · **Equipo:** E10 · **Entrega:** avance (KDD Steps 1–6)

El Puericultorio registra a mano el estado nutricional de cada NNA en la ficha nominal mensual. Este proyecto
(1) estima la **alteración nutricional estricta** (exceso de peso o retraso de talla) de la ficha a partir de peso, talla, IMC, edad y sexo,
y (2) **audita** en qué niños y meses la ficha y la clasificación OMS de las mediciones no coinciden.
Se sigue el proceso KDD de Fayyad et al.; cada notebook corresponde a un paso.

## Estructura

```
TA_E10/
├── README.md                  este archivo (incluye la declaración de uso de IA)
├── requirements.txt           versiones de las librerías
├── ejecutar_todo.py           ejecuta todos los notebooks desde cero y verifica el resultado
├── actualizar_entregables.py  genera ficha técnica, Gantt y PPTX con las cifras de la ejecución
├── datos/
│   ├── 0_crudos/              originales, solo lectura (hashes.json verifica que no cambien)
│   ├── 1_consolidados/        Step2a: Bloque 2 consolidado desde los 6 Excel mensuales
│   ├── 2_limpios/             Step3: ficha limpia, Bloque 2 limpio, tabla de evaluaciones, tabla por niño (Anexo)
│   ├── 3_transformados/       Step4 y Anexo_Step4: train/test
│   └── 4_resultados/          Step5, Step6 y Anexos: tablas de resultados y cifras_*.json
├── notebooks/                 un notebook por paso KDD (ver orden)
├── figuras/                   prefijo = paso que la genera
├── entregables/               FichaTecnica_E10.xlsx, Gantt_E10.xlsx, Avance_TA_E10.pptx (+ plantillas/ originales)
└── docs/                      diseño y plan de la reconstrucción
```

## Notebooks y orden de ejecución

| # | Notebook | Paso KDD | Qué hace |
|---|---|---|---|
| 1 | `Step1_Entendimiento_del_Dominio` | 1 | Caso, conocimiento previo (OMS/INS, indicadores), objetivos, inventario de fuentes |
| 2 | `Step2a_Consolidacion_Bloque2` | 2 | Une los 6 Excel de nutrición con un mapeo de columnas explícito y verificado |
| 3 | `Step2b_Seleccion_y_Entendimiento` | 2 | Calidad de datos, población, unidad de análisis y criterios de inclusión |
| 4 | `Step3_Limpieza_y_Preprocesamiento` | 3 | Limpieza, etiquetas, cruce ficha × medición (periodo + ID), concordancia |
| 5 | `Anexo_Step4_solo_ficha` | 4 | Hipótesis descartada: transformación de las variables de la ficha |
| 6 | `Anexo_Step6_solo_ficha` | 6 | Hipótesis descartada: con la ficha sola no hay señal (AUC ≈ 0,5) |
| 7 | `Step4_Reduccion_y_Proyeccion` | 4 | Partición por niño, residuos por edad (`ResiduosEdad`), escalado, PCA descartado |
| 8 | `Step5_Seleccion_Tarea_de_Mineria` | 5 | Tarea por objetivo y auditoría de discrepancias para la nutricionista |
| 9 | `Step6_Seleccion_de_Algoritmos` | 6 | Logística, KNN, SVC con CV agrupada por niño en `Pipeline`, permutaciones, ablación, K-Means, sensibilidad a la semilla |

Cada notebook explica cada celda de código, interpreta sus resultados y verifica con `assert` las cifras que cita.

## Cómo ejecutar

```bash
pip install -r requirements.txt
python ejecutar_todo.py           # ≈10 min; se detiene ante cualquier error o assert fallido
python actualizar_entregables.py  # regenera los entregables con las cifras nuevas
```

`Step2a` compara el consolidado nuevo con el anterior (`../Output/datos/raw/Nutricion_Consolidado_2026.xlsx`) si ese archivo existe; si no, omite la comparación.

## Resultados principales del avance

- **Datos:** 324 evaluaciones (niño × mes) de 121 NNA, de 5 meses de 2026 con ficha. Prevalencia de alteración estricta: 37,3 %.
- **Clasificación:** la regresión logística con medidas crudas + ajustadas por edad alcanza **AUC 0,85** en validación cruzada agrupada por niño (0,76–0,86 según la partición); el SVC, 0,83. La señal no es casualidad (permutaciones por niño, *p* = 0,01). Con solo las variables de la ficha no hay señal (AUC 0,48–0,56).
- **Auditoría:** la ficha y la clasificación OMS concuerdan en el 68,8 % de las evaluaciones; 65 de 121 NNA tienen al menos una discrepancia (`datos/4_resultados/step5_auditoria_discrepancias.csv`).

## Correcciones respecto a la versión anterior (`Output/`)

Las decisiones de análisis no cambiaron; se corrigió la ejecución:

1. El Bloque 2 se consolida con código desde los Excel originales. Así se corrige `PPA_FN_0011` (`2020-03-40` → `2020-03-04`) y se convierten 8 fechas `DD/MM/AAAA`.
2. El cruce ficha × medición es por **periodo + ID** (la fecha de nacimiento solo distingue los 4 IDs reutilizados). Se recuperan 10 evaluaciones de 4 NNA cuya fecha de nacimiento difiere entre bloques (2 con día y mes invertidos).
3. Los residuos por edad y el escalado se ajustan **dentro de cada pliegue** (`Pipeline`), sin fuga hacia validación. En el Anexo, la imputación se ajusta solo en train.
4. Se agrega la sensibilidad del AUC a la semilla de partición (20 semillas).
5. La etiqueta principal (`alteracion_estricta`) es la misma en todos los notebooks; el cruce y las concordancias se calculan una sola vez; se eliminaron archivos y código sin uso.
6. La columna `Edad` del Bloque 2 no se usa: en junio y agosto es una fórmula `HOY()`.

## Pendiente para la entrega final (Steps 7–9)

- **Step 7 – Minería:** ajuste de hiperparámetros con `GridSearchCV` y validación agrupada por niño; cuarto modelo (árbol o bosque); clustering de perfiles (K-Prototypes / Gower), opcional.
- **Step 8 – Interpretación:** evaluación **única** en el conjunto de prueba (31 niños) con intervalo de incertidumbre; interpretación de coeficientes.
- **Step 9 – Consolidación:** validar la lista de discrepancias con la nutricionista; informe final, ficha técnica y Gantt finales.

## Declaración de uso de IA generativa

Conforme a los lineamientos del curso, el equipo declara el uso de IA generativa:

- **Herramienta:** Claude (Anthropic), usado mediante **Claude Code**.
- **Usos:**
  - revisión de los notebooks anteriores (auditoría de pasos innecesarios, errores y fugas de información);
  - auditoría del consolidado de nutrición contra los 6 Excel originales;
  - diseño y reconstrucción del proyecto: estructura de carpetas, código de los notebooks y redacción de sus interpretaciones;
  - scripts `ejecutar_todo.py` y `actualizar_entregables.py`, y actualización de la ficha técnica, el Gantt y la presentación.
- **Justificación:** acelerar el trabajo operativo y detectar errores de ejecución. Las decisiones de análisis (objetivo, etiqueta, unidad de análisis, partición por niño, modelos) son del equipo y se mantuvieron sin cambios.
- **Validación:**
  - cada cifra citada en los notebooks se verifica con `assert` sobre la salida real;
  - el consolidado se comparó celda por celda con el anterior;
  - `ejecutar_todo.py` ejecuta todo desde cero y comprueba que los datos crudos no cambiaron y que no queden archivos huérfanos.

  El equipo revisa, ejecuta y puede explicar cada paso.
- Esta declaración cubre todos los notebooks y archivos del proyecto.

### Anexo: prompts principales

1. «quiero que actives el agente superpowers y me digas de que trata el trabajo y audites el procedimiento para simplificar pasos, corregir o limpiar pasos inutiles»
2. «entonces la conclusión está mal?»
3. «tu crees que los consolidados estén bien […]? toma en cuenta que viene de […] Datos TA - Bloque 2 Nutricion_IDs_2026.xlsx»
4. «pero todos las edades están desfasadas? o sea si no hay que asumir que el dataset y las mediciones se hicieron en esa fecha»
5. «segun la carpeta dataset […] y las reglas que te parece si hacemos de nuevo el proyecto, podemos tomar las ideas del pasado pero corrigiendo toda la estructura del proyecto en carpetas nuevas, las decisiones no deberían cambiar sino la ejecución y que sea correcto todo utiliza superpowers»
6. «que los nombres de los notebooks tengan los pasos» (con los 9 pasos de KDD de Fayyad)
7. «los notebooks deben tener explicación del código una breve descripción nomás»
8. «que sea declaración en cada notebook o en el readme»
9. «ok, arma el plan de implementación y continúa con la creación»
