import streamlit as st
st.set_page_config(page_title='chromLit')

st.title('Dosimetría fotográfica con películas radiocrómicas')

st.markdown(
'''
`chromLit` es una aplicación para procesar películas radiocrómicas mediante un protocolo de digitalización única (*SSP, single scan protocol*) en el que la película se lee en la misma digitalización en la que se calibra el escáner.

Si en un corto intervalo de tiempo se irradian las películas de medida y de calibración, el procedimiento es independiente del tiempo de evolución de la película, evitando tener que esperar el tiempo de estabilización. 

El procesado utiliza un análisis multicanal mediante promedios no locales. 

La calibración se realiza mediante un modelo sensitométrico de crecimiento con la dosis de dos tipos de absorbentes, dos fases del polímero presente en la capa sensible de la película. La cinética con la dosis de estas fases se caracteriza previamente para los modelos de escáner y película empleados. Las condiciones particulares que resultan del proceso de fabricación del lote, su conservación, el fondo y el estado del escáner se determinan en la digitalización. 

El algoritmo corrige el efecto lateral del escáner.

La aplicación puede producir los archivos de dosis en formato `dxf` (formato de texto definido por Varian), formato `TIFF`y como planos de dosis formato `DICOM`. 
'''
)

st.subheader('Procedimiento')

st.markdown(
'''     | **Etapa** | **Acciones** |
        |----------|---------|
        | Preparación       | Cortar la película de medida, la de calibración y la de fondo marcando la orientación (alargada, apaisada)      |
        | Irradiación       | Irradiar la película de medida y la de calibración en un corto periodo de tiempo. En esta etapa la orientación no es relevante       |
        | Plano dosis película           | Digitalizar conjuntamente la película de medida, la de calibración, la de fondo con indicación de la posición en la bandeja del escáner, respetando la orientación de calibración. Procesar la imagen.| 
        | Exportación       | Reorientar la imagen de dosis y exportar en el formato deseado.     |
'''
)