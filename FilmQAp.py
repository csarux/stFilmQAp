import streamlit as st

st.title('Dosimetría fotográfica con películas radiocrómicas')

st.markdown(
'''
Aplicación para procesar películas radiocrómicas mediante un esquema de digitalización única (SSP, *single scan protocol*) leyéndose la película en la misma digitalización en la que se calibra el escáner. Si la película de calibración se ha irradido en la misma sesión que la película a medir, el procedimiento es independiente del tiempo de evolución de la película, evitando tener que esperar el tiempo de estabilización. El procesado utiliza un análisis multicanal mediante promedios no locales. La calibración se realiza mediante un modelo sensitométrico de crecimiento con la dosis de dos fases del polímero, válido para un modelo de escáner y película dados. Las condiciones particulares resultado del proceso de fabricación del lote, su conservación, el fondo y el estado del escáner se establecen durante la digitalización. El algoritmo corrige el efecto lateral.
'''
)

st.subheader('Procedimiento')

st.markdown(
'''     | **Página** | **Acciones** |
        |----------|---------|
        | Plano dosis planificador       | Procesar el plano de dosis calculado en el planificador (formato `DICOM`). Convertirlo a formato `dxf`       |
        | Plano dosis película           | Importar la imagen digitalizada en formato `TIFF` (16 bits por canal). Etiquetar en la imagen digitalizada las regiones relevantes para aplicar el *SSP*. Determinar la dosis en la película. Reorientar el plano y exportar la distribución espacial de dosis medida en formato `dxf`| '''
)
