import pandas as pd
import numpy as np
import pydicom as dicom
from pymedphys.dicom import zyx_and_dose_from_dataset
import streamlit as st

st.header('Tests pymedphys')

dcmplan = st.file_uploader('Archivo DICOM de dosis:', help='Seleccionar el archivo DICOM exportado del planificador.')

if dcmplan is not None:
    # Leer el fichero DICOM
    dcmf = dicom.read_file(dcmplan, force=True)


    x, y = zyx_and_dose_from_dataset(dcmf)

    x[0]
    x[1]
    x[2]
