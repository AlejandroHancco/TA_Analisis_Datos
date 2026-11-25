# TA E10 – Estructura de la atención y prioridad de seguimiento (Puericultorio Pérez Araníbar)

**Curso:** Análisis de Datos 1INF03 (PUCP), 2026-2 · **Equipo:** E10 · **Entrega:** final, ciclo KDD completo (Steps 1–9)

El Puericultorio registra cada mes, en la ficha nominal, la atención que recibe cada NNA (soporte psicoemocional, salud mental,
plan de trabajo individual, situación legal) y, aparte, sus mediciones de peso y talla. Este proyecto:
1. **descubre cómo se organiza la atención** registrada en 19 meses de ficha y construye un **índice de prioridad** de seguimiento;
2. describe el **estado nutricional** con puntajes z de la OMS y prueba si se asocia con la atención;
3. **audita** las evaluaciones en que la ficha y la clasificación OMS de las mediciones no coinciden.

Se siguen los nueve pasos del proceso KDD de Fayyad, Piatetsky-Shapiro y Smyth (1996); cada notebook corresponde a un paso.

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
├── src/atencion.py            recalcula el índice de prioridad con meses nuevos de ficha (Step 9)
├── datos/
│   ├── 0_crudos/              originales, solo lectura (hashes.json verifica que no cambien)
│   │   └── referencias/oms_lms/   tablas LMS oficiales de la OMS (who.int): 0–5 años (2006) y 5–19 años (2007)
│   ├── 1_consolidados/        Step2a: Bloque 2 consolidado desde los 6 Excel mensuales
│   ├── 2_limpios/             Step3: ficha limpia, Bloque 2 limpio, mediciones, evaluaciones, trayectoria de atención por niño
│   ├── 3_transformados/       Step4: variables de atención por niño, mediciones con z y estado nutricional por niño
│   └── 4_resultados/          Steps 5–9 y anexo: auditoría, comparación de métodos, modelo PCA, puntajes, lista de prioridad, cifras_*.json
├── notebooks/                 un notebook por paso KDD (ver orden)
├── figuras/                   prefijo = paso que la genera
├── entregables/               informe final (.docx), presentación final (.pptx), ficha técnica y Gantt finales (.xlsx)
└── fuentes/                   PDF de las referencias (ver fuentes/README.md)
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
| 8 | `Step6_Seleccion_de_Algoritmos` | 6 | Compara clustering (K-Means, Ward, Gower, LCA, HDBSCAN, secuencias) y **PCA** con reglas fijadas antes; elige el PCA |
| 9 | `Step7_Mineria_de_Datos` | 7 | Ajusta el PCA, guarda el modelo, calcula puntajes, cuadrantes e índice de prioridad; robustez bootstrap |
| 10 | `Step8_Interpretacion` | 8 | Interpreta los cuadrantes, su relación con edad, UPE, sexo y nutrición; **evaluación comparativa de los modelos**; iteraciones |
| 11 | `Step9_Consolidacion` | 9 | Función reutilizable (`src/atencion.py`), lista de prioridad, hallazgos y acciones, conclusiones |

Cada notebook explica cada celda de código, interpreta sus resultados y verifica con `assert` las cifras que cita.

## Cómo ejecutar

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python run_all.py                 # ≈8 min; se detiene ante cualquier error o assert fallido
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
  de los meses o más sin soporte psicoemocional, el 63 % sin PTI y ninguno recibió salud mental especializada. 23 de ellos quedan en prioridad en al menos el 80 % de 300 remuestreos (`step9_lista_prioridad.csv`).
- **La permanencia difiere entre UPE** (*p* < 0,001); la intensidad psicosocial no depende de la edad ni de la UPE, y es algo mayor en varones (*p* = 0,01).
- **Nutrición:** la población pesa más y mide menos de lo esperado (z de IMC +0,98; z de talla −0,94). El exceso de peso (≈ 40 %) es igual en todos los
  hogares, sexos, edades y perfiles de atención: es un problema **institucional**, no focalizado.
- **Auditoría:** la ficha y la clasificación OMS concuerdan en el 68,8 % de las evaluaciones, y la institución usa cortes más laxos que la OMS.

## Entregables

En `entregables/`:
- `Informe_Final_TA_E10.docx`: informe por pasos KDD, con figuras, tablas, referencias y anexos.
- `Presentacion_Final_TA_E10.pptx`: 17 láminas con notas para el expositor.
- `FichaTecnica_E10_final.xlsx` y `Gantt_E10_final.xlsx`: ficha técnica y diagrama de Gantt finales.

Los nombres de los integrantes aparecen como `[Nombre]` junto a cada código: hay que completarlos antes de entregar.

## Referencias

Las citas aparecen en los notebooks como (Autor, año). Los PDF se guardan en `fuentes/`, con el nombre indicado en `fuentes/README.md`.

**Proceso KDD**
- Fayyad, U., Piatetsky-Shapiro, G., & Smyth, P. (1996). From data mining to knowledge discovery in databases. *AI Magazine, 17*(3), 37–54.

**Referencias de crecimiento y estado nutricional**
- WHO Multicentre Growth Reference Study Group. (2006). WHO Child Growth Standards based on length/height, weight and age. *Acta Paediatrica, 95*(S450), 76–85.
- de Onis, M., Onyango, A. W., Borghi, E., Siyam, A., Nishida, C., & Siekmann, J. (2007). Development of a WHO growth reference for school-aged children and adolescents. *Bulletin of the World Health Organization, 85*(9), 660–667.
- Cole, T. J., & Green, P. J. (1992). Smoothing reference centile curves: The LMS method and penalized likelihood. *Statistics in Medicine, 11*(10), 1305–1319.
- Santra, A., Rai, S., Misra, P., Yadav, K., Goswami, K., & Kaur, G. (2023). Comparison of different anthropometric indicators for assessment of nutritional status among adolescent girls in an urban resettlement colony in New Delhi: A cross-sectional study. *Cureus, 15*(4), e37242. https://doi.org/10.7759/cureus.37242
- Barouaca, H., Ben Loubir, D., El Bouhali, B., Tachfouti, N., & El Midaoui, A. (2021). The role of body mass index-for-age in the assessment of acute malnutrition and obesity in Moroccan hospitalized children. *Journal of Applied Pharmaceutical Science, 11*(7), 98–104. https://doi.org/10.7324/JAPS.2021.110710
- Orden, A. B., & Apezteguía, M. C. (2014). Weight and height centiles of Argentinian children and adolescents: A comparison with WHO and national growth references. *Annals of Human Biology*. https://doi.org/10.3109/03014460.2014.970576
- Johnson, D. E., & Gunnar, M. R. (2011). Growth failure in institutionalized children. *Monographs of the Society for Research in Child Development, 76*(4), 92–126.

**Niños en acogimiento residencial**
- Delfabbro, P. H., Barber, J. G., & Cooper, L. (2002). Children entering out-of-home care in South Australia: Baseline analyses for a 3-year longitudinal study. *Children and Youth Services Review, 24*(12), 917–932.
- Hagaman, J. L., Trout, A. L., Chmelka, M. B., Thompson, R. W., & Reid, R. (2010). Risk profiles of children entering residential care: A cluster analysis. *Journal of Child and Family Studies, 19*, 525–535. https://doi.org/10.1007/s10826-009-9325-3
- Raitasalo, K., Kosonen, J., Plaami, E., & Kuusisto, K. (2026). A typology of teen-aged children in out-of-home care: A register-based cohort study. *Nordic Social Work Research*. https://doi.org/10.1080/2156857X.2026.2730122

**Métodos**
- Horn, J. L. (1965). A rationale and test for the number of factors in factor analysis. *Psychometrika, 30*(2), 179–185.
- Lorenzo-Seva, U., & ten Berge, J. M. F. (2006). Tucker's congruence coefficient as a meaningful index of factor similarity. *Methodology, 2*(2), 57–64.
- Hopkins, B., & Skellam, J. G. (1954). A new method for determining the type of distribution of plant individuals. *Annals of Botany, 18*(2), 213–227.
- Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics, 20*, 53–65.
- Kaufman, L., & Rousseeuw, P. J. (1990). *Finding groups in data: An introduction to cluster analysis*. Wiley.
- Hennig, C. (2007). Cluster-wise assessment of cluster stability. *Computational Statistics & Data Analysis, 52*(1), 258–271.
- Gower, J. C. (1971). A general coefficient of similarity and some of its properties. *Biometrics, 27*(4), 857–871.
- Campello, R. J. G. B., Moulavi, D., & Sander, J. (2013). Density-based clustering based on hierarchical density estimates. En *Advances in Knowledge Discovery and Data Mining (PAKDD 2013)* (pp. 160–172). Springer.
- Abbott, A., & Tsay, A. (2000). Sequence analysis and optimal matching methods in sociology. *Sociological Methods & Research, 29*(1), 3–33.

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
