import streamlit as st
import pandas as pd
import pydeck as pdk

# Configuración inicial del proyecto
st.set_page_config(                     # Método de Streamlit para configurar la página
    page_title="Mi App - Proyecto Streamlit",     # Título de la página
    page_icon=":zap:",                  # Icono de la página
    layout="wide",                      # Diseño de la página (ancho completo)
    # Estado inicial de la barra lateral (expandida)
    initial_sidebar_state="expanded",
)

st.title(f'Red de Cargadores Madrid 2024')  # Título principal de la aplicación

st.image('madrid_skyline.jpg',
         caption='Madrid Skyline',
         width=1200)

# Carga y procesamiento de datos
try:
    df = pd.read_csv(
        r'MASTER DATA SCIENCE\Masterclass\Streamlit\app_Streamlit\red_recarga_acceso_publico_2024.csv', sep=';')
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    df = pd.DataFrame()  # DataFrame vacío en caso de error

uploaded_file = st.sidebar.file_uploader(   # Método de Streamlit para cargar archivos
    "Añade un archivo CSV"
)

if uploaded_file is not None:  # Verifica si se ha cargado un archivo
    try:
        # Detectar el tipo de archivo y cargarlo
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, sep=';')
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)

        st.success("Archivo cargado correctamente")
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")

# if uploaded_file is not None:  # Verifica si se ha cargado un archivo
#     try:
#         df = pd.read_csv(uploaded_file, sep=';')
#         st.success("Archivo cargado correctamente")
#     except Exception as e:
#         st.error(f"Error al cargar el archivo: {e}")

# Expansor para mostrar información adicional
with st.expander('Descripción de la aplicación'):
    st.write(
        'Esta aplicación permite analizar la red de cargadores de Madrid para el año 2024.')
    st.write(
        'La información ha sido extraída de la página oficial del Ayuntamiento de Madrid.')
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No hay datos disponibles para mostrar.")

# --------------------------------------------------------------
# FILTROS EN LA BARRA LATERAL BASADOS EN LAS COLUMNAS REALES
# --------------------------------------------------------------
st.sidebar.header('Filtros de datos')

# Solo creamos filtros si tenemos datos
if not df.empty:
    # Filtro por DISTRITO
    if "DISTRITO" in df.columns:
        distritos = ["Todos"] + \
            sorted(df["DISTRITO"].dropna().unique().tolist())
        distrito_seleccionado = st.sidebar.selectbox(
            "Selecciona distrito:", distritos)
    else:
        distrito_seleccionado = "Todos"

    # Filtro por BARRIO (solo si se ha seleccionado un distrito específico)
    if "BARRIO" in df.columns:
        if distrito_seleccionado != "Todos":
            # Filtramos barrios que pertenecen al distrito seleccionado
            barrios_filtrados = df[df["DISTRITO"] ==
                                   distrito_seleccionado]["BARRIO"].dropna().unique()
            barrios = ["Todos"] + sorted(barrios_filtrados.tolist())
        else:
            barrios = ["Todos"] + \
                sorted(df["BARRIO"].dropna().unique().tolist())
        barrio_seleccionado = st.sidebar.selectbox(
            "Selecciona barrio:", barrios)
    else:
        barrio_seleccionado = "Todos"

    # Filtro por OPERADOR
    if "OPERADOR" in df.columns:
        operadores = ["Todos"] + \
            sorted(df["OPERADOR"].dropna().unique().tolist())
        operador_seleccionado = st.sidebar.selectbox(
            "Selecciona operador:", operadores)
    else:
        operador_seleccionado = "Todos"

    # Filtro por EMPLAZAMIENTO
    if "EMPLAZAMIENTO" in df.columns:
        emplazamientos = ["Todos"] + \
            sorted(df["EMPLAZAMIENTO"].dropna().unique().tolist())
        emplazamiento_seleccionado = st.sidebar.selectbox(
            "Selecciona emplazamiento:", emplazamientos)
    else:
        emplazamiento_seleccionado = "Todos"

    # Filtro por ESTADO
    if "ESTADO" in df.columns:
        estados = ["Todos"] + sorted(df["ESTADO"].dropna().unique().tolist())
        estado_seleccionado = st.sidebar.selectbox(
            "Selecciona estado:", estados)
    else:
        estado_seleccionado = "Todos"

    # Filtro por CARACTERISTICAS_EQUIPO (usando multiselect para permitir selección múltiple)
    if "CARACTERISTICAS_EQUIPO" in df.columns:
        # Extraer palabras clave de las características
        caracteristicas_keywords = set()
        for desc in df["CARACTERISTICAS_EQUIPO"].dropna().unique():
            # Dividir por espacios y tomar palabras significativas (por ejemplo, más de 3 caracteres)
            keywords = [word.strip()
                        for word in desc.split() if len(word.strip()) > 3]
            caracteristicas_keywords.update(keywords)

        # Convertir a lista ordenada y permitir selección múltiple
        caracteristicas_list = sorted(list(caracteristicas_keywords))
        caracteristicas_seleccionadas = st.sidebar.multiselect(
            "Características del equipo (palabras clave):",
            caracteristicas_list
        )
    else:
        caracteristicas_seleccionadas = []

    # --------------------------------------------------------------
    # APLICACIÓN DE LOS FILTROS
    # --------------------------------------------------------------
    # Hacemos una copia del DataFrame original
    df_filtrado = df.copy()

    # Aplicamos cada filtro
    if distrito_seleccionado != "Todos" and "DISTRITO" in df.columns:
        df_filtrado = df_filtrado[df_filtrado["DISTRITO"]
                                  == distrito_seleccionado]

    if barrio_seleccionado != "Todos" and "BARRIO" in df.columns:
        df_filtrado = df_filtrado[df_filtrado["BARRIO"] == barrio_seleccionado]

    if operador_seleccionado != "Todos" and "OPERADOR" in df.columns:
        df_filtrado = df_filtrado[df_filtrado["OPERADOR"]
                                  == operador_seleccionado]

    if emplazamiento_seleccionado != "Todos" and "EMPLAZAMIENTO" in df.columns:
        df_filtrado = df_filtrado[df_filtrado["EMPLAZAMIENTO"]
                                  == emplazamiento_seleccionado]

    if estado_seleccionado != "Todos" and "ESTADO" in df.columns:
        df_filtrado = df_filtrado[df_filtrado["ESTADO"] == estado_seleccionado]

    # Aplicar filtros de características (si se han seleccionado)
    if caracteristicas_seleccionadas and "CARACTERISTICAS_EQUIPO" in df.columns:
        # Creamos una máscara inicial todos True
        mask = pd.Series([True] * len(df_filtrado))

        # Por cada característica seleccionada, actualizamos la máscara
        for keyword in caracteristicas_seleccionadas:
            mask = mask & df_filtrado["CARACTERISTICAS_EQUIPO"].str.contains(
                keyword, case=False, na=False)

        # Aplicamos la máscara final
        df_filtrado = df_filtrado[mask]

    # Añadimos métricas para mostrar la información filtrada
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de cargadores", len(df_filtrado))
    with col2:
        if "OPERADOR" in df_filtrado.columns:
            st.metric("Operadores únicos", df_filtrado["OPERADOR"].nunique())
    with col3:
        if "EMPLAZAMIENTO" in df_filtrado.columns:
            st.metric("Tipos de emplazamiento",
                      df_filtrado["EMPLAZAMIENTO"].nunique())

    # --------------------------------------------------------------
    # MAPA ACTUALIZADO CON DATOS FILTRADOS
    # --------------------------------------------------------------
    st.header('Mapa de Cargadores Madrid')

    # Si no hay datos filtrados, mostrar mensaje
    if len(df_filtrado) == 0:
        st.warning(
            "No hay cargadores que coincidan con los filtros seleccionados.")
    else:
        # Aseguramos que las columnas necesarias para el mapa existan
        required_columns = ["LONGITUD", "LATITUD"]
        if all(col in df_filtrado.columns for col in required_columns):
            tooltip = {
                "html": "<b>Ubicación:</b> {UBICACION} <br> <b>Características:</b> {CARACTERISTICAS_EQUIPO} <br> <b>Operador:</b> {OPERADOR} <br> <b>Emplazamiento:</b> {EMPLAZAMIENTO} <br> <b>Estado:</b> {ESTADO}",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white",
                    "fontSize": "14px",
                    "padding": "8px",
                },
            }

            layer = pdk.Layer(
                "ScatterplotLayer",
                df_filtrado,  # Usamos el DataFrame filtrado en lugar del original
                get_position=["LONGITUD", "LATITUD"],
                get_radius=30,
                radius_scale=4,
                radius_min_pixels=2,
                radius_max_pixels=100,
                get_fill_color=[255, 0, 0],
                pickable=True,
                auto_highlight=True,
            )

            # Ajustamos la vista al centro de los datos filtrados
            view_state = pdk.ViewState(
                latitude=df_filtrado['LATITUD'].mean(),
                longitude=df_filtrado['LONGITUD'].mean(),
                zoom=10,
                pitch=0,
            )

            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,
                map_style='mapbox://styles/mapbox/light-v9',
            )

            # Muestra el mapa interactivo en la aplicación Streamlit
            st.pydeck_chart(deck)
        else:
            st.error(
                f"Faltan columnas necesarias para el mapa: {required_columns}")

    # Opcionalmente: añadir una tabla con los resultados filtrados
    with st.expander("Ver detalles de los cargadores filtrados"):
        st.dataframe(df_filtrado)
else:
    st.warning("Carga datos para ver filtros y mapa")
