# ============================================================
# LABORATORIO VIRTUAL - ANÁLISIS DE VINO POR ABSORCIÓN ATÓMICA
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    st.set_page_config(page_title="Laboratorio Virtual - AA de Vinos", layout="wide")
    st.title("🍷 Laboratorio Virtual: Determinación de Hierro en Vino por Absorción Atómica")

    st.markdown("""
    ### Objetivo
    Determinar la concentración de hierro en una muestra de vino mediante **Absorción Atómica (AA)**,
    usando una curva de calibración con estándares conocidos.
    """)

    # ============================================================
    # ETAPA 1: DATOS DE CALIBRACIÓN
    # ============================================================

    st.header("Etapa 1: Datos de calibración")
    st.markdown("Introduce las concentraciones y absorbancias de los patrones.")

    n_std = st.number_input("Número de estándares", min_value=2, max_value=10, value=5)
    col1, col2 = st.columns(2)
    with col1:
        conc_std = []
        for i in range(n_std):
            conc_std.append(st.number_input(f"Concentración estándar {i+1} (mg/L)", min_value=0.0, value=float(i+1)))
    with col2:
        abs_std = []
        for i in range(n_std):
            abs_std.append(st.number_input(f"Absorbancia estándar {i+1}", min_value=0.0, value=0.100*i+0.050))

    df_std = pd.DataFrame({
        "Concentración (mg/L)": conc_std,
        "Absorbancia": abs_std
    })
    st.dataframe(df_std)

    # ============================================================
    # ETAPA 2: REGRESIÓN LINEAL
    # ============================================================

    st.header("Etapa 2: Curva de calibración")
    model = LinearRegression()
    X = np.array(conc_std).reshape(-1, 1)
    y = np.array(abs_std)
    model.fit(X, y)
    slope = model.coef_[0]
    intercept = model.intercept_
    r2 = model.score(X, y)

    st.markdown(f"""
    **Ecuación de calibración:**
    \[
    A = {slope:.4f}C + {intercept:.4f}
    \]

    **Coeficiente de determinación:** \( R^2 = {r2:.4f} \)
    """)

    st.line_chart(df_std.rename(columns={"Concentración (mg/L)": "x", "Absorbancia": "y"}).set_index("x"))

    # ============================================================
    # ETAPA 3: MEDICIÓN DE MUESTRA
    # ============================================================

    st.header("Etapa 3: Medición de la muestra")
    abs_muestra = st.number_input("Absorbancia de la muestra", min_value=0.0, value=0.350)
    fd = st.number_input("Factor de dilución aplicado a la muestra", min_value=1.0, value=10.0)

    conc_calculada_diluida = (abs_muestra - intercept) / slope
    conc_vino_original = conc_calculada_diluida * fd

    st.markdown(f"""
    Concentración calculada en la dilución: **{conc_calculada_diluida:.4f} mg/L**  
    Concentración del vino original: **{conc_vino_original:.4f} mg/L**
    """)

    # ============================================================
    # ETAPA 4: VALIDACIÓN ANALÍTICA
    # ============================================================

    st.header("Etapa 4: Validación analítica")
    u_interpol = st.number_input("Incertidumbre de la interpolación (mg/L)", min_value=0.0, value=0.05)
    u_pipeta = st.number_input("Incertidumbre pipeta (mL)", min_value=0.0, value=0.01)
    pipeta_vol = st.number_input("Volumen pipeta (mL)", min_value=0.1, value=10.0)
    u_balon = st.number_input("Incertidumbre matraz (mL)", min_value=0.0, value=0.02)
    balon_vol = st.number_input("Volumen matraz (mL)", min_value=0.1, value=100.0)

    u_conc_interpol = conc_vino_original * np.sqrt(
        (u_interpol / conc_calculada_diluida) ** 2 +
        (u_pipeta / pipeta_vol) ** 2 +
        (u_balon / balon_vol) ** 2
    )

    if u_conc_interpol > 1:
        conc_vino_str = f"{round(conc_vino_original):.0f}"
    else:
        conc_vino_str = f"{conc_vino_original:.2f}"

    st.markdown(f"""
    **Incertidumbre combinada:** {u_conc_interpol:.4f} mg/L  
    **Resultado final:** {conc_vino_str} ± {u_conc_interpol:.2f} mg/L
    """)

    # ============================================================
    # ETAPA 5: ANÁLISIS FINAL
    # ============================================================

    st.header("Etapa 5: Análisis final y comparación")
    conc_real = st.number_input("Concentración real conocida (mg/L)", min_value=0.0, value=12.0)
    error_relativo = abs(conc_vino_original - conc_real) / conc_real * 100

    st.markdown(f"""
    **Error relativo:** {error_relativo:.2f} %

    **Interpretación:**
    Un error menor al 5% indica excelente exactitud.  
    Entre 5% y 10% es aceptable.  
    Mayor al 10% sugiere revisar la preparación de estándares o dilución.
    """)

    with st.expander("Mostrar desarrollo completo del cálculo"):
        z = [slope, intercept]
        st.markdown(f"""
        **Paso 1: Cálculo de concentración en la dilución**

        Usando la ecuación de la recta de calibración:

        \[
        A = {z[0]:.4f}C + {z[1]:.4f}
        \]

        Despejando:

        \[
        C = \frac{{A - {z[1]:.4f}}}{{{z[0]:.4f}}}
        \]

        Sustituyendo \(A = {abs_muestra:.4f}\):

        \[
        C = \frac{{{abs_muestra:.4f} - {z[1]:.4f}}}{{{z[0]:.4f}}} = {conc_calculada_diluida:.4f}\, \text{{mg/L}}
        \]

        **Paso 2: Aplicar factor de dilución**

        \[
        C_{{vino}} = C_{{dilución}} \times FD = {conc_calculada_diluida:.4f} \times {fd:.2f} = {conc_vino_original:.4f}\, \text{{mg/L}}
        \]

        **Paso 3: Comparación con valor real**

        \[
        \text{{Error relativo}} = \frac{{|{conc_vino_original:.2f} - {conc_real:.2f}|}}{{{conc_real:.2f}}} \times 100 = {error_relativo:.2f}\%
        \]
        """)

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    main()
