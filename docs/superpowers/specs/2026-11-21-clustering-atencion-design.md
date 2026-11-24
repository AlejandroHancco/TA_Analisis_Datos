# Diseño: perfiles de atención de los NNA (clustering sobre la ficha nominal)

**Fecha:** 2026-11-21 · **Rama:** `feat/clustering-atencion` (parte de `feat/clustering`, commit `89bfb31`)

## 1. Intención

El TA necesita un objetivo de minería que **funcione con los datos**, que no sea circular, que le sirva al Puericultorio y que tenga respaldo en la literatura.

El clustering nutricional (z OMS) mostró que los niños forman un continuo sin grupos naturales: Hopkins igual al de una normal, BIC con k = 1 y silueta que no supera a la nula. En cambio, una prueba descartable sobre la **ficha nominal** (19 meses, unos 160 niños) sí mostró estructura:
- Hopkins 0,84 frente a 0,75 de la nula;
- silueta 0,235 frente a un percentil 95 nulo de 0,177 (*p* = 0,024);
- K-Means con k = 4 estable (ARI bootstrap 0,85).

**Objetivo general:** identificar perfiles de atención de los NNA del Puericultorio a partir de su trayectoria en la ficha nominal (ene-2025 a jul-2026), para detectar grupos que reciben un seguimiento parecido y señalar vacíos de atención.

**Objetivos específicos:**
1. Resumir la trayectoria de atención de cada niño en 19 meses.
2. Agruparlos con clustering y demostrar que los grupos son reales (frente a una referencia nula) y estables (bootstrap y muestra reservada).
3. Describir cada perfil con variables que no entraron al algoritmo: edad, sexo, UPE, hogar, educación y estado nutricional (z OMS).
4. Entregar a la institución los perfiles con brechas (por ejemplo, sin soporte psicoemocional o sin PTI).

## 2. Metas, no-metas y anti-metas

- **Metas:** perfiles estables e interpretables; validación más rigurosa que la de los papers de referencia; un entregable útil para el Puericultorio; un pipeline reproducible con `run_all.py`.
- **No-metas:** predecir resultados; afirmar causalidad; usar la nutrición como eje (queda como descripción secundaria).
- **Anti-metas** (fallaría aunque el código corra):
  - presentar los perfiles como **necesidades** del niño, cuando reflejan **cómo se atiende y se registra**;
  - presentar como descubrimiento un grupo que define una sola variable sí/no;
  - ocultar que la silueta absoluta es baja (< 0,25, "sin estructura sustancial" según Kaufman y Rousseeuw);
  - mezclar la edad en el algoritmo y después "descubrir" que los grupos son de edad.

## 3. Restricciones

- **Datos:** `datos/2_limpios/step3_panel.csv` (ficha limpia, niño × mes). Se excluyen las personas con más de 19 años en su último registro. 4 niños no tienen tiempo en el hogar.
- Se usan solo librerías del `requirements.txt`, salvo la que se indica en §6.
- Se mantiene la convención del proyecto: cada celda explicada, interpretación con cifras y `assert` que verifiquen esas cifras, `cifras_*.json` y `run_all.py` verde.
- **Privacidad:** no se publican listas con IDs fuera de `datos/4_resultados/`. Los IDs son seudónimos.

## 4. Enfoques considerados

| Enfoque | Qué es | Por qué sí o por qué no |
|---|---|---|
| **A. Perfiles de atención (ficha)** | Clustering de la trayectoria de atención en 19 meses | **Elegido.** Tiene estructura estable, no es circular, aporta a la institución y tiene respaldo en Delfabbro (2002), Hagaman (2010) y Raitasalo (2026) |
| B. Segmentación nutricional (z OMS) | Lo que hoy está en `feat/clustering` | No hay grupos naturales. Pasa a ser un **anexo** que justifica el cambio |
| C. Target supervisado (talla baja OMS ~ variables de la ficha) | Factores de riesgo | Señal débil: la atención no se asocia con los z (1 de 18 pruebas con *p* < 0,05) |

## 5. Decisiones tomadas

### Unidad y variables
- **Unidad:** el niño (última fila de la ficha para las variables de estado; proporciones sobre todos sus meses).
- **Variables del clustering:**

| Variable | Definición |
|---|---|
| `tiempo_hogar` | meses en el hogar en el último registro |
| `legal_definitiva` | 1 si la última situación legal es definitiva. Se **descarta** `legal_cambio` porque es redundante |
| `p_acompan`, `p_psicoter`, `p_taller` | proporción de meses con cada tipo de soporte psicoemocional |
| `p_sin_soporte` | proporción de meses sin ningún soporte |
| `p_salud_mental` | proporción de meses con atención en salud mental especializada |
| `p_pti_vencido`, `p_pti_no_tiene` | proporción de meses con PTI vencido o sin PTI |
| `discap_sev` | severidad máxima de discapacidad (0–3) |
| `anemia_alguna` | anemia en algún registro |

- **Fuera del algoritmo** (solo para describir): edad, edad de ingreso, sexo, UPE, nivel educativo, estudia, `p_estimul` (estimulación temprana, que en la práctica indica la edad), CEBE (redundante con discapacidad) y los z OMS.
- **Redundancia:** si dos variables del clustering tienen |r| > 0,8, se deja una y se documenta.

### Algoritmos
k = 2…6 en todos, salvo HDBSCAN.
- K-Means y Ward sobre variables estandarizadas (como Hagaman y Delfabbro);
- enlace promedio sobre **Gower**;
- **LCA** sobre las variables binarizadas (como Raitasalo). Las proporciones se binarizan con "≥ 50 % de los meses" y el tiempo en el hogar por su mediana;
- HDBSCAN como contraste basado en densidad.

### Validación
- Índices internos: silueta, Calinski-Harabasz, Davies-Bouldin y BIC/entropía en la LCA.
- **Dos referencias nulas**, con 200 repeticiones cada una:
  - columnas permutadas (conserva las proporciones de cada variable y rompe sus relaciones);
  - nula más exigente: remuestreo paramétrico que conserva las correlaciones (normal multivariada con la covarianza observada sobre las variables estandarizadas).
- **Estabilidad:** bootstrap por niño (200 repeticiones, ARI, criterio de Hennig).
- **Muestra reservada:** al estilo de Hagaman, partir 2/3 y 1/3, agrupar cada parte y comparar las asignaciones con ARI.
- **Tamaño mínimo de grupo:** si un grupo tiene menos de 8 niños (5 %), se marca como frágil y se reporta aparte. No se oculta.
- **Regla de elección:** la combinación más estable (ARI ≥ 0,75) que supere a ambas nulas, con el menor k entre las equivalentes. Si ninguna supera a la nula exigente, se dice explícitamente.

### Descripción, validación externa y entregable
- **Descripción de los perfiles:** edad, sexo, UPE, hogar (de las mediciones), educación y z OMS con su categoría. Se usan Kruskal-Wallis y χ², con advertencia de comparaciones múltiples.
- **Nutrición:** es una pregunta secundaria ("¿los perfiles difieren en exceso de peso o talla baja?"). Se reporta aunque salga nula.
- **Entregable:**
  - `datos/4_resultados/step6_perfiles_atencion.csv` (perfil por niño);
  - una tabla de brechas por perfil (% sin soporte, % sin PTI, % PTI vencido) para la institución.

### Cambios en notebooks y archivos
| Archivo | Cambio |
|---|---|
| Step 1 | Nuevo objetivo, con la secuencia avance → clustering nutricional → perfiles de atención |
| Step 2b | Unidad de análisis = niño de la ficha |
| Step 3 | Construir la tabla de trayectoria por niño (`step3_ninos_atencion.csv`) con las variables de §5 |
| Step 4 | Sección nueva: variables de atención, correlaciones, redundancia y Hopkins. La sección nutricional se mantiene como antecedente |
| Step 5 | Tabla de tareas: clustering de atención como tarea principal; auditoría y nutrición como secundarias |
| Step 6 | Clustering de atención (principal) |
| `notebooks/Anexo_Step6_clustering_nutricional.ipynb` | El Step 6 nutricional actual, sin cambios de contenido |
| `run_all.py`, `README.md`, `requirements.txt` | Nuevo orden y nueva dependencia |

### Referencias que se citan
- **Diseño:** Delfabbro, Barber & Cooper (2002); Hagaman et al. (2010); Raitasalo et al. (2026).
- **Método:** Gower (1971); Hennig (2007); Rousseeuw (1987); Kaufman & Rousseeuw (1990).
- **Contexto:** Johnson & Gunnar (2011) o van IJzendoorn et al. (2020); D.L. 1297 (Perú).
- **Nutrición:** Santra et al. (2023); Barouaca et al. (2021); Orden & Apezteguía (2014).

## 6. Lo que queda al implementador

- **Dependencia de la LCA:** `stepmix` (Python). Si no es compatible con las versiones fijadas, la LCA se reemplaza por una mezcla de Bernoulli propia o se omite, y se documenta.
- El k final y los nombres de los perfiles se deciden **después** de ver los resultados, con la regla de §5.
- La redacción de las interpretaciones, siguiendo las anti-metas de §2.
- `actualizar_entregables.py` sigue fuera del alcance (pendiente aparte).

## 7. Resultado de la implementación (2026-11-24)

- Con la validación de §5, **ningún clustering cumplió la regla**. El más estable (K-Means, k = 2; ARI 0,75) repetía la situación legal definitiva (ARI 0,75 con esa variable), y el clustering de secuencias mes a mes repetía el estado predominante (ARI 0,99). La prueba rápida inicial estaba inflada por variables duplicadas.
- Se evaluaron otras cuatro ideas con criterios fijados de antemano: PCA, predicción del cambio nutricional (R² ≈ 0), efecto del hogar (ICC ≈ 0) y reglas de asociación (solo reglas obvias). **El PCA fue la única que dio estructura real, estable y no trivial:** 2 dimensiones (permanencia e intensidad psicosocial) que superan el análisis paralelo, con Tucker 0,93 y 0,86.
- El Step 6 quedó como **selección de algoritmos**: se compara clustering y PCA, y se elige el PCA, con un mapa de la atención y un índice de prioridad (51 niños de larga permanencia y baja atención). El clustering nutricional quedó como anexo.
