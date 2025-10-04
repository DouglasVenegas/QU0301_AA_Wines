import streamlit as st
import pandas as pd
import numpy as np
import random
import base64
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Simulador AAS - Determinación de Hierro en Vinos",
    page_icon="🍷",
    layout="wide"
)

# Función para cargar imágenes base64 (para evitar dependencias externas)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Imágenes base64 para los vinos (puedes reemplazar estas con tus propias imágenes)
WINE_IMAGES = {
    "Tinto": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "Blanco": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADgQGBAZnD1QAAAABJRU5ErkJggg==",
    "Rosado": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+O/4PwAGIwMfLr0UJAAAAABJRU5ErkJggg==",
    "Espumante": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+O/4PwAGIwMfLr0UJAAAAABJRU5ErkJggg=="
}

# Título principal con estilo mejorado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #8B0000;
        text-align: center;
        margin-bottom: 2rem;
    }
    .instrument-panel {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ddd;
    }
    .balance-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-family: 'Courier New', monospace;
    }
    .pipette-animation {
        text-align: center;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🍷 Laboratorio Virtual - Determinación de Hierro en Vinos por AAS</div>', unsafe_allow_html=True)
st.markdown("---")

# Inicializar variables de estado
if 'calibracion_realizada' not in st.session_state:
    st.session_state.calibracion_realizada = False
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'parametros_instrumento' not in st.session_state:
    st.session_state.parametros_instrumento = {}
if 'peso_actual' not in st.session_state:
    st.session_state.peso_actual = 0.0000
if 'volumen_pipeteado' not in st.session_state:
    st.session_state.volumen_pipeteado = 0.0

# Información sobre la técnica
with st.expander("📚 Información sobre la técnica AAS", expanded=False):
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        **Espectrofotometría de Absorción Atómica (AAS)**
        
        🔬 **Principio básico:** 
        Los átomos en estado fundamental absorben luz a longitudes de onda específicas
        
        📊 **Ley de Beer-Lambert:**
        A = ε × b × C
        
        ⚗️ **Para hierro (Fe):**
        - Longitud de onda óptima: 248.3 nm
        - Límite de detección: 0.01-0.1 mg/L
        - Rango lineal: 0.1-10 mg/L
        """)
    with col_info2:
        st.image("https://via.placeholder.com/400x200/4B8BBE/FFFFFF?text=Esquema+AAS", 
                caption="Esquema de un espectrómetro de absorción atómica")

# SECCIÓN 1: SELECCIÓN DE MUESTRA CON IMÁGENES
st.header("1. 🍷 Selección de Muestra de Vino")

# Tipos de vino con imágenes y descripciones
vinos = {
    "Tinto (Cabernet Sauvignon)": {
        "hierro_real": 4.2, 
        "color": "#722F37",
        "imagen": "🍷",
        "descripcion": "Vino tinto robusto con notas de cassis y pimienta"
    },
    "Blanco (Chardonnay)": {
        "hierro_real": 1.8, 
        "color": "#F3E4AB",
        "imagen": "🥂",
        "descripcion": "Vino blanco seco con aromas cítricos y tropicales"
    },
    "Rosado (Garnacha)": {
        "hierro_real": 2.5, 
        "color": "#E8ADAA",
        "imagen": "🍑",
        "descripcion": "Vino rosado fresco con notas de frutos rojos"
    },
    "Espumante (Cava)": {
        "hierro_real": 1.2, 
        "color": "#F5F5DC",
        "imagen": "🫧",
        "descripcion": "Vino espumante seco con burbujas finas"
    }
}

# Mostrar vinos como tarjetas seleccionables
cols = st.columns(4)
for i, (vino_nombre, info) in enumerate(vinos.items()):
    with cols[i]:
        st.markdown(f"""
        <div style='border: 2px solid {info["color"]}; border-radius: 10px; padding: 15px; text-align: center; 
                    background-color: {"#e6f3ff" if st.session_state.get('vino_seleccionado') == vino_nombre else "white"};'>
            <div style='font-size: 3rem;'>{info['imagen']}</div>
            <h4>{vino_nombre.split(' ')[0]}</h4>
            <p style='font-size: 0.8em; color: #666;'>{info['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Seleccionar {vino_nombre.split(' ')[0]}", key=f"btn_{i}"):
            st.session_state.vino_seleccionado = vino_nombre
            st.rerun()

if 'vino_seleccionado' in st.session_state:
    vino_info = vinos[st.session_state.vino_seleccionado]
    st.success(f"""
    ✅ **Muestra seleccionada:** {st.session_state.vino_seleccionado}
    🎯 **Descripción:** {vino_info['descripcion']}
    📊 **Hierro de referencia:** {vino_info['hierro_real']} mg/L
    """)

# SECCIÓN 2: SIMULADOR DE BALANZA
st.header("2. ⚖️ Simulador de Balanza Analítica")

col_balance1, col_balance2 = st.columns([2, 1])

with col_balance1:
    st.subheader("🔧 Pesada de Sal de Mohr")
    
    # Simulador de balanza interactivo
    st.markdown("""
    **Instrucciones:**
    1. Coloque el vidrio de reloj en la balanza
    2. Tara la balanza (botón 'Tara')
    3. Agregue Sal de Mohr gradualmente
    4. Intente alcanzar 0.7020 g ± 0.0010 g
    """)
    
    # Controles de la balanza
    col_controls1, col_controls2, col_controls3 = st.columns(3)
    
    with col_controls1:
        if st.button("⚖️ Tara (Cero)", use_container_width=True):
            st.session_state.peso_actual = 0.0000
    
    with col_controls2:
        agregar_peso = st.slider("Agregar Sal de Mohr (mg)", 0, 50, 10, key="agregar_sal")
    
    with col_controls3:
        if st.button("➕ Agregar", use_container_width=True):
            st.session_state.peso_actual += agregar_peso / 1000.0

with col_balance2:
    st.markdown('<div class="balance-display">', unsafe_allow_html=True)
    st.markdown("### BALANZA ANALÍTICA")
    st.markdown(f"# {st.session_state.peso_actual:.4f} g")
    
    # Indicador de precisión
    diferencia = abs(st.session_state.peso_actual - 0.7020)
    if diferencia <= 0.0010:
        st.success("✅ Peso óptimo")
    elif diferencia <= 0.0020:
        st.warning("⚠️ Peso aceptable")
    else:
        st.error("❌ Fuera de rango")
    
    st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN 3: PREPARACIÓN DE SOLUCIONES
st.header("3. 🧪 Preparación de Soluciones")

col_sol1, col_sol2 = st.columns(2)

with col_sol1:
    st.subheader("Solución Stock")
    
    volumen_matraz = st.selectbox(
        "📏 Volumen del matraz aforado:",
        options=[100, 250, 500],
        index=0,
        format_func=lambda x: f"{x} mL"
    )
    
    # Cálculo automático basado en pesada
    masa_molar_sal_mohr = 392.14
    masa_molar_fe = 55.845
    proporcion_fe = masa_molar_fe / masa_molar_sal_mohr
    
    if st.session_state.peso_actual > 0:
        concentracion_stock_real = (st.session_state.peso_actual * proporcion_fe * 1000) / (volumen_matraz / 1000)
        st.info(f"**Concentración stock calculada:** {concentracion_stock_real:.1f} mg/L")
    else:
        concentracion_stock_real = 1000.0
        st.warning("Realice la pesada para calcular concentración")

with col_sol2:
    st.subheader("🧴 Soluciones de Calibración")
    
    num_puntos = st.radio(
        "Número de puntos de calibración:",
        options=[3, 5, 7],
        horizontal=True,
        format_func=lambda x: f"{x} puntos"
    )
    
    # Generar concentraciones objetivo
    if num_puntos == 3:
        concentraciones_objetivo = [0.5, 2.0, 4.0]
    elif num_puntos == 5:
        concentraciones_objetivo = [0.5, 1.0, 2.0, 3.0, 4.0]
    else:
        concentraciones_objetivo = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

# SECCIÓN 4: SIMULADOR DE PIPETEO
st.header("4. 🧫 Simulador de Pipeteo")

st.markdown("""
**Instrucciones de pipeteo:**
1. Seleccione el volumen a pipetear
2. Presione 'Aspirar' para llenar la pipeta
3. Presione 'Transferir' para vaciar en el matraz
4. Repita para cada solución de calibración
""")

col_pip1, col_pip2, col_pip3 = st.columns([1, 1, 2])

with col_pip1:
    volumen_seleccionado = st.slider(
        "Volumen de pipeta (mL):",
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )
    
    if st.button("💧 Aspirar muestra", use_container_width=True):
        st.session_state.volumen_pipeteado = volumen_seleccionado
        st.success(f"Aspirados {volumen_seleccionado} mL")

with col_pip2:
    precision_pipeta = st.slider(
        "Precisión de pipeteo (%):",
        min_value=80,
        max_value=100,
        value=95,
        help="Afecta la reproducibilidad de las mediciones"
    )

with col_pip3:
    st.markdown('<div class="pipette-animation">', unsafe_allow_html=True)
    if st.session_state.volumen_pipeteado > 0:
        st.markdown(f"### 🧪 PIPETA AUTOMÁTICA")
        st.markdown(f"### 🔴 {st.session_state.volumen_pipeteado} mL")
        st.progress(st.session_state.volumen_pipeteado / 10.0)
        if st.button("➡️ Transferir a matraz", use_container_width=True):
            st.success(f"✅ Transferidos {st.session_state.volumen_pipeteado} mL")
            st.session_state.volumen_pipeteado = 0
    else:
        st.markdown("### 🧪 PIPETA AUTOMÁTICA")
        st.markdown("### ⚪ 0.0 mL")
        st.info("Seleccione volumen y aspire")
    st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN 5: PARÁMETROS DEL INSTRUMENTO AAS
st.header("5. 🔬 Parámetros del Espectrómetro AAS")

st.markdown('<div class="instrument-panel">', unsafe_allow_html=True)

col_aas1, col_aas2, col_aas3 = st.columns(3)

with col_aas1:
    st.subheader("⚡ Fuente de Radiación")
    
    longitud_onda = st.select_slider(
        "Longitud de onda (nm):",
        options=[248.3, 302.1, 372.0, 386.0],
        value=248.3,
        format_func=lambda x: f"{x} nm"
    )
    
    # Indicador visual de longitud de onda óptima
    if longitud_onda == 248.3:
        st.success("✅ Longitud de onda óptima para Fe")
    else:
        st.error("❌ Longitud de onda no óptima")

with col_aas2:
    st.subheader("🔥 Sistema de Atomización")
    
    tipo_llama = st.radio(
        "Tipo de llama:",
        ["Aire-Acetileno", "Óxido nitroso-Acetileno"],
        index=0
    )
    
    altura_llama = st.slider(
        "Altura de llama (mm):",
        min_value=5, max_value=15, value=8, step=1
    )

with col_aas3:
    st.subheader("📊 Parámetros de Medición")
    
    flujo_oxidante = st.slider(
        "Flujo de oxidante (L/min):",
        min_value=5.0, max_value=15.0, value=10.0, step=0.5
    )
    
    velocidad_aspiraccion = st.slider(
        "Velocidad de aspiración (mL/min):",
        min_value=3.0, max_value=8.0, value=5.0, step=0.1
    )

st.markdown('</div>', unsafe_allow_html=True)

# Evaluación de parámetros en tiempo real
parametros_optimos = True
mensajes = []

if longitud_onda != 248.3:
    parametros_optimos = False
    mensajes.append("❌ Longitud de onda no óptima")
if tipo_llama != "Aire-Acetileno":
    parametros_optimos = False
    mensajes.append("❌ Tipo de llama no recomendado")
if altura_llama < 7 or altura_llama > 10:
    parametros_optimos = False
    mensajes.append("⚠️ Altura de llama fuera de rango óptimo")
if flujo_oxidante < 8.0 or flujo_oxidante > 12.0:
    parametros_optimos = False
    mensajes.append("⚠️ Flujo de oxidante fuera de rango")
if velocidad_aspiraccion < 4.0 or velocidad_aspiraccion > 6.0:
    parametros_optimos = False
    mensajes.append("⚠️ Velocidad de aspiración fuera de rango")

if mensajes:
    st.warning("**Ajustes recomendados:** " + " | ".join(mensajes))
else:
    st.success("✅ Todos los parámetros están en rangos óptimos")

# SECCIÓN 6: PREPARACIÓN DE MUESTRA
st.header("6. 🧴 Preparación de Muestra de Vino")

if 'vino_seleccionado' in st.session_state:
    col_muestra1, col_muestra2 = st.columns(2)
    
    with col_muestra1:
        alicuota_vino = st.slider(
            "Alícuota de vino (mL):",
            min_value=1.0, max_value=10.0, value=5.0, step=0.1
        )
        
        factor_dilucion = st.slider(
            "Factor de dilución:",
            min_value=1, max_value=10, value=5, step=1
        )
    
    with col_muestra2:
        hierro_real_vino = vinos[st.session_state.vino_seleccionado]["hierro_real"]
        concentracion_esperada = hierro_real_vino / factor_dilucion
        
        st.info(f"""
        **Cálculos de dilución:**
        - Concentración original: {hierro_real_vino} mg/L
        - Factor de dilución: {factor_dilucion}x
        - Concentración esperada: {concentracion_esperada:.2f} mg/L
        """)

# BOTÓN DE EJECUCIÓN PRINCIPAL
st.markdown("---")
col_exec1, col_exec2, col_exec3 = st.columns([1, 2, 1])

with col_exec2:
    if st.button("🚀 EJECUTAR ANÁLISIS COMPLETO", use_container_width=True, type="primary"):
        with st.spinner("Realizando análisis..."):
            # Simular todo el proceso de análisis
            import time
            
            # Barra de progreso para simular el proceso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "Preparando soluciones de calibración...",
                "Optimizando parámetros del AAS...",
                "Atomizando muestras...",
                "Midiendo absorbancias...",
                "Calculando curva de calibración...",
                "Analizando muestra de vino..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(f"⏳ {step}")
                progress_bar.progress((i + 1) / len(steps))
                time.sleep(1)
            
            # Cálculos de la curva de calibración
            vol_pipeteo_teorico = [(conc * 100) / concentracion_stock_real for conc in concentraciones_objetivo]
            
            # Aplicar errores de pipeteo
            concentraciones_reales = []
            for vol in vol_pipeteo_teorico:
                error_porcentual = (100 - precision_pipeta) / 100
                error_vol = random.uniform(-error_porcentual, error_porcentual) * vol
                vol_real = vol + error_vol
                conc_real = (vol_real * concentracion_stock_real) / 100
                concentraciones_reales.append(conc_real)
            
            # Generar absorbancias con efectos de parámetros
            factor_senal = 1.0
            if longitud_onda != 248.3: factor_senal *= 0.3
            if tipo_llama != "Aire-Acetileno": factor_senal *= 0.7
            if altura_llama < 7 or altura_llama > 10: factor_senal *= 0.9
            
            sensibilidad = 0.1 * factor_senal
            absorbancias_medidas = [sensibilidad * c + random.gauss(0, 0.005) for c in concentraciones_reales]
            
            # Regresión lineal manual
            x, y = np.array(concentraciones_reales), np.array(absorbancias_medidas)
            slope = np.cov(x, y, bias=True)[0,1] / np.var(x) if np.var(x) > 0 else sensibilidad
            intercept = np.mean(y) - slope * np.mean(x)
            y_pred = slope * x + intercept
            r_cuadrado = 1 - (np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)) if np.var(y) > 0 else 0.999
            
            # Calcular resultado de la muestra
            absorbancia_muestra = sensibilidad * concentracion_esperada + random.gauss(0, 0.008)
            concentracion_muestra = (absorbancia_muestra - intercept) / slope if slope != 0 else 0
            concentracion_vino = concentracion_muestra * factor_dilucion
            error_relativo = ((concentracion_vino - hierro_real_vino) / hierro_real_vino) * 100
            
            # Guardar resultados
            st.session_state.calibracion_realizada = True
            st.session_state.resultados = {
                "concentraciones_reales": concentraciones_reales,
                "absorbancias_medidas": absorbancias_medidas,
                "pendiente": slope, "intercepto": intercept, "r_cuadrado": r_cuadrado,
                "absorbancia_muestra": absorbancia_muestra, "concentracion_muestra": concentracion_muestra,
                "concentracion_vino": concentracion_vino, "error_relativo": error_relativo,
                "hierro_real_vino": hierro_real_vino
            }
            
            st.session_state.parametros_instrumento = {
                "longitud_onda": longitud_onda, "tipo_llama": tipo_llama,
                "altura_llama": altura_llama, "flujo_oxidante": flujo_oxidante,
                "velocidad_aspiraccion": velocidad_aspiraccion, "parametros_optimos": parametros_optimos
            }
            
            status_text.success("✅ Análisis completado exitosamente!")
            st.rerun()

# MOSTRAR RESULTADOS
if st.session_state.calibracion_realizada and st.session_state.resultados:
    st.markdown("---")
    st.header("📊 RESULTADOS DEL ANÁLISIS")
    
    resultados = st.session_state.resultados
    
    # Tarjeta de resultados principales
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.metric(
            "Concentración de Hierro", 
            f"{resultados['concentracion_vino']:.2f} mg/L",
            f"{resultados['error_relativo']:+.1f}%"
        )
    
    with col_res2:
        st.metric("Calidad de Calibración", f"R² = {resultados['r_cuadrado']:.4f}")
    
    with col_res3:
        if abs(resultados['error_relativo']) < 5:
            st.success("✅ Excelente precisión")
        elif abs(resultados['error_relativo']) < 10:
            st.info("🟡 Precisión aceptable")
        else:
            st.error("🔴 Precisión deficiente")
    
    # Tabla de datos de calibración
    st.subheader("📈 Datos de Calibración")
    datos_calibracion = {
        "Solución": [f"Std {i+1}" for i in range(len(resultados["concentraciones_reales"]))],
        "[Fe] (mg/L)": [f"{c:.3f}" for c in resultados["concentraciones_reales"]],
        "Absorbancia": [f"{a:.4f}" for a in resultados["absorbancias_medidas"]]
    }
    st.dataframe(pd.DataFrame(datos_calibracion), use_container_width=True)
    
    # Resumen ejecutivo
    with st.expander("📋 Resumen Ejecutivo del Análisis", expanded=True):
        st.write(f"**Muestra analizada:** {st.session_state.vino_seleccionado}")
        st.write(f"**Ecuación de calibración:** A = {resultados['pendiente']:.4f} × C + {resultados['intercepto']:.4f}")
        st.write(f"**Linealidad:** {'Excelente' if resultados['r_cuadrado'] > 0.995 else 'Buena' if resultados['r_cuadrado'] > 0.99 else 'Aceptable' if resultados['r_cuadrado'] > 0.98 else 'Deficiente'}")
        st.write(f"**Exactitud:** {'Muy alta' if abs(resultados['error_relativo']) < 5 else 'Alta' if abs(resultados['error_relativo']) < 10 else 'Moderada' if abs(resultados['error_relativo']) < 20 else 'Baja'}")

# PIE DE PÁGINA
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p><strong>🧪 Laboratorio Virtual de Química Analítica</strong></p>
        <p>Simulador educativo para la determinación de hierro en vinos por espectrofotometría de absorción atómica</p>
    </div>
    """, 
    unsafe_allow_html=True
)
