import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import random

# Configuración de la página
st.set_page_config(
    page_title="Simulador AAS - Determinación de Hierro en Vinos",
    page_icon="🍷",
    layout="wide"
)

# Título principal
st.title("🍷 Determinación de Hierro en Vinos por Espectrofotometría de Absorción Atómica")
st.markdown("---")

# Inicializar variables de estado en session_state
if 'calibracion_realizada' not in st.session_state:
    st.session_state.calibracion_realizada = False
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'parametros_instrumento' not in st.session_state:
    st.session_state.parametros_instrumento = {}

# Información sobre la técnica
with st.expander("📚 Información sobre la técnica AAS"):
    st.markdown("""
    La **espectrofotometría de absorción atómica (AAS)** es una técnica analítica que permite determinar 
    la concentración de elementos metálicos en una muestra midiendo la absorción de luz a longitudes 
    de onda específicas características de cada elemento.
    
    **Principio básico:** Los átomos en estado fundamental absorben luz a longitudes de onda específicas, 
    produciendo espectros de líneas estrechas. La absorbancia es proporcional a la concentración del elemento.
    
    **Para el hierro (Fe):**
    - Longitud de onda óptima: 248.3 nm
    - Límite de detección típico: 0.01-0.1 mg/L
    - Rango lineal: 0.1-10 mg/L
    """)

# Dividir en columnas
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Selección de Muestra")
    
    # Tipos de vino con concentraciones típicas de hierro (en mg/L)
    vinos = {
        "Tinto (Cabernet Sauvignon)": {"hierro_real": 4.2, "color": "#722F37"},
        "Blanco (Chardonnay)": {"hierro_real": 1.8, "color": "#F3E4AB"},
        "Rosado (Garnacha)": {"hierro_real": 2.5, "color": "#E8ADAA"},
        "Espumante (Cava)": {"hierro_real": 1.2, "color": "#F5F5DC"}
    }
    
    vino_seleccionado = st.selectbox(
        "Selecciona el tipo de vino a analizar:",
        options=list(vinos.keys())
    )
    
    # Mostrar información del vino seleccionado
    st.info(f"**Vino seleccionado:** {vino_seleccionado}")
    st.info(f"**Color característico:** {vinos[vino_seleccionado]['color']}")
    
    st.header("2. Preparación de Solución Stock")
    
    # Parámetros para preparar la solución stock
    st.subheader("Preparación de solución stock de Fe (1000 mg/L)")
    
    col1a, col1b = st.columns(2)
    
    with col1a:
        masa_sal_mohr = st.slider(
            "Masa de Sal de Mohr pesada (g):",
            min_value=0.6900, max_value=0.7100, value=0.7020, step=0.0001,
            help="Pesar aproximadamente 0.702 g de FeSO₄·(NH₄)₂SO₄·6H₂O"
        )
    
    with col1b:
        volumen_matraz = st.selectbox(
            "Volumen del matraz aforado (mL):",
            options=[100, 250, 500],
            index=0
        )
    
    # Calcular concentración teórica de la solución stock
    # Masa molar de Sal de Mohr: 392.14 g/mol, contiene 55.845 g/mol de Fe
    masa_molar_sal_mohr = 392.14
    masa_molar_fe = 55.845
    proporcion_fe = masa_molar_fe / masa_molar_sal_mohr
    
    # Concentración teórica (mg/L)
    concentracion_stock_teorica = (masa_sal_mohr * proporcion_fe * 1000) / (volumen_matraz / 1000)
    
    # Introducir error experimental
    error_pesada = random.uniform(-0.0005, 0.0005)
    masa_real = masa_sal_mohr + error_pesada
    
    concentracion_stock_real = (masa_real * proporcion_fe * 1000) / (volumen_matraz / 1000)
    
    st.success(f"**Concentración teórica de la solución stock:** {concentracion_stock_teorica:.1f} mg/L")
    
    st.header("3. Preparación de Soluciones de Calibración")
    
    # Número de puntos de calibración
    num_puntos = st.radio(
        "Número de puntos de la curva de calibración:",
        options=[3, 5, 7],
        horizontal=True
    )
    
    # Generar concentraciones objetivo
    if num_puntos == 3:
        concentraciones_objetivo = [0.5, 2.0, 4.0]
    elif num_puntos == 5:
        concentraciones_objetivo = [0.5, 1.0, 2.0, 3.0, 4.0]
    else:  # 7 puntos
        concentraciones_objetivo = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    
    st.write("**Concentraciones objetivo de las soluciones de calibración (mg/L):**")
    st.write(", ".join([f"{c} mg/L" for c in concentraciones_objetivo]))
    
    # Parámetros de dilución
    st.subheader("Parámetros de dilución")
    
    volumen_final_calibracion = st.slider(
        "Volumen final de cada solución de calibración (mL):",
        min_value=50, max_value=100, value=100, step=10
    )
    
    # Simular errores de pipeteo
    st.subheader("Precisión en el pipeteo")
    precision_pipeta = st.slider(
        "Precisión de pipeteo (%):",
        min_value=80, max_value=100, value=95,
        help="Mayor precisión = menor error en las concentraciones"
    )
    
    # Calcular volúmenes a pipetear de la solución stock
    vol_pipeteo_teorico = []
    for conc in concentraciones_objetivo:
        vol = (conc * volumen_final_calibracion) / concentracion_stock_real
        vol_pipeteo_teorico.append(vol)
    
    # Aplicar errores de pipeteo
    vol_pipeteo_real = []
    for vol in vol_pipeteo_teorico:
        error_porcentual = (100 - precision_pipeta) / 100
        error_vol = random.uniform(-error_porcentual, error_porcentual) * vol
        vol_real = vol + error_vol
        vol_pipeteo_real.append(vol_real)
    
    # Calcular concentraciones reales considerando errores
    concentraciones_reales = []
    for i, vol in enumerate(vol_pipeteo_real):
        conc_real = (vol * concentracion_stock_real) / volumen_final_calibracion
        concentraciones_reales.append(conc_real)
    
    # Mostrar tabla de preparación
    st.subheader("Tabla de preparación de soluciones de calibración")
    datos_calibracion = {
        "Solución": [f"Std {i+1}" for i in range(num_puntos)],
        "Conc. objetivo (mg/L)": concentraciones_objetivo,
        "Vol. teórico (mL)": [f"{v:.2f}" for v in vol_pipeteo_teorico],
        "Conc. real (mg/L)": [f"{c:.3f}" for c in concentraciones_reales]
    }
    df_calibracion = pd.DataFrame(datos_calibracion)
    st.dataframe(df_calibracion, use_container_width=True)

with col2:
    st.header("4. Parámetros del Instrumento AAS")
    
    # Longitud de onda
    longitud_onda = st.selectbox(
        "Longitud de onda (nm):",
        options=[248.3, 372.0, 386.0, 302.1],
        index=0,
        help="248.3 nm es la longitud de onda óptima para hierro"
    )
    
    # Tipo de llama
    tipo_llama = st.selectbox(
        "Tipo de llama:",
        options=["Aire-Acetileno", "Óxido nitroso-Acetileno"],
        index=0
    )
    
    # Altura de llama
    altura_llama = st.slider(
        "Altura de llama (mm):",
        min_value=5, max_value=15, value=8, step=1
    )
    
    # Flujo de oxidante
    flujo_oxidante = st.slider(
        "Flujo de oxidante (L/min):",
        min_value=5.0, max_value=15.0, value=10.0, step=0.5
    )
    
    # Velocidad de aspiración
    velocidad_aspiraccion = st.slider(
        "Velocidad de aspiración (mL/min):",
        min_value=3.0, max_value=8.0, value=5.0, step=0.1
    )
    
    # Evaluar parámetros seleccionados
    parametros_optimos = True
    mensajes_advertencia = []
    
    if longitud_onda != 248.3:
        parametros_optimos = False
        mensajes_advertencia.append("❌ Longitud de onda no óptima. Se recomienda 248.3 nm para máxima sensibilidad.")
    
    if tipo_llama != "Aire-Acetileno":
        parametros_optimos = False
        mensajes_advertencia.append("❌ Tipo de llama no recomendado. Aire-Acetileno es óptimo para hierro.")
    
    if altura_llama < 7 or altura_llama > 10:
        parametros_optimos = False
        mensajes_advertencia.append("⚠️ Altura de llama fuera del rango óptimo (7-10 mm).")
    
    if flujo_oxidante < 8.0 or flujo_oxidante > 12.0:
        parametros_advertencia = False
        mensajes_advertencia.append("⚠️ Flujo de oxidante fuera del rango recomendado (8-12 L/min).")
    
    if velocidad_aspiraccion < 4.0 or velocidad_aspiraccion > 6.0:
        parametros_optimos = False
        mensajes_advertencia.append("⚠️ Velocidad de aspiración fuera del rango óptimo (4-6 mL/min).")
    
    # Mostrar advertencias
    if mensajes_advertencia:
        for mensaje in mensajes_advertencia:
            st.warning(mensaje)
    else:
        st.success("✅ Todos los parámetros instrumentales están en rangos óptimos.")
    
    st.header("5. Preparación de Muestra de Vino")
    
    # Parámetros para preparar la muestra
    alicuota_vino = st.slider(
        "Alícuota de vino tomada (mL):",
        min_value=1.0, max_value=10.0, value=5.0, step=0.1
    )
    
    factor_dilucion = st.slider(
        "Factor de dilución:",
        min_value=1, max_value=10, value=5, step=1,
        help="Dilución necesaria para que la muestra esté dentro del rango de calibración"
    )
    
    # Calcular concentración esperada en la solución medida
    hierro_real_vino = vinos[vino_seleccionado]["hierro_real"]
    concentracion_esperada_muestra = hierro_real_vino / factor_dilucion
    
    st.info(f"**Concentración esperada en la solución medida:** {concentracion_esperada_muestra:.2f} mg/L")
    
    # Botón para realizar medición
    if st.button("🚀 Realizar Medición y Calibración", type="primary"):
        # Simular medición de absorbancias
        
        # Efecto de los parámetros instrumentales en la señal
        factor_senal = 1.0
        
        if longitud_onda != 248.3:
            factor_senal *= 0.3  # Reducción significativa de señal
        
        if tipo_llama != "Aire-Acetileno":
            factor_senal *= 0.7  # Reducción moderada
        
        if altura_llama < 7 or altura_llama > 10:
            factor_senal *= 0.9  # Pequeña reducción
        
        if flujo_oxidante < 8.0 or flujo_oxidante > 12.0:
            factor_senal *= 0.95  # Reducción mínima
        
        if velocidad_aspiraccion < 4.0 or velocidad_aspiraccion > 6.0:
            factor_senal *= 0.9  # Pequeña reducción
        
        # Generar curva de calibración (Ley de Beer-Lambert: A = ε * b * C)
        # Para hierro, la sensibilidad típica es ~0.1 A por mg/L
        sensibilidad_base = 0.1
        
        # Ajustar sensibilidad según parámetros
        sensibilidad = sensibilidad_base * factor_senal
        
        # Generar absorbancias teóricas
        absorbancias_teoricas = [sensibilidad * c for c in concentraciones_reales]
        
        # Añadir ruido experimental
        absorbancias_medidas = []
        for abs_teorica in absorbancias_teoricas:
            ruido = random.gauss(0, 0.005)  # Ruido aleatorio
            abs_medida = max(0, abs_teorica + ruido)
            absorbancias_medidas.append(abs_medida)
        
        # Realizar regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(concentraciones_reales, absorbancias_medidas)
        
        # Calcular absorbancia de la muestra
        absorbancia_muestra_teorica = sensibilidad * concentracion_esperada_muestra
        ruido_muestra = random.gauss(0, 0.008)
        absorbancia_muestra = max(0, absorbancia_muestra_teorica + ruido_muestra)
        
        # Calcular concentración de la muestra
        if slope != 0:
            concentracion_muestra = (absorbancia_muestra - intercept) / slope
        else:
            concentracion_muestra = 0
        
        # Calcular concentración real en el vino
        concentracion_vino = concentracion_muestra * factor_dilucion
        
        # Calcular error relativo
        error_relativo = ((concentracion_vino - hierro_real_vino) / hierro_real_vino) * 100
        
        # Guardar resultados en session_state
        st.session_state.calibracion_realizada = True
        st.session_state.resultados = {
            "concentraciones_reales": concentraciones_reales,
            "absorbancias_medidas": absorbancias_medidas,
            "pendiente": slope,
            "intercepto": intercept,
            "r_cuadrado": r_value**2,
            "absorbancia_muestra": absorbancia_muestra,
            "concentracion_muestra": concentracion_muestra,
            "concentracion_vino": concentracion_vino,
            "error_relativo": error_relativo,
            "hierro_real_vino": hierro_real_vino
        }
        
        st.session_state.parametros_instrumento = {
            "longitud_onda": longitud_onda,
            "tipo_llama": tipo_llama,
            "altura_llama": altura_llama,
            "flujo_oxidante": flujo_oxidante,
            "velocidad_aspiraccion": velocidad_aspiraccion,
            "parametros_optimos": parametros_optimos
        }

# Mostrar resultados si la calibración se ha realizado
if st.session_state.calibracion_realizada and st.session_state.resultados:
    st.markdown("---")
    st.header("📊 Resultados del Análisis")
    
    resultados = st.session_state.resultados
    parametros = st.session_state.parametros_instrumento
    
    # Mostrar curva de calibración
    col_res1, col_res2 = st.columns([2, 1])
    
    with col_res1:
        st.subheader("Curva de Calibración")
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Puntos experimentales
        ax.scatter(resultados["concentraciones_reales"], resultados["absorbancias_medidas"], 
                  color='blue', s=50, zorder=5, label='Datos experimentales')
        
        # Línea de regresión
        x_fit = np.linspace(0, max(resultados["concentraciones_reales"]) * 1.1, 100)
        y_fit = resultados["pendiente"] * x_fit + resultados["intercepto"]
        ax.plot(x_fit, y_fit, 'r-', label=f'Regresión lineal (R² = {resultados["r_cuadrado"]:.4f})')
        
        # Punto de la muestra
        ax.scatter([resultados["concentracion_muestra"]], [resultados["absorbancia_muestra"]], 
                  color='green', s=100, zorder=6, label='Muestra de vino')
        
        ax.set_xlabel('Concentración de Fe (mg/L)')
        ax.set_ylabel('Absorbancia')
        ax.set_title('Curva de Calibración - Hierro por AAS')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        st.pyplot(fig)
    
    with col_res2:
        st.subheader("Resultados Cuantitativos")
        
        # Ecuación de la recta
        st.metric("Ecuación de calibración", 
                 f"A = {resultados['pendiente']:.4f}C + {resultados['intercepto']:.4f}")
        
        st.metric("Coeficiente de determinación (R²)", f"{resultados['r_cuadrado']:.4f}")
        
        st.metric("Absorbancia de la muestra", f"{resultados['absorbancia_muestra']:.4f}")
        
        st.metric("Concentración en solución medida", f"{resultados['concentracion_muestra']:.3f} mg/L")
        
        st.metric("Concentración en vino", f"{resultados['concentracion_vino']:.2f} mg/L")
        
        # Mostrar valor real y error
        st.metric("Valor de referencia esperado", f"{resultados['hierro_real_vino']:.2f} mg/L")
        
        # Mostrar error con color según magnitud
        error = resultados["error_relativo"]
        if abs(error) < 5:
            st.success(f"Error relativo: {error:.2f}%")
        elif abs(error) < 10:
            st.warning(f"Error relativo: {error:.2f}%")
        else:
            st.error(f"Error relativo: {error:.2f}%")
    
    # Resumen de parámetros y su efecto
    st.subheader("📋 Resumen de Parámetros y su Efecto")
    
    col_param1, col_param2 = st.columns(2)
    
    with col_param1:
        st.write("**Parámetros Instrumentales:**")
        
        # Evaluar cada parámetro
        parametros_evaluacion = [
            ("Longitud de onda", parametros["longitud_onda"], "248.3 nm", 
             "Óptima" if parametros["longitud_onda"] == 248.3 else "No óptima"),
            
            ("Tipo de llama", parametros["tipo_llama"], "Aire-Acetileno", 
             "Óptima" if parametros["tipo_llama"] == "Aire-Acetileno" else "No óptima"),
            
            ("Altura de llama", f"{parametros['altura_llama']} mm", "7-10 mm", 
             "Óptima" if 7 <= parametros['altura_llama'] <= 10 else "Fuera de rango"),
            
            ("Flujo de oxidante", f"{parametros['flujo_oxidante']} L/min", "8-12 L/min", 
             "Óptimo" if 8 <= parametros['flujo_oxidante'] <= 12 else "Fuera de rango"),
            
            ("Velocidad de aspiración", f"{parametros['velocidad_aspiraccion']} mL/min", "4-6 mL/min", 
             "Óptima" if 4 <= parametros['velocidad_aspiraccion'] <= 6 else "Fuera de rango")
        ]
        
        for param, valor_actual, valor_optimo, evaluacion in parametros_evaluacion:
            if "Óptim" in evaluacion:
                st.success(f"✅ **{param}:** {valor_actual} ({evaluacion})")
            else:
                st.error(f"❌ **{param}:** {valor_actual} ({evaluacion}) - Óptimo: {valor_optimo}")
    
    with col_param2:
        st.write("**Parámetros de Preparación:**")
        
        prep_evaluacion = [
            ("Precisión de pipeteo", f"{precision_pipeta}%", 
             "Alta (>95%)" if precision_pipeta > 95 else "Media" if precision_pipeta > 90 else "Baja"),
            
            ("Número de puntos de calibración", f"{num_puntos}", 
             "Adecuado" if num_puntos >= 5 else "Mínimo"),
            
            ("Rango de calibración", f"{min(concentraciones_objetivo)}-{max(concentraciones_objetivo)} mg/L", 
             "Adecuado" if max(concentraciones_objetivo) >= 4.0 else "Limitado"),
            
            ("Factor de dilución", f"{factor_dilucion}x", 
             "Adecuado" if 1 <= factor_dilucion <= 10 else "Extremo")
        ]
        
        for param, valor, evaluacion in prep_evaluacion:
            if "Adecuado" in evaluacion or "Alta" in evaluacion:
                st.success(f"✅ **{param}:** {valor} ({evaluacion})")
            elif "Media" in evaluacion or "Mínimo" in evaluacion:
                st.warning(f"⚠️ **{param}:** {valor} ({evaluacion})")
            else:
                st.error(f"❌ **{param}:** {valor} ({evaluacion})")
    
    # Interpretación de resultados
    st.subheader("🔍 Interpretación de Resultados")
    
    if resultados["r_cuadrado"] > 0.995:
        st.success("**Curva de calibración:** Excelente linealidad (R² > 0.995)")
    elif resultados["r_cuadrado"] > 0.99:
        st.info("**Curva de calibración:** Buena linealidad (R² > 0.99)")
    elif resultados["r_cuadrado"] > 0.98:
        st.warning("**Curva de calibración:** Linealidad aceptable (R² > 0.98)")
    else:
        st.error("**Curva de calibración:** Linealidad deficiente (R² < 0.98). Verificar preparación y parámetros.")
    
    if abs(resultados["error_relativo"]) < 5:
        st.success("**Exactitud:** Resultado muy preciso (error < 5%)")
    elif abs(resultados["error_relativo"]) < 10:
        st.info("**Exactitud:** Resultado aceptable (error < 10%)")
    elif abs(resultados["error_relativo"]) < 20:
        st.warning("**Exactitud:** Resultado con error moderado (error < 20%)")
    else:
        st.error("**Exactitud:** Resultado con error significativo (error > 20%). Revisar metodología.")
    
    # Recomendaciones para mejorar
    if resultados["r_cuadrado"] < 0.99 or abs(resultados["error_relativo"]) > 10:
        st.subheader("💡 Recomendaciones para Mejorar")
        
        recomendaciones = []
        
        if parametros["longitud_onda"] != 248.3:
            recomendaciones.append("Utilizar longitud de onda de 248.3 nm para máxima sensibilidad")
        
        if parametros["tipo_llama"] != "Aire-Acetileno":
            recomendaciones.append("Cambiar a llama Aire-Acetileno para mejor sensibilidad con hierro")
        
        if not (7 <= parametros['altura_llama'] <= 10):
            recomendaciones.append("Ajustar altura de llama al rango 7-10 mm")
        
        if precision_pipeta < 95:
            recomendaciones.append("Mejorar precisión de pipeteo usando pipetas de mayor calidad y técnica adecuada")
        
        if num_puntos < 5:
            recomendaciones.append("Utilizar al menos 5 puntos de calibración para mejor estadística")
        
        if max(concentraciones_objetivo) < 4.0:
            recomendaciones.append("Ampliar rango de calibración para cubrir concentraciones más altas")
        
        if recomendaciones:
            for rec in recomendaciones:
                st.write(f"- {rec}")

# Información adicional
with st.expander("🧪 Información Adicional sobre la Metodología"):
    st.markdown("""
    ### Procedimiento Experimental Típico:
    
    1. **Preparación de solución stock de Fe (1000 mg/L):**
       - Pesar aproximadamente 0.702 g de Sal de Mohr (FeSO₄·(NH₄)₂SO₄·6H₂O)
       - Disolver y aforar a 100 mL con agua desionizada acidificada
    
    2. **Preparación de soluciones de calibración:**
       - Preparar diluciones apropiadas de la solución stock
       - Rango típico: 0.5 - 4.0 mg/L
       - Utilizar al menos 5 puntos de calibración
    
    3. **Preparación de muestra:**
       - Tomar alícuota de vino (2-10 mL)
       - Diluir apropiadamente (generalmente 5-10x)
       - Acidificar ligeramente si es necesario
    
    4. **Medición en AAS:**
       - Longitud de onda: 248.3 nm
       - Llama: Aire-Acetileno
       - Altura de llama: 8 mm
       - Corregir por blanco apropiado
    
    ### Factores Críticos para Resultados Precisos:
    - Limpieza exhaustiva de todo el material
    - Precisión en pesadas y pipeteos
    - Parámetros instrumentales óptimos
    - Preparación adecuada de blancos
    - Verificación de linealidad de la curva
    """)

# Pie de página
st.markdown("---")
st.markdown(
    "**Simulador educativo desarrollado para prácticas de laboratorio de Química Analítica** • "
    "Método basado en técnicas estándar para determinación de hierro en vinos por AAS"
)