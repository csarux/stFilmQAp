import streamlit as st
st.set_page_config(page_title='FilmQAp')

st.title('Dosimetría fotográfica con películas radiocrómicas')

st.markdown(
'''
**FilmQAp** es una aplicación para procesar películas radiocrómicas mediante un esquema de digitalización única (*SSP, single scan protocol*) leyéndose la película en la misma digitalización en la que se calibra el escáner. Si en un corto intervalo de tiempo se irradian las películas de medida y de calibración, el procedimiento es independiente del tiempo de evolución de la película, evitando tener que esperar el tiempo de estabilización. El procesado utiliza un análisis multicanal mediante promedios no locales. La calibración se realiza mediante un modelo sensitométrico de crecimiento con la dosis de dos fases del polímero presente en la capa sensible de la película. Las condiciones particulares que resultan del proceso de fabricación del lote, su conservación, el fondo y el estado del escáner se determinan en la digitalización. El algoritmo corrige el efecto lateral del escáner.

La aplicación produce los archivos de dosis en formato `dxf` (formato de intercambio de Varian) que se pueden analizar mediante *Portal Dosimetry*.
'''
)

st.subheader('Procedimiento')

st.markdown(
'''     | **Página** | **Acciones** |
        |----------|---------|
        | Plano dosis planificador       | Procesar el plano de dosis calculado en el planificador (formato `DICOM`). Convertirlo a formato `dxf`       |
        | Plano dosis película           | Importar la imagen digitalizada en formato `TIFF` (16 bits por canal). Etiquetar en la imagen digitalizada las regiones relevantes para aplicar el *SSP*. Determinar la dosis en la película.| 
        | Reorientar y exportar dosis    | Comparar la distribución epacial del plano de dosis calculado con la del medido para hacer coincidir su orientación. Exportar la distribución en formato `dxf`.| '''
)

st.subheader('Utilidades')

st.markdown(
'''
        **FilmQAp** ofrece utilidades adicionales que complementan su funcionalidad'''
)

st.markdown(
'''     | **Página** | **Acciones** |
        |----------|--------|
        | Análisis          | Analizar la coincidencia entre las distribuciones medidas y calculadas de forma autónoma mediante diferencias de dosis y mapas de índice gamma (*experimental*).|
        | Calibración       | Mostrar las ajustes de calibración actualizados mediante el *SSP*. Valorar las incertidumbres de medida. | 
        | Configuración     | Mostrar los parámetros de configuración de la aplicación. | '''
)
