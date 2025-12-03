## 📊 Especificación: Simulador Multijugador de Análisis Financiero (FinanzaSim)

El siguiente documento estructura la arquitectura, lógica de negocio y características clave para el desarrollo del simulador **FinanzaSim**, utilizando un *stack* centrado en **Google Cloud (Firebase, Gemini)** y tecnologías web.

-----

## 1\. Objetivo del Proyecto

Desarrollar una aplicación *full-stack* que simule la gestión financiera de empresas en un entorno competitivo por trimestres. Los jugadores (CEO) toman decisiones clave (producción, precio y marketing), reciben análisis de IA y compiten por liderazgo financiero.

-----

## 2\. Arquitectura de Lógica de Negocio y Datos (Backend Lógico)

### 2.1. Stack de Lógica de Negocio

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Lógica de Negocio** | **JavaScript** (Integrada en el Frontend) | Ejecución del modelo económico, cálculos de estados financieros, y función de **cierre de trimestre** (`closeQuarter()`). Se ejecuta de forma descentralizada y segura a nivel cliente. |
| **Base de Datos** | **Google Firestore** | Persistencia de sesiones, estados financieros históricos de cada jugador y registros de *chat* del Agente en tiempo real. |
| **Integración AI** | **API de Gemini** | Generación de **diagnósticos** y **directivas financieras** personalizados para el jugador al inicio de cada trimestre. |

-----

### 2.2. Persistencia de Datos y Modelo de Sesión

**Ruta de Almacenamiento:** `/artifacts/{appId}/public/data/finance_games/{sessionId}`

**Estructura del Documento `sessionId` (Ejemplo):**

```json
{
  "gameCode": "XYZ123",
  "gameStatus": "Q1", // Lobby, Q1, Q2, Q3, Q4, Finished
  "currentQuarter": 1,
  "lastUpdateTime": 1733054478, // Marca de tiempo (Unix)
  "companies": {
    "user123": {
      "name": "Alpha Corp",
      "financials": [ // Array de estados históricos, empezando por Q0 (Inicial)
        { "quarter": 0, "cash": 50000, "inventory": 1000, "equity": 50000, ... },
        { "quarter": 1, "cash": 45000, "inventory": 1200, "equity": 52000, ... }
      ],
      "decisions": { // Decisiones para el trimestre actual
        "production": 1500,
        "price": 55,
        "marketing": 2000
      },
      "agentChat": [ /* Historial de mensajes del Agente de IA */ ]
    },
    // ... otros jugadores
  }
}
```

-----

### 2.3. Motor de Simulación Financiera (Función `closeQuarter()`)

Esta función es clave y debe ser ejecutada de manera atómica y segura por el **Host** de la sesión al final de cada ciclo de 5 minutos.

#### 2.3.1. Variables de Simulación (Constantes)

| Constante | Valor | Descripción |
| :--- | :--- | :--- |
| $\text{CostPerUnit}$ | $25 | Costo de bienes vendidos por unidad. |
| $\text{FixedOpEx}$ | $10,000 | Gastos operativos fijos (alquiler, nóminas básicas). |
| $\text{TaxRate}$ | 20% | Tasa de impuestos corporativos. |
| $\text{Demanda Base}$ | 1200 unidades | Demanda inicial del mercado. |
| $\text{Efecto Marketing}$ | 1 unidad / $10 | Cada $10 de marketing aumenta la demanda en 1 unidad. |
| $\text{Elasticidad del Precio}$ | ±20 unidades / $1 | Por cada $1 de diferencia con el precio de referencia ($50). |

#### 2.3.2. Flujo de Cálculo Detallado

**1. Demanda y Ventas:**

  * **Efecto Precio:** $(\text{Precio Referencia} (\$50) - \text{Precio de Venta}) \times 20$
  * **Efecto Marketing:** $\text{Marketing} / 10$
  * **Demanda Realizada:** $$\text{Máx}(0, 1200 + (\text{Marketing} / 10) + ((\$50 - \text{Precio}) \times 20))$$
  * **Unidades Vendidas:** $$\text{Mín}(\text{Demanda Realizada}, \text{Producción} + \text{Inventario Anterior})$$

**2. Estado de Resultados (P\&L):**

| Elemento | Fórmula |
| :--- | :--- |
| $\text{Ingresos}$ | $\text{Unidades Vendidas} \times \text{Precio}$ |
| $\text{COGS}$ | $\text{Unidades Vendidas} \times \text{CostPerUnit} (\$25)$ |
| $\text{Utilidad Bruta}$ | $\text{Ingresos} - \text{COGS}$ |
| $\text{Gastos Operativos}$ | $\text{FixedOpEx} (\$10,000) + \text{Marketing}$ |
| $\text{EBIT}$ | $\text{Utilidad Bruta} - \text{Gastos Operativos}$ |
| $\text{Impuestos}$ | $\text{Máx}(0, \text{EBIT} \times \text{TaxRate} (20\%))$ |
| $\text{Utilidad Neta}$ | $\text{EBIT} - \text{Impuestos}$ |

**3. Balance General (Flujo de Caja y Patrimonio):**

| Elemento | Fórmula |
| :--- | :--- |
| $\text{Cambio en Efectivo}$ | $\text{Ingresos} - (\text{Producción} \times \text{CostPerUnit}) - \text{Gastos Operativos}$ |
| $\text{Efectivo Nuevo}$ | $\text{Efectivo Anterior} + \text{Cambio en Efectivo}$ |
| $\text{Inventario Nuevo}$ | $\text{Inventario Anterior} + \text{Producción} - \text{Unidades Vendidas}$ |
| $\text{Patrimonio Nuevo}$ | $\text{Patrimonio Anterior} + \text{Utilidad Neta}$ |

**4. Ajuste de Liquidez (Balance Contable):**

  * Si $\text{Efectivo Nuevo} < 0$, la empresa incurre en **Deuda a Corto Plazo**.
  * $\text{Deuda a Corto Plazo} = \text{Máx}(0, -\text{Efectivo Nuevo})$
  * $\text{Efectivo Nuevo (Ajustado)} = \text{Máx}(0, \text{Efectivo Nuevo})$

-----

### 2.4. Agente de Análisis (Integración Gemini)

  * **Trigger:** Invocación automática al inicio de cada nuevo trimestre (después de que `closeQuarter()` finaliza y avanza el estado).
  * **Prompt (Input):** Debe incluir el resumen de los resultados financieros completos del trimestre anterior, incluyendo:
      * $\text{Ingresos}$ y $\text{Utilidad Neta}$
      * $\text{Razón Circulante}$ y $\text{Margen Neto}$
      * $\text{Decisiones tomadas}$ (Producción, Precio, Marketing).
  * **Output (Respuesta):** Generar un **diagnóstico** conciso de la salud financiera (enfocado en liquidez y rentabilidad) y una **directiva** o pregunta clave estratégica para la toma de decisiones del próximo trimestre.

-----

## 3\. Características Clave del Frontend y UI

### 3.1. Gestión de Sesiones y Autenticación

  * **Autenticación:** Utilizar **Autenticación Anónima de Firebase** o mediante el *token* provisto por el entorno (`__initial_auth_token`).
  * **Lobby:** Interfaz simple para **Crear Sesión** (el creador es el **Host**) o **Unirse a Sesión** (usando el código `gameCode`).

### 3.2. Ciclo de Juego y Temporización

  * **Estructura:** Juego de **4 Trimestres** (Q1 a Q4).
  * **Duración:** Cada trimestre dura **5 minutos** (300 segundos).
  * **Visualización:** **Cronómetro** visible en la UI que muestra el tiempo restante para el cierre.

### 3.3. Interfaz de Decisiones y Estado Financiero

  * **Input de Decisiones:** Formulario visible con campos para las tres decisiones clave del trimestre:
    1.  **Unidades a Producir**
    2.  **Precio Unitario de Venta**
    3.  **Inversión en Marketing**
  * **Visualización de Datos:** Mostrar el estado financiero del trimestre más reciente (Q anterior) en formato de tablas:
      * **Balance General:** $\text{Efectivo}$, $\text{Inventario}$, $\text{Deuda}$, $\text{Patrimonio}$.
      * **Estado de Resultados (P\&L):** $\text{Ingresos}$, $\text{COGS}$, $\text{EBIT}$, $\text{Utilidad Neta}$.
      * **Ratios Clave:** $\text{Razón Circulante}$ ($\text{Activo Circulante} / \text{Pasivo Circulante}$) y $\text{Margen Neto}$ ($\text{Utilidad Neta} / \text{Ingresos}$).

<div align="center">

![Ejemplo de dashboard financiero con KPIs](https://files.oaiusercontent.com/file-MudlEayMoL73wYXGoESbsFnH?se=2024-05-29T20%3A10%3A42Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image&s... "Dashboard financiero con indicadores clave")

</div>

*Imagen 1: Ejemplo visual de dashboard financiero con indicadores clave, gráficos de ingresos, flujos de caja, rentabilidad, precio, EBIT y ratios.*

### 3.4. Comparación de Rendimiento (Leaderboard)

  * **Requerimiento:** Una sección de la UI debe comparar el desempeño de todas las empresas.
  * **Métricas Clave:**
      * Nombre de la Empresa
      * **Utilidad Neta Acumulada** (Métrica principal de rentabilidad)
      * **Patrimonio Neto Final** (Métrica de valor a largo plazo)
      * **Razón Circulante Actual** (Métrica de liquidez)
  * **Visualización:** Presentar los datos en formato de tabla o gráfico de barras comparativo.
