import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Ansiedad en la población mexicana", layout="centered")

# --- TÍTULO ---
st.title("📊 Ansiedad en la población mexicana")
st.markdown("Explora las diferencias en la frecuencia de ansiedad entre hombres y mujeres usando datos de ENSANUT 2022-2023.")

# --- CARGAR DATOS DESDE GITHUB ---
@st.cache_data
def cargar_datos_desde_github():
    url = "https://raw.githubusercontent.com/Mexaddon/ENSANUTans_2023-2024/main/ejercicio%20analisis%20de%20datos_modificada.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Género', 'Ansiedad_frecuencia'])
    return df

df = cargar_datos_desde_github()

# --- SELECCIÓN DE GÉNERO ---
genero = st.selectbox("Selecciona el grupo de análisis:", ['Ambos', 'Hombre', 'Mujer'])

# --- FILTRADO DE DATOS ---
if genero == 'Hombre':
    df_filtrado = df[df['Género'] == 1]
elif genero == 'Mujer':
    df_filtrado = df[df['Género'] == 2]
else:
    df_filtrado = df.copy()

# --- TABLA DE FRECUENCIAS (si es Hombre o Mujer) ---
if genero != 'Ambos':  # 👈 NUEVO
    st.subheader("📋 Tabla de frecuencias de ansiedad")  # 👈 NUEVO
    niveles = {  # 👈 NUEVO
        0: 'Nunca',
        2: 'Mensual o múltiples veces',
        1: 'Semanal o diario'
    }
    frecuencia = df_filtrado['Ansiedad_frecuencia'].map(niveles).value_counts().rename_axis("Frecuencia de Ansiedad").reset_index(name="Conteo")  # 👈 NUEVO
    frecuencia["Porcentaje"] = (frecuencia["Conteo"] / frecuencia["Conteo"].sum() * 100).round(2)  # 👈 NUEVO
    st.dataframe(frecuencia)  # 👈 NUEVO

# --- GRÁFICO DE BARRAS: PROMEDIO DE ANSIEDAD POR GÉNERO ---
st.subheader("📊 Promedio de frecuencia de ansiedad por género")

# Calcular promedios
promedios = df.groupby('Género')['Ansiedad_frecuencia'].mean()
labels = ['Hombres', 'Mujeres']
plt.figure(figsize=(6, 4))
sns.barplot(x=labels, y=promedios.values, palette="viridis")
plt.ylabel('Promedio de ansiedad')
plt.xlabel('Género')
plt.ylim(0, 2)
st.pyplot(plt)

# --- GRÁFICO DE PASTEL: DISTRIBUCIÓN DE NIVELES DE ANSIEDAD ---
st.subheader("🥧 Distribución de niveles de ansiedad")

# Etiquetas descriptivas
niveles = {
    0: 'Nunca',
    2: 'Mensual o múltiples veces',
    1: 'Semanal o diario'
}
# Contar ocurrencias
conteo = df_filtrado['Ansiedad_frecuencia'].map(niveles).value_counts()

# Gráfico
plt.figure(figsize=(6, 6))
plt.pie(conteo.values, labels=conteo.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
plt.axis('equal')
st.pyplot(plt)

# --- ANÁLISIS ESTADÍSTICO ---
if genero == 'Ambos':
    hombres = df[df['Género'] == 1]['Ansiedad_frecuencia']
    mujeres = df[df['Género'] == 2]['Ansiedad_frecuencia']

    # Pruebas de normalidad
    shapiro_h = stats.shapiro(hombres)
    shapiro_m = stats.shapiro(mujeres)

    # Prueba de igualdad de varianzas
    levene_test = stats.levene(hombres, mujeres)

    # Selección de prueba estadística
    if shapiro_h.pvalue > 0.05 and shapiro_m.pvalue > 0.05:
        if levene_test.pvalue > 0.05:
            test_name = 't de Student'
            resultado = stats.ttest_ind(hombres, mujeres, equal_var=True)
        else:
            test_name = 't de Welch'
            resultado = stats.ttest_ind(hombres, mujeres, equal_var=False)
    else:
        test_name = 'U de Mann-Whitney'
        resultado = stats.mannwhitneyu(hombres, mujeres)

    # Mostrar resultados
    st.subheader("📊 Resultados Estadísticos")
    st.markdown(f"""
    - **Prueba de normalidad (Shapiro-Wilk):**
        - Hombres: p = {shapiro_h.pvalue:.4f}
        - Mujeres: p = {shapiro_m.pvalue:.4f}
    - **Prueba de varianzas (Levene):** p = {levene_test.pvalue:.4f}
    - **Prueba utilizada:** {test_name}
    - **Estadístico:** {resultado.statistic:.4f}
    - **Valor p:** {resultado.pvalue:.4f}
    """)

    st.subheader("📌 Interpretación")
    if resultado.pvalue < 0.05:
        st.success("✅ Hay diferencias significativas en la frecuencia de ansiedad entre hombres y mujeres.")
    else:
        st.info("ℹ️ No hay diferencias significativas en la frecuencia de ansiedad entre hombres y mujeres.")
else:
    st.info("Selecciona 'Ambos' para comparar hombres y mujeres estadísticamente.")
