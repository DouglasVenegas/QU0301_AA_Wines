import os
import time
import random
import base64
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# --- Configuración de la página ---
st.set_page_config(
    page_title="Simulador AAS - Determinación de Hierro en Vinos",
    page_icon="🍷",
    layout="wide"
)

# --- Utilidades para imágenes ---
def show_image(path, caption=None, use_container_width=True):
    """
    Intenta abrir y mostrar una imagen desde `path`.
    Si no existe o falla, genera un placeholder y lo muestra.
    """
    try:
        if path is None:
            raise FileNotFoundError("ruta vacía")
        if os.path.exists(path):
            img = Image.open(path)
        else:
            raise FileNotFoundError(path)
    except Exception:
        # Crear placeholder simple
        img = Image.new("RGB", (800, 500), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        text = "Imagen no disponible"
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((800 - w) / 2, (500 - h) / 2), text, fill=(100, 100, 100), font=font)
    if caption:
        st.image(img, caption=caption, use_container_width=use_container_width)
    else:
        st.image(img, use_container_width=use_container_width)

# --- Datos de vinos (un solo lugar) ---
vinos = {
    "Tinto (Cabernet Sauvignon)": {
        "imagen": "datos/Download.jpg",
        "descripcion": "Vino tinto con cuerpo, envejecido en barrica.",
        "hierro_real": 3.25,
        "color": "#8B0000"
    },
    "Blanco (Chardonnay)": {
        "imagen": "datos/White_Wine.jpg",
        "descripcion": "Vino blanco seco, frutado, de fermentación controlada.",
        "hierro_real": 1.85,
        "color": "#F5DEB3"
    },
    "Rosado (Garnacha)": {
        "imagen": "datos/Rose_Wine.webp",
        "descripcion": "Vino rosado fresco, con notas florales.",
        "hierro_real": 2.10,
        "color": "#FF69B4"
    },
    "Espumante (Cava)": {
        "imagen": "datos/sparkling_Wine.webp",
        "descripcion": "Vino espumoso tradicional, segunda fermentación en botella.",
        "hierro_real": 2.65,
        "color": "#DAA520"
    }
}

# --- Estilos ---
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

st.markdown(
    """
    <h1 style='font-size:3.5rem; font-weight:bold; color:#000000; text-align:center; margin-bottom:2rem;'>
        🍷 Laboratorio Virtual - Determinación de Hierro en Vinos por AAS
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# --- Estado ---
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

# --- Información técnica ---
with st.expander("📚 Información sobre la técnica AAS", expanded=False):
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        **Espectrofotometría de Absorción Atómica (AAS)**

        🔬 **Principio básico:** 
        La absorción atómica se basa en que los átomos en estado fundamental pueden absorber luz únicamente a longitudes de onda específicas. 

        🔬 **Instrumentación:** 
        Muestra en aerosol en la llama, fuente de radiación específica y detector que mide la atenuación de la luz.

        📊 **Para hierro (Fe):**
        - Longitud de onda óptima: 248.3 nm
        - Límite de detección: 0.01-0.1 mg/L
        - Rango lineal: 0.1-10 mg/L
        """)
    with col_info2:
        show_image("datos/Energy_Fiagram.jpg", caption="Diagrama de energía en espectroscopía atómica")
        show_image("datos/Instrument.webp", caption="Esquema de equipo de Absorción Atómica")

# --- SECCIÓN 1: Selección de muestra ---
st.markdown(
    """
    <h2 style='color:#458B74; font-weight:bold; font-size:2rem;'>
        Parte I. Selección de Muestra de Vino 🍷
    </h2>
    """,
    unsafe_allow_html=True
)
cols = st.columns(4)
for i, (vino_nombre, info) in enumerate(vinos.items()):
    with cols[i]:
        show_image(info.get('imagen'), use_container_width=True)
        st.markdown(f"""
        <div style='border: 2px solid {info["color"]}; border-radius: 10px; padding: 10px; text-align: center;'>
            <h4 style="margin:6px 0;">{vino_nombre.split(' ')[0]}</h4>
            <p style='font-size: 0.8em; color: #666; margin:4px 0;'>{info['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Seleccionar {vino_nombre.split(' ')[0]}", key=f"btn_{i}"):
            st.session_state.vino_seleccionado = vino_nombre
            st.rerun()

if 'vino_seleccionado' in st.session_state:
    vino_info = vinos[st.session_state.vino_seleccionado]
    st.success(f"✅ **Muestra seleccionada:** {st.session_state.vino_seleccionado} — Hierro referencia: {vino_info['hierro_real']} mg/L")

# --- SECCIÓN 2: Simulador de balanza ---
st.header("2. ⚖️ Simulador de Balanza Analítica")
col_balance1, col_balance2 = st.columns([2, 1])

with col_balance1:
    st.subheader("🔧 Pesada de Sal de Mohr")
    st.markdown("""
    **Instrucciones:**
    1. Coloque el vidrio de reloj en la balanza
    2. Tara la balanza (botón 'Tara')
    3. Agregue Sal de Mohr gradualmente
    4. Intente alcanzar 0.7020 g ± 0.0010 g
    """)
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
    diferencia = abs(st.session_state.peso_actual - 0.7020)
    if diferencia <= 0.0010:
        st.success("✅ Peso óptimo")
    elif diferencia <= 0.0020:
        st.warning("⚠️ Peso aceptable")
    else:
        st.error("❌ Fuera de rango")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECCIÓN 3: Preparación de soluciones ---
st.header("3. 🧪 Preparación de Soluciones")
col_sol1, col_sol2 = st.columns(2)

with col_sol1:
    st.subheader("Solución Stock")
    volumen_matraz = st.selectbox("📏 Volumen del matraz aforado:", options=[100, 250, 500], index=0, format_func=lambda x: f"{x} mL")
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
    num_puntos = st.radio("Número de puntos de calibración:", options=[3, 5, 7], horizontal=True, format_func=lambda x: f"{x} puntos")
    if num_puntos == 3:
        concentraciones_objetivo = [0.5, 2.0, 4.0]
    elif num_puntos == 5:
        concentraciones_objetivo = [0.5, 1.0, 2.0, 3.0, 4.0]
    else:
        concentraciones_objetivo = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

# --- SECCIÓN 4: Pipeteo ---
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
    volumen_seleccionado = st.slider("Volumen de pipeta (mL):", min_value=1.0, max_value=10.0, value=5.0, step=0.1)
    if st.button("💧 Aspirar muestra", use_container_width=True):
        st.session_state.volumen_pipeteado = volumen_seleccionado
        st.success(f"Aspirados {volumen_seleccionado} mL")

with col_pip2:
    precision_pipeta = st.slider("Precisión de pipeteo (%):", min_value=80, max_value=100, value=95, help="Afecta la reproducibilidad de las mediciones")

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

# --- SECCIÓN 5: Parámetros AAS ---
st.header("5. 🔬 Parámetros del Espectrómetro AAS")
st.markdown('<div class="instrument-panel">', unsafe_allow_html=True)
col_aas1, col_aas2, col_aas3 = st.columns(3)

with col_aas1:
    st.subheader("⚡ Fuente de Radiación")
    longitud_onda = st.select_slider("Longitud de onda (nm):", options=[248.3, 302.1, 372.0, 386.0], value=248.3, format_func=lambda x: f"{x} nm")
    if longitud_onda == 248.3:
        st.success("✅ Longitud de onda óptima para Fe")
    else:
        st.error("❌ Longitud de onda no óptima")

with col_aas2:
    st.subheader("🔥 Sistema de Atomización")
    tipo_llama = st.radio("Tipo de llama:", ["Aire-Acetileno", "Óxido nitroso-Acetileno"], index=0)
    altura_llama = st.slider("Altura de llama (mm):", min_value=5, max_value=15, value=8, step=1)

with col_aas3:
    st.subheader("📊 Parámetros de Medición")
    flujo_oxidante = st.slider("Flujo de oxidante (L/min):", min_value=5.0, max_value=15.0, value=10.0, step=0.5)
    velocidad_aspiracion = st.slider("Velocidad de aspiración (mL/min):", min_value=3.0, max_value=8.0, value=5.0, step=0.1)

st.markdown('</div>', unsafe_allow_html=True)

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
if velocidad_aspiracion < 4.0 or velocidad_aspiracion > 6.0:
    parametros_optimos = False
    mensajes.append("⚠️ Velocidad de aspiración fuera de rango")

if mensajes:
    st.warning("**Ajustes recomendados:** " + " | ".join(mensajes))
else:
    st.success("✅ Todos los parámetros están en rangos óptimos")

# --- SECCIÓN 6: Preparación de muestra ---
st.header("6. 🧴 Preparación de Muestra de Vino")
if 'vino_seleccionado' in st.session_state:
    col_muestra1, col_muestra2 = st.columns(2)
    with col_muestra1:
        alicuota_vino = st.slider("Alícuota de vino (mL):", min_value=1.0, max_value=10.0, value=5.0, step=0.1)
        factor_dilucion = st.slider("Factor de dilución:", min_value=1, max_value=10, value=5, step=1)
    with col_muestra2:
        hierro_real_vino = vinos[st.session_state.vino_seleccionado]["hierro_real"]
        concentracion_esperada = hierro_real_vino / factor_dilucion
        st.info(f"**Cálculos de dilución:**\n- Concentración original: {hierro_real_vino} mg/L\n- Factor de dilución: {factor_dilucion}x\n- Concentración esperada: {concentracion_esperada:.2f} mg/L")

# --- BOTÓN EJECUTAR ---
st.markdown("---")
col_exec1, col_exec2, col_exec3 = st.columns([1, 2, 1])
with col_exec2:
    if st.button("🚀 EJECUTAR ANÁLISIS COMPLETO", use_container_width=True, type="primary"):
        with st.spinner("Realizando análisis..."):
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
                time.sleep(0.8)

            # Cálculos
            vol_pipeteo_teorico = [(conc * 100) / concentracion_stock_real for conc in concentraciones_objetivo]
            concentraciones_reales = []
            for vol in vol_pipeteo_teorico:
                error_porcentual = (100 - precision_pipeta) / 100
                error_vol = random.uniform(-error_porcentual, error_porcentual) * vol
                vol_real = vol + error_vol
                conc_real = (vol_real * concentracion_stock_real) / 100
                concentraciones_reales.append(conc_real)

            factor_senal = 1.0
            if longitud_onda != 248.3: factor_senal *= 0.3
            if tipo_llama != "Aire-Acetileno": factor_senal *= 0.7
            if altura_llama < 7 or altura_llama > 10: factor_senal *= 0.9

            sensibilidad = 0.1 * factor_senal
            absorbancias_medidas = [sensibilidad * c + random.gauss(0, 0.005) for c in concentraciones_reales]

            x, y = np.array(concentraciones_reales), np.array(absorbancias_medidas)
            slope = (np.cov(x, y, bias=True)[0, 1] / np.var(x)) if np.var(x) > 0 else sensibilidad
            intercept = np.mean(y) - slope * np.mean(x)
            y_pred = slope * x + intercept
            r_cuadrado = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)) if np.var(y) > 0 else 0.999

            # Resultado muestra
            if 'concentracion_esperada' in locals():
                absorbancia_muestra = sensibilidad * concentracion_esperada + random.gauss(0, 0.008)
                concentracion_muestra = (absorbancia_muestra - intercept) / slope if slope != 0 else 0
                concentracion_vino = concentracion_muestra * factor_dilucion
            else:
                absorbancia_muestra = 0
                concentracion_muestra = 0
                concentracion_vino = 0
            error_relativo = ((concentracion_vino - vinos.get(st.session_state.get('vino_seleccionado', ''), {}).get('hierro_real', 1)) / max(vinos.get(st.session_state.get('vino_seleccionado', ''), {}).get('hierro_real', 1), 1e-9)) * 100

            # Guardar resultados
            st.session_state.calibracion_realizada = True
            st.session_state.resultados = {
                "concentraciones_reales": concentraciones_reales,
                "absorbancias_medidas": absorbancias_medidas,
                "pendiente": slope, "intercepto": intercept, "r_cuadrado": r_cuadrado,
                "absorbancia_muestra": absorbancia_muestra, "concentracion_muestra": concentracion_muestra,
                "concentracion_vino": concentracion_vino, "error_relativo": error_relativo,
                "hierro_real_vino": vinos.get(st.session_state.get('vino_seleccionado', ''), {}).get('hierro_real', None)
            }
            st.session_state.parametros_instrumento = {
                "longitud_onda": longitud_onda, "tipo_llama": tipo_llama,
                "altura_llama": altura_llama, "flujo_oxidante": flujo_oxidante,
                "velocidad_aspiracion": velocidad_aspiracion, "parametros_optimos": parametros_optimos
            }
            status_text.success("✅ Análisis completado exitosamente!")
            st.rerun()

# --- Mostrar resultados ---
if st.session_state.calibracion_realizada and st.session_state.resultados:
    st.markdown("---")
    st.header("📊 RESULTADOS DEL ANÁLISIS")
    resultados = st.session_state.resultados

    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Concentración de Hierro", f"{resultados['concentracion_vino']:.2f} mg/L", f"{resultados['error_relativo']:+.1f}%")
    with col_res2:
        st.metric("Calidad de Calibración", f"R² = {resultados['r_cuadrado']:.4f}")
    with col_res3:
        if abs(resultados['error_relativo']) < 5:
            st.success("✅ Excelente precisión")
        elif abs(resultados['error_relativo']) < 10:
            st.info("🟡 Precisión aceptable")
        else:
            st.error("🔴 Precisión deficiente")

    st.subheader("📈 Datos de Calibración")
    datos_calibracion = {
        "Solución": [f"Std {i+1}" for i in range(len(resultados["concentraciones_reales"]))],
        "[Fe] (mg/L)": [f"{c:.3f}" for c in resultados["concentraciones_reales"]],
        "Absorbancia": [f"{a:.4f}" for a in resultados["absorbancias_medidas"]]
    }
    st.dataframe(pd.DataFrame(datos_calibracion), use_container_width=True)

    with st.expander("📋 Resumen Ejecutivo del Análisis", expanded=True):
        st.write(f"**Muestra analizada:** {st.session_state.get('vino_seleccionado', 'N/A')}")
        st.write(f"**Ecuación de calibración:** A = {resultados['pendiente']:.4f} × C + {resultados['intercepto']:.4f}")
        st.write(f"**Linealidad:** {'Excelente' if resultados['r_cuadrado'] > 0.995 else 'Buena' if resultados['r_cuadrado'] > 0.99 else 'Aceptable' if resultados['r_cuadrado'] > 0.98 else 'Deficiente'}")
        st.write(f"**Exactitud:** {'Muy alta' if abs(resultados['error_relativo']) < 5 else 'Alta' if abs(resultados['error_relativo']) < 10 else 'Moderada' if abs(resultados['error_relativo']) < 20 else 'Baja'}")

# --- Pie de página ---
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
