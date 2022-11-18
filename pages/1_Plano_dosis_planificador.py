import pydicom as dicom
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pyfilmqa as fqa
# - Config file
import configparser
import streamlit as st
st.set_page_config(page_title='FilmQAp')

st.header('1. Procesar el plano de dosis calculado en el planificador')

dcmplan = st.file_uploader('Archivo DICOM de dosis:', help='Seleccionar el archivo DICOM exportado del planificador.')

if dcmplan is not None:
    # Leer el fichero DICOM
    dcmf = dicom.read_file(dcmplan)

    if 'PatientId' not in st.session_state:
        st.session_state.PatientId = dcmf.PatientID
    if 'LastName' not in st.session_state:
        st.session_state.LastName = str(dcmf.PatientName).split('^')[0]
    if 'FirstName' not in st.session_state:
        st.session_state.FirstName = str(dcmf.PatientName).split('^')[1]
    if 'Dmax' not in st.session_state:
        st.session_state.Dmax = (dcmf.pixel_array*dcmf.DoseGridScaling).max() * 1.1

    # Leer la configuración
    config = configparser.ConfigParser()
    configfile='config/filmQAp.config'
    config.read(configfile)

    # Mostrar los datos del paciente
    apellidos, nombre = str(dcmf.PatientName).split('^')
    apellidos = apellidos.split()
    apellidos = [apellido[0] + apellido[1:].lower() for apellido in apellidos]
    apellidos = ' '.join(apellidos)
    nombres = nombre.split()
    nombres = [nombre[0] + nombre[1:].lower() for nombre in nombres]
    nombre = ' '.join(nombres)
    patdict = {'Historia' : dcmf.PatientID, 'Apellidos' :apellidos, 'Nombre' : nombre}
    patdf = pd.DataFrame(patdict, index=[0])

    st.subheader('Datos del Paciente')
    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    st.table(patdf)


    # Mostrar el plano de dosis

    st.subheader('Plano de dosis')

    Dx = np.arange(0, dcmf.Columns*dcmf.PixelSpacing[0], dcmf.PixelSpacing[0])
    Dy = np.arange(0, dcmf.Rows*dcmf.PixelSpacing[1], dcmf.PixelSpacing[1])
    Dim = dcmf.pixel_array * dcmf.DoseGridScaling
    Dosesdf = pd.DataFrame(data=Dim, index=Dy, columns=Dx)
    if 'pDdf' not in st.session_state:
        st.session_state.pDdf = Dosesdf

    fig, ax = plt.subplots()
    sns.heatmap(Dosesdf, cmap='jet', cbar_kws={'label': 'Dosis [Gy]'})
    ax.xaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')

    st.pyplot(fig)

    plandxf = fqa.dcm2dxf(dcmf=dcmf, config=config)
    if plandxf:
        st.success('Exportado el archivo RT Dose en formato dxf: \n' + str(plandxf))
