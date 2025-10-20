"""
LABORATORIO VIRTUAL - QUÍMICA ANALÍTICA
Práctica: Determinación de Hierro en Vinos por Absorción Atómica
Curso: QU-0301 Análisis Cuantitativo
Universidad de Costa Rica

Profesor: Douglas Venegas González
douglas.venegas@ucr.ac.cr

INSTALACIÓN:
pip install streamlit

EJECUCIÓN:
streamlit run Lab_virtual.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Lab Virtual - Fe en Vinos",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DATOS DE LOS VINOS (con concentraciones reales de Fe)
# ============================================================================

VINOS_DATABASE = {
    "Vino Tinto Reserva": {
        "imagen": "🍷",
        "color": "#8B0000",
        "concentracion_fe": 8.5,  # mg/L real en el vino
        "descripcion": "Vino tinto con cuerpo, crianza en barrica",
        "fd_sugerido": 2
    },
    "Vino Blanco Seco": {
        "imagen": "🥂",
        "color": "#FFD700",
        "concentracion_fe": 2.8,  # mg/L
        "descripcion": "Vino blanco ligero, afrutado",
        "fd_sugerido": 1
    },
    "Vino Rosado": {
        "imagen": "🌸",
        "color": "#FF69B4",
        "concentracion_fe": 4.2,  # mg/L
        "descripcion": "Vino rosado fresco y aromático",
        "fd_sugerido": 1
    },
    "Vino Tinto Joven": {
        "imagen": "🍇",
        "color": "#DC143C",
        "concentracion_fe": 12.3,  # mg/L
        "descripcion": "Vino tinto joven, intenso",
        "fd_sugerido": 3
    }
}

# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

if 'masa_sal_mohr' not in st.session_state:
    st.session_state.masa_sal_mohr = None

if 'volumen_aforo_patron' not in st.session_state:
    st.session_state.volumen_aforo_patron = None

if 'patrones_preparados' not in st.session_state:
    st.session_state.patrones_preparados = []

if 'vino_seleccionado' not in st.session_state:
    st.session_state.vino_seleccionado = None

if 'alicuota_vino' not in st.session_state:
    st.session_state.alicuota_vino = None

if 'volumen_aforo_muestra' not in st.session_state:
    st.session_state.volumen_aforo_muestra = None

if 'mediciones_aa' not in st.session_state:
    st.session_state.mediciones_aa = {}

# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def calcular_concentracion_patron_madre(masa_sal, volumen_aforo):
    """
    Calcula la concentración de Fe en la solución patrón madre
    Sal de Mohr: (NH4)2Fe(SO4)2·6H2O
    MM = 392.14 g/mol
    MM Fe = 55.845 g/mol
    """
    if masa_sal is None or volumen_aforo is None:
        return None
    
    mm_sal = 392.14  # g/mol
    mm_fe = 55.845   # g/mol
    
    # Moles de sal
    moles_sal = masa_sal / mm_sal
    
    # Moles de Fe (1:1)
    moles_fe = moles_sal
    
    # Masa de Fe
    masa_fe = moles_fe * mm_fe  # g
    masa_fe_mg = masa_fe * 1000  # mg
    
    # Concentración en mg/L
    conc_mg_L = masa_fe_mg / (volumen_aforo / 1000)
    
    return conc_mg_L

def calcular_concentracion_patron(conc_madre, alicuota, volumen_aforo):
    """Calcula la concentración de un patrón por dilución"""
    if conc_madre is None:
        return None
    return (conc_madre * alicuota) / volumen_aforo

def generar_absorbancia(concentracion, curva_lineal=True):
    """
    Genera absorbancia basada en Ley de Beer
    Si curva_lineal=False, añade desviaciones
    """
    # Coeficiente de absorción típico para Fe a 248.3 nm
    k = 0.082  # L/(mg·cm)
    
    if curva_lineal:
        # Ley de Beer perfecta con pequeño ruido
        abs_teorica = k * concentracion
        ruido = np.random.normal(0, 0.002)
        return abs_teorica + ruido
    else:
        # Con desviaciones (concentraciones fuera de rango óptimo)
        abs_teorica = k * concentracion
        # Añadir desviaciones no lineales
        desviacion = np.random.normal(0, 0.02) + 0.01 * (concentracion - 3)**2
        return abs_teorica + desviacion

def calcular_fd_muestra(alicuota, volumen_aforo):
    """Calcula el factor de dilución de la muestra"""
    if alicuota is None or volumen_aforo is None:
        return None
    return volumen_aforo / alicuota

def verificar_rango_optimo(concentracion):
    """Verifica si la concentración está en rango óptimo (1-5 mg/L)"""
    return 1.0 <= concentracion <= 5.0

# ============================================================================
# ESTILOS CSS
# ============================================================================

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .wine-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ddd;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .wine-card:hover {
        transform: scale(1.05);
        border-color: #DC143C;
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.3);
    }
    .wine-card.selected {
        border-color: #DC143C;
        background-color: #FFF5F5;
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.3);
    }
    .section-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #DC143C;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🍷 LABORATORIO VIRTUAL - QUÍMICA ANALÍTICA</h1>
            <h3>Determinación de Hierro en Vinos por Absorción Atómica</h3>
            <p>QU-0301 Análisis Cuantitativo | Universidad de Costa Rica</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Escudo_UCR.svg/1200px-Escudo_UCR.svg.png", width=150)
        st.markdown("### 👨‍🏫 Información del Curso")
        st.info("""
        **Profesor:**  
        Douglas Venegas González  
        douglas.venegas@ucr.ac.cr
        
        **Curso:**  
        QU-0301 Análisis Cuantitativo
        """)
        
        st.markdown("### 📚 Navegación")
        pagina = st.radio(
            "Seleccione una etapa:",
            [
                "🏠 Inicio",
                "1️⃣ Preparación Patrón Madre",
                "2️⃣ Curva de Calibración", 
                "3️⃣ Preparación de Muestra",
                "4️⃣ Medición AA",
                "5️⃣ Resultados"
            ],
            key="navegacion"
        )

    # Páginas
    if pagina == "🏠 Inicio":
        mostrar_inicio()
    elif pagina == "1️⃣ Preparación Patrón Madre":
        mostrar_patron_madre()
    elif pagina == "2️⃣ Curva de Calibración":
        mostrar_curva_calibracion()
    elif pagina == "3️⃣ Preparación de Muestra":
        mostrar_preparacion_muestra()
    elif pagina == "4️⃣ Medición AA":
        mostrar_medicion_aa()
    elif pagina == "5️⃣ Resultados":
        mostrar_resultados()

# ============================================================================
# PÁGINAS
# ============================================================================

def mostrar_inicio():
    st.markdown("## 🎯 Objetivo de la Práctica")
    st.markdown("""
    <div class="section-box">
    Determinar la concentración de hierro (Fe) en diferentes muestras de vino 
    mediante <b>Espectroscopía de Absorción Atómica (AA)</b>, utilizando el 
    método de curva de calibración.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔬 Fundamento Teórico")
        st.markdown("""
        La **Absorción Atómica** es una técnica analítica que mide la absorción 
        de radiación electromagnética por átomos libres en estado fundamental.
        
        **Ley de Beer-Lambert:**
        ```
        A = ε × b × c
        ```
        Donde:
        - A = Absorbancia
        - ε = Coeficiente de absorción molar
        - b = Longitud del camino óptico
        - c = Concentración
        
        **Longitud de onda para Fe:** 248.3 nm
        """)
    
    with col2:
        st.markdown("### 📋 Procedimiento General")
        st.info("""
        **Etapas del análisis:**
        
        1. **Preparación de Patrón Madre**
           - Pesar Sal de Mohr
           - Preparar solución patrón de Fe
        
        2. **Curva de Calibración**
           - Preparar 3-7 patrones (1-5 mg/L)
           - Medir absorbancias
        
        3. **Preparación de Muestra**
           - Seleccionar vino
           - Realizar dilución apropiada
        
        4. **Medición por AA**
           - Determinar absorbancia
        
        5. **Cálculos y Resultados**
        """)

    st.markdown("### 🍷 Muestras de Vino Disponibles")
    
    cols = st.columns(4)
    
    for i, (nombre, datos) in enumerate(VINOS_DATABASE.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="wine-card">
                <div style="font-size: 48px;">{datos['imagen']}</div>
                <h4>{nombre}</h4>
                <p style="color: {datos['color']}; font-weight: bold;">
                    {datos['descripcion']}
                </p>
            </div>
            """, unsafe_allow_html=True)

def mostrar_patron_madre():
    st.markdown("## 1️⃣ Preparación de Solución Patrón Madre de Fe")
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Preparar una solución patrón madre de Fe a partir de Sal de Mohr 
    [(NH₄)₂Fe(SO₄)₂·6H₂O] para posteriormente preparar los patrones de la curva de calibración.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎮 Simulador de Pesado y Aforo")
    
    # Aquí iría el HTML del simulador de pesado (lo crearemos después)
    st.info("🖱️ **Instrucciones:** Usa el simulador para pesar la Sal de Mohr y aforar en el balón")
    
    # Simulador simplificado con inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚖️ Pesado de Sal de Mohr")
        masa_pesada = st.number_input(
            "Masa pesada (g):",
            min_value=0.20,
            max_value=5.00,
            value=None,
            step=0.0001,
            format="%.4f",
            help="Rango recomendado: 0.2 - 5.0 g"
        )
        
        if masa_pesada:
            st.success(f"✅ Masa registrada: {masa_pesada:.4f} g")
            st.session_state.masa_sal_mohr = masa_pesada
    
    with col2:
        st.markdown("#### 🧪 Aforo del Balón")
        volumen_balon = st.selectbox(
            "Volumen del balón aforado (mL):",
            [None, 50, 100, 250, 500, 1000],
            format_func=lambda x: "Seleccione..." if x is None else f"{x} mL"
        )
        
        if volumen_balon:
            st.success(f"✅ Volumen seleccionado: {volumen_balon} mL")
            st.session_state.volumen_aforo_patron = volumen_balon
    
    # Cálculos
    if st.session_state.masa_sal_mohr and st.session_state.volumen_aforo_patron:
        st.markdown("---")
        st.markdown("### 🧮 Cálculos Automáticos")
        
        conc_patron_madre = calcular_concentracion_patron_madre(
            st.session_state.masa_sal_mohr,
            st.session_state.volumen_aforo_patron
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Masa Sal de Mohr", f"{st.session_state.masa_sal_mohr:.4f} g")
        
        with col2:
            st.metric("Volumen Aforo", f"{st.session_state.volumen_aforo_patron} mL")
        
        with col3:
            st.metric(
                "Concentración Patrón Madre",
                f"{conc_patron_madre:.2f} mg/L",
                help="Concentración de Fe en la solución patrón madre"
            )
        
        # Verificar si es adecuado para hacer patrones
        if conc_patron_madre < 50:
            st.warning("⚠️ La concentración del patrón madre es baja. Será difícil preparar patrones en el rango 1-5 mg/L")
        elif conc_patron_madre > 500:
            st.info("💡 La concentración del patrón madre es alta. Necesitarás alícuotas pequeñas para los patrones")
        else:
            st.success("✅ Concentración del patrón madre adecuada para preparar la curva de calibración")
        
        st.session_state.conc_patron_madre = conc_patron_madre

def mostrar_curva_calibracion():
    st.markdown("## 2️⃣ Preparación de Curva de Calibración")
    
    if st.session_state.masa_sal_mohr is None:
        st.warning("⚠️ Primero debes preparar el patrón madre en la Etapa 1")
        return
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Preparar entre 3 y 7 soluciones patrón con concentraciones en el rango de 
    <b>1 a 5 mg/L</b> para construir la curva de calibración.
    </div>
    """, unsafe_allow_html=True)
    
    conc_madre = st.session_state.conc_patron_madre
    
    st.info(f"💡 Concentración del patrón madre: **{conc_madre:.2f} mg/L**")
    
    # Selector de número de patrones
    num_patrones = st.selectbox(
        "¿Cuántos patrones deseas preparar?",
        [3, 5, 7],
        help="Se recomienda mínimo 5 puntos para una buena curva"
    )
    
    st.markdown("### 🧪 Preparación de Patrones")
    
    patrones_data = []
    
    for i in range(num_patrones):
        st.markdown(f"#### Patrón {i+1}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            alicuota = st.number_input(
                f"Alícuota patrón madre (mL):",
                min_value=0.1,
                max_value=50.0,
                value=None,
                step=0.1,
                key=f"alicuota_{i}"
            )
        
        with col2:
            vol_aforo = st.selectbox(
                f"Volumen aforo (mL):",
                [None, 10, 25, 50, 100],
                format_func=lambda x: "Seleccione..." if x is None else f"{x} mL",
                key=f"aforo_{i}"
            )
        
        if alicuota and vol_aforo:
            conc_patron = calcular_concentracion_patron(conc_madre, alicuota, vol_aforo)
            
            with col3:
                st.metric("Concentración", f"{conc_patron:.3f} mg/L")
            
            with col4:
                if verificar_rango_optimo(conc_patron):
                    st.success("✅ En rango")
                else:
                    st.error("❌ Fuera de rango")
            
            patrones_data.append({
                'patron': i+1,
                'alicuota': alicuota,
                'volumen': vol_aforo,
                'concentracion': conc_patron,
                'en_rango': verificar_rango_optimo(conc_patron)
            })
    
    if len(patrones_data) == num_patrones:
        st.session_state.patrones_preparados = patrones_data
        
        # Resumen
        st.markdown("---")
        st.markdown("### 📊 Resumen de Patrones Preparados")
        
        df = pd.DataFrame(patrones_data)
        st.dataframe(df, use_container_width=True)
        
        # Verificar cuántos están en rango
        en_rango = sum([p['en_rango'] for p in patrones_data])
        
        if en_rango == num_patrones:
            st.success(f"✅ Todos los patrones ({en_rango}/{num_patrones}) están en el rango óptimo (1-5 mg/L)")
        else:
            st.warning(f"⚠️ Solo {en_rango}/{num_patrones} patrones están en el rango óptimo")

def mostrar_preparacion_muestra():
    st.markdown("## 3️⃣ Preparación de Muestra de Vino")
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Seleccionar una muestra de vino y preparar una dilución adecuada para que la 
    concentración final esté dentro del rango de la curva de calibración (1-5 mg/L).
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🍷 Selección de Muestra")
    
    # Mostrar vinos disponibles
    cols = st.columns(4)
    
    for i, (nombre, datos) in enumerate(VINOS_DATABASE.items()):
        with cols[i]:
            if st.button(
                f"{datos['imagen']}\n\n**{nombre}**\n\n{datos['descripcion']}",
                key=f"vino_{i}",
                use_container_width=True
            ):
                st.session_state.vino_seleccionado = nombre
    
    if st.session_state.vino_seleccionado:
        vino = VINOS_DATABASE[st.session_state.vino_seleccionado]
        
        st.success(f"✅ Vino seleccionado: **{st.session_state.vino_seleccionado}**")
        
        # Simulador de dilución
        st.markdown("### 🧪 Preparación de Dilución")
        
        col1, col2 = st.columns(2)
        
        with col1:
            alicuota_vino = st.number_input(
                "Alícuota de vino (mL):",
                min_value=0.1,
                max_value=50.0,
                value=None,
                step=0.1,
                help="Volumen de vino a tomar"
            )
        
        with col2:
            volumen_aforo_muestra = st.selectbox(
                "Volumen de aforo (mL):",
                [None, 10, 25, 50, 100, 250],
                format_func=lambda x: "Seleccione..." if x is None else f"{x} mL"
            )
        
        if alicuota_vino and volumen_aforo_muestra:
            st.session_state.alicuota_vino = alicuota_vino
            st.session_state.volumen_aforo_muestra = volumen_aforo_muestra
            
            # Calcular factor de dilución y concentración esperada
            fd = volumen_aforo_muestra / alicuota_vino
            conc_real_vino = vino['concentracion_fe']
            conc_diluida = conc_real_vino / fd
            
            st.markdown("---")
            st.markdown("### 📊 Análisis de la Dilución")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Factor de Dilución", f"{fd:.2f}x")
            
            with col2:
                st.metric("Concentración Esperada", f"{conc_diluida:.3f} mg/L")
            
            with col3:
                if verificar_rango_optimo(conc_diluida):
                    st.success("✅ En rango óptimo")
                else:
                    if conc_diluida < 1.0:
                        st.error("❌ Muy diluido (< 1 mg/L)")
                    else:
                        st.error("❌ Muy concentrado (> 5 mg/L)")
            
            st.session_state.conc_muestra_diluida = conc_diluida

def mostrar_medicion_aa():
    st.markdown("## 4️⃣ Medición por Absorción Atómica")
    
    if not st.session_state.patrones_preparados:
        st.warning("⚠️ Primero debes preparar la curva de calibración en la Etapa 2")
        return
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Realizar las mediciones de absorbancia de los patrones y la muestra en el 
    espectrómetro de absorción atómica.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔬 Simulador de Espectrómetro AA")
    
    # Aquí iría el simulador visual del AA (lo haremos después)
    
    tab1, tab2 = st.tabs(["📊 Medición de Patrones", "🍷 Medición de Muestra"])
    
    with tab1:
        st.markdown("#### Medición de Patrones para Curva de Calibración")
        
        patrones = st.session_state.patrones_preparados
        
        if st.button("🔥 Medir Todos los Patrones", key="medir_patrones"):
            # Verificar si los patrones están en rango
            todos_en_rango = all([p['en_rango'] for p in patrones])
            
            resultados_patrones = []
            
            for patron in patrones:
                conc = patron['concentracion']
                # Generar absorbancia basado en si están en rango
                abs_val = generar_absorbancia(conc, curva_lineal=todos_en_rango)
                
                resultados_patrones.append({
                    'Patrón': patron['patron'],
                    'Concentración (mg/L)': conc,
                    'Absorbancia': abs_val
                })
            
            st.session_state.mediciones_aa['patrones'] = resultados_patrones
            
            df_resultados = pd.DataFrame(resultados_patrones)
            st.dataframe(df_resultados, use_container_width=True)
            
            # Gráfico
            fig = px.scatter(
                df_resultados,
                x='Concentración (mg/L)',
                y='Absorbancia',
                title='Curva de Calibración',
                trendline='ols'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if todos_en_rango:
                st.success("✅ Curva de calibración lineal - Patrones en rango óptimo")
            else:
                st.warning("⚠️ Curva con desviaciones - Algunos patrones fuera de rango")
    
    with tab2:
        st.markdown("#### Medición de Muestra de Vino")
        
        if st.session_state.vino_seleccionado and hasattr(st.session_state, 'conc_muestra_diluida'):
            if st.button("🔥 Medir Muestra", key="medir_muestra"):
                conc_diluida = st.session_state.conc_muestra_diluida
                en_rango = verificar_rango_optimo(conc_diluida)
                
                # Generar absorbancia
                abs_muestra = generar_absorbancia(conc_diluida, curva_lineal=en_rango)
                
                st.session_state.mediciones_aa['muestra'] = {
                    'vino': st.session_state.vino_seleccionado,
                    'absorbancia': abs_muestra,
                    'concentracion_diluida': conc_diluida
                }
                
                st.metric("Absorbancia de la Muestra", f"{abs_muestra:.4f}")
                
                if en_rango:
                    st.success("✅ Absorbancia dentro del rango de la curva")
                else:
                    if conc_diluida < 1.0:
                        st.error("❌ Absorbancia muy baja - Muestra muy diluida")
                    else:
                        st.error("❌ Absorbancia muy alta - Muestra muy concentrada")
        else:
            st.info("Primero prepara la muestra en la Etapa 3")

def mostrar_resultados():
    st.markdown("## 5️⃣ Resultados y Cálculos")
    
    if 'patrones' not in st.session_state.mediciones_aa:
        st.warning("⚠️ Primero debes realizar las mediciones en la Etapa 4")
        return
    
    st.markdown("### 📊 Curva de Calibración Final")
    
    df_patrones = pd.DataFrame(st.session_state.mediciones_aa['patrones'])
    
    # Regresión lineal
    x = df_patrones['Concentración (mg/L)'].values
    y = df_patrones['Absorbancia'].values
    
    # Calcular pendiente e intercepto
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    
    # Coeficiente de determinación R²
    yhat = p(x)
    ybar = np.mean(y)
    ssreg = np.sum((yhat - ybar)**2)
    sstot = np.sum((y - ybar)**2)
    r2 = ssreg / sstot
    
    # Mostrar ecuación
    st.markdown(f"""
    **Ecuación de la recta:**
    
    A = {z[0]:.4f} × C + {z[1]:.4f}
    
    **Coeficiente de determinación:** R² = {r2:.4f}
    """)
    
    # Gráfico mejorado
    fig = go.Figure()
    
    # Puntos experimentales
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        name='Patrones',
        marker=dict(size=10, color='red')
    ))
    
    # Línea de regresión
    x_line = np.linspace(min(x), max(x), 100)
    y_line = p(x_line)
    
    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name='Regresión lineal',
        line=dict(color='blue', dash='dash')
    ))
    
    # Muestra (si existe)
    if 'muestra' in st.session_state.mediciones_aa:
        abs_muestra = st.session_state.mediciones_aa['muestra']['absorbancia']
        conc_muestra = st.session_state.mediciones_aa['muestra']['concentracion_diluida']
        
        fig.add_trace(go.Scatter(
            x=[conc_muestra],
            y=[abs_muestra],
            mode='markers',
            name='Muestra',
            marker=dict(size=15, color='green', symbol='star')
        ))
    
    fig.update_layout(
        title='Curva de Calibración para Fe por AA',
        xaxis_title='Concentración (mg/L)',
        yaxis_title='Absorbancia',
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Evaluación de la curva
    if r2 >= 0.995:
        st.success(f"✅ Excelente linealidad (R² = {r2:.4f})")
    elif r2 >= 0.99:
        st.info(f"✓ Buena linealidad (R² = {r2:.4f})")
    else:
        st.warning(f"⚠️ Linealidad aceptable (R² = {r2:.4f}) - Revisa los patrones")
    
    # Cálculo de concentración de la muestra
    if 'muestra' in st.session_state.mediciones_aa:
        st.markdown("---")
        st.markdown("### 🧮 Cálculo de Concentración en la Muestra")
        
        abs_muestra = st.session_state.mediciones_aa['muestra']['absorbancia']
        vino_nombre = st.session_state.mediciones_aa['muestra']['vino']
        
        # Calcular concentración a partir de la curva
        conc_calculada_diluida = (abs_muestra - z[1]) / z[0]
        
        # Factor de dilución
        fd = st.session_state.volumen_aforo_muestra / st.session_state.alicuota_vino
        
        # Concentración en el vino original
        conc_vino_original = conc_calculada_diluida * fd
        
        # Concentración real del vino
        conc_real = VINOS_DATABASE[vino_nombre]['concentracion_fe']
        
        # Error relativo
        error_relativo = abs((conc_vino_original - conc_real) / conc_real) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Absorbancia Medida", f"{abs_muestra:.4f}")
        
        with col2:
            st.metric("Conc. en Dilución", f"{conc_calculada_diluida:.3f} mg/L")
        
        with col3:
            st.metric("Factor de Dilución", f"{fd:.2f}x")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Concentración Calculada\n(Vino original)",
                f"{conc_vino_original:.2f} mg/L",
                help="Concentración de Fe calculada en el vino sin diluir"
            )
        
        with col2:
            st.metric(
                "Concentración Real",
                f"{conc_real:.2f} mg/L",
                help="Valor real de Fe en el vino"
            )
        
        with col3:
            if error_relativo < 5:
                delta_color = "normal"
                st.metric("Error Relativo", f"{error_relativo:.2f}%", delta=None, delta_color=delta_color)
                st.success("✅ Excelente precisión")
            elif error_relativo < 10:
                st.metric("Error Relativo", f"{error_relativo:.2f}%")
                st.info("✓ Buena precisión")
            else:
                st.metric("Error Relativo", f"{error_relativo:.2f}%")
                st.warning("⚠️ Error alto - Revisa el procedimiento")
        
        # Análisis detallado
        st.markdown("---")
        st.markdown("### 📝 Análisis del Resultado")
        
        with st.expander("Ver cálculos detallados", expanded=True):
            st.markdown(f"""
            **Paso 1: Cálculo de concentración en la dilución**
            
            Usando la ecuación de la recta:
            
            C = (A - b) / m
            
            C = ({abs_muestra:.4f} - {z[1]:.4f}) / {z[0]:.4f} = {conc_calculada_diluida:.3f} mg/L
            
            ---
            
            **Paso 2: Corrección por factor de dilución**
            
            C_original = C_diluida × FD
            
            C_original = {conc_calculada_diluida:.3f} × {fd:.2f} = {conc_vino_original:.2f} mg/L
            
            ---
            
            **Paso 3: Evaluación del resultado**
            
            - Vino analizado: **{vino_nombre}**
            - Concentración calculada: **{conc_vino_original:.2f} mg/L**
            - Concentración real: **{conc_real:.2f} mg/L**
            - Error relativo: **{error_relativo:.2f}%**
            """)
        
        # Recomendaciones
        if error_relativo > 10:
            st.markdown("#### 💡 Posibles causas del error elevado:")
            
            conc_diluida = st.session_state.mediciones_aa['muestra']['concentracion_diluida']
            
            if not verificar_rango_optimo(conc_diluida):
                if conc_diluida < 1.0:
                    st.warning("""
                    - ❌ La dilución fue **excesiva** (concentración < 1 mg/L)
                    - 💡 Recomendación: Usar un factor de dilución menor
                    - 📊 La absorbancia quedó por debajo del rango óptimo de la curva
                    """)
                else:
                    st.warning("""
                    - ❌ La dilución fue **insuficiente** (concentración > 5 mg/L)
                    - 💡 Recomendación: Usar un factor de dilución mayor
                    - 📊 La absorbancia quedó por encima del rango óptimo de la curva
                    """)
            
            if r2 < 0.995:
                st.warning("""
                - ❌ La curva de calibración tiene **baja linealidad**
                - 💡 Recomendación: Asegurar que todos los patrones estén en rango 1-5 mg/L
                - 📊 Algunos patrones pueden estar fuera del rango óptimo
                """)
    
    # Tabla resumen final
    st.markdown("---")
    st.markdown("### 📊 Tabla Resumen de Resultados")
    
    resumen_data = {
        "Parámetro": [
            "Masa Sal de Mohr",
            "Volumen Patrón Madre",
            "Conc. Patrón Madre",
            "Número de Patrones",
            "R² de la Curva",
            "Pendiente (m)",
            "Intercepto (b)",
        ],
        "Valor": [
            f"{st.session_state.masa_sal_mohr:.4f} g",
            f"{st.session_state.volumen_aforo_patron} mL",
            f"{st.session_state.conc_patron_madre:.2f} mg/L",
            f"{len(st.session_state.patrones_preparados)}",
            f"{r2:.4f}",
            f"{z[0]:.4f}",
            f"{z[1]:.4f}",
        ]
    }
    
    if 'muestra' in st.session_state.mediciones_aa:
        resumen_data["Parámetro"].extend([
            "Vino Analizado",
            "Alícuota Vino",
            "Factor de Dilución",
            "Absorbancia Muestra",
            "Conc. Calculada",
            "Conc. Real",
            "Error Relativo"
        ])
        resumen_data["Valor"].extend([
            vino_nombre,
            f"{st.session_state.alicuota_vino} mL",
            f"{fd:.2f}x",
            f"{abs_muestra:.4f}",
            f"{conc_vino_original:.2f} mg/L",
            f"{conc_real:.2f} mg/L",
            f"{error_relativo:.2f}%"
        ])
    
    df_resumen = pd.DataFrame(resumen_data)
    st.table(df_resumen)
    
    # Botón de descarga
    csv = df_resumen.to_csv(index=False)
    st.download_button(
        label="📥 Descargar Resultados (CSV)",
        data=csv,
        file_name="resultados_fe_vinos_aa.csv",
        mime="text/csv"
    )

# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    main()
