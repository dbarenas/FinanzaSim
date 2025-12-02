# FinanzaSim

Simulador multijugador de análisis financiero, reescrito íntegramente en **Python**. El proyecto incluye motor económico, orquestación de partidas, demo por consola y pruebas automatizadas listos para ejecutarse localmente.

## Requisitos

- Python **3.11+**
- `pip` (para instalar dependencias listadas en `requirements.txt`)

## Instalación y despliegue local (paso a paso)

1) **Clonar o descargar** el repositorio.
2) **Crear y activar** un entorno virtual (recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```
3) **Instalar dependencias** (pruebas y notebook interactivo):
   ```bash
   pip install -r requirements.txt
   ```
   > Si solo quieres ejecutar la demo por consola, basta con Python estándar; para el notebook necesitas `pandas`, `matplotlib` y `jupyter` (ya listados en `requirements.txt`).
4) **Ejecutar la demo de consola** para cerrar un trimestre y visualizar métricas:
   ```bash
   python scripts/console_demo.py
   ```
5) **Ejecutar las pruebas unitarias**:
   ```bash
   pytest
   ```

## Explicación completa del sistema

### Vista general

- **Objetivo**: simular la gestión financiera de varias empresas (jugadores) en ciclos trimestrales. Cada ciclo calcula demanda, P&L, balance y ratios de liquidez/rentabilidad.
- **Componentes clave**:
  - **Motor económico**: implementa la fórmula de demanda, márgenes, impuestos y liquidez.
  - **Servicio de sesión**: orquesta cierres de trimestre para todas las empresas en una partida y persiste los resultados en un repositorio intercambiable (en memoria por defecto).
  - **Batería CFA-style**: 20 preguntas de decisión con 3 opciones que ajustan las decisiones de producción, precio y marketing según la respuesta elegida cada trimestre.
  - **Demo por consola**: ejecuta un cierre de trimestre y muestra el estado financiero actualizado.
  - **Pruebas**: validan escenarios de rentabilidad y estrés de liquidez.

### Flujo de juego y lógica

1. **Estado inicial**: cada empresa parte con efectivo, inventario y patrimonio definidos en `SessionState`.
2. **Decisiones del trimestre**: producción, precio de venta e inversión en marketing se registran en `CompanyDecisions`.
3. **Pregunta táctica CFA-style**: al comenzar el trimestre, `SessionService.assign_quarter_questions` asigna a cada empresa una pregunta aleatoria (de un banco de 20). La empresa responde eligiendo entre 3 opciones; la opción seleccionada ajusta las decisiones del trimestre (multiplicadores y deltas sobre producción, precio y marketing).
4. **Cierre (`simulate_quarter`)**:
   - Calcula la **demanda realizada** considerando precio de referencia, elasticidad y efecto de marketing.
   - Determina **unidades vendidas** respetando inventario inicial + producción.
   - Construye **Estado de Resultados** (ingresos, COGS, utilidad bruta, gastos fijos + marketing, EBIT, impuestos y utilidad neta).
   - Actualiza **Balance** (efectivo, inventario, patrimonio) y aplica deuda de corto plazo si el efectivo queda negativo.
   - Deriva **ratios**: margen neto y razón circulante.
5. **Persistencia del trimestre**: `SessionService` crea un nuevo `QuarterResult` con las cifras y limpia las decisiones para el siguiente ciclo.

### Módulos y archivos

- `finanzasim/constants.py`: constantes económicas (precio de referencia, elasticidad, costo por unidad, gastos fijos, tasa impositiva, demanda base y efecto de marketing).
- `finanzasim/financial_calculator.py`:
  - `simulate_quarter` calcula demanda, P&L, balance, deuda y ratios.
  - `compute_current_ratio` y `compute_net_margin` exponen métricas reutilizables.
- `finanzasim/session_service.py`:
  - `InMemorySessionRepository` almacena sesiones en memoria (intercambiable por DB en el futuro).
  - `SessionService` centraliza el cierre de trimestre por empresa y guarda los resultados.
- `finanzasim/cfa_questions.py`: banco de 20 preguntas estilo CFA con 3 opciones cada una, utilidades para elegir preguntas aleatorias (`pick_random_question`) y aplicar el impacto de la opción seleccionada (`apply_option_impact`).
- `scripts/console_demo.py`: crea una sesión de muestra, aplica decisiones predefinidas, cierra Q1 y presenta métricas clave en consola.
- `notebooks/analisis_financiero.py`: notebook (estilo Jupytext) listo para calcular FM, CC, NOF, márgenes, DuPont, EVA, 20 escenarios de decisiones y un dashboard trimestral de KPIs con gráficas automáticas.
- `tests/test_financial_calculator.py`: casos de prueba `pytest` que verifican cálculos de ingresos, utilidades y manejo de liquidez/deuda.
- `requirements.txt`: dependencias para pruebas y notebook (`pytest`, `pandas`, `matplotlib`, `jupyter`).

### Notebook interactivo de análisis financiero

1. Instala dependencias (incluyen `pandas`, `matplotlib` y `jupyter`):
   ```bash
   pip install -r requirements.txt
   ```
2. Abre el notebook desde VS Code (celdas `# %%`) o con Jupyter:
   ```bash
   jupyter notebook notebooks/analisis_financiero.py
   ```
3. En la sección **Datos de entrada**, ajusta el diccionario `inputs` para recalcular automáticamente FM, CC, NOF, márgenes, ROA/ROE, DuPont y EVA.
4. En **Escenarios listos para jugar (20 casos)** modifica la lista `SCENARIOS` para probar decisiones de producción, precio y marketing. La celda mostrará una tabla y gráficas comparando ingresos, utilidad neta y liquidez de cada caso.
5. En **Dashboard trimestral estilo KPI** puedes ajustar la lista `TIMELINE_DECISIONS` para ver la evolución por trimestre de ingresos, ROI, flujo de caja, precio, EBIT/gross profit y D/E, todo en un panel de 6 gráficas.
6. Si quieres incorporar la dinámica de preguntas en un frontend, invoca `assign_quarter_questions(session_id)` al empezar el trimestre, presenta el `prompt` y las 3 `options` al usuario, guarda el `selected_option_id` en la compañía y luego ejecuta `close_quarter(session_id)` para que el impacto se refleje en el cálculo.

### Cómo adaptar a otros frontends o APIs

- **Frontends web/JS**: pueden invocar `SessionService.close_quarter(session_state)` desde un endpoint FastAPI o similar, serializando/deserializando las dataclasses.
- **Persistencia externa**: reemplazar `InMemorySessionRepository` por un adaptador a DynamoDB/Firestore manteniendo los métodos `get_by_id` y `save`.
- **IA o guías de trimestre**: tras cada cierre, un servicio externo puede consumir el `QuarterResult` para generar mensajes y guardarlos en el equivalente de `agentChat`.

## Estructura

- `finanzasim/constants.py`: Constantes del modelo de simulación.
- `finanzasim/financial_calculator.py`: Funciones de cálculo (`simulate_quarter`) y razones financieras.
- `finanzasim/session_service.py`: Servicio de sesión y repositorio en memoria para orquestar cierres de trimestre.
- `scripts/console_demo.py`: Demo por consola que cierra un trimestre y muestra métricas clave.
- `tests/`: Pruebas unitarias con `pytest`.

## Notas de arquitectura

- `simulate_quarter` calcula demanda, ingresos, EBITDA, impuestos, utilidades, flujo de caja ajustado por deuda de corto plazo y ratios de liquidez/margen.
- `SessionService` centraliza el flujo de cierre de trimestre y actualiza el estado de cada empresa, limpiando las decisiones después de aplicar el cálculo.
- El `InMemorySessionRepository` es un reemplazo sencillo de persistencia para poder intercambiarlo por Firestore/DynamoDB manteniendo las mismas firmas de `get_by_id`/`save`.
