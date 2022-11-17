import streamlit as st
import os
from pathlib import Path
import configparser
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import pyfilmqa as fqa

def original():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    tif2dxf(fDim=fDim)

def rot90():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim)
    tif2dxf(fDim=fDim)

def rot180():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim, k=2)
    tif2dxf(fDim=fDim)

def rot270():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim, k=3)
    tif2dxf(fDim=fDim)

def voltear():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.fliplr(fDim)
    tif2dxf(fDim=fDim)

def vrot90():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim))
    tif2dxf(fDim=fDim)

def vrot180():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim), k=2)
    tif2dxf(fDim=fDim)

def vrot270():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim), k=3)
    tif2dxf(fDim=fDim)

def tif2dxf(fDim=None):
    pxsp = fqa.TIFFPixelSpacing(os.path.join("img_dir", st.session_state.FilmFileName))
    imsz = fqa.DoseImageSize(fDim)
    config = configparser.ConfigParser()
    configfile='config/filmQAp.config'
    config.read(configfile)
    dxffilePath = Path(config['DEFAULT']['exportpath'] + st.session_state.PatientId + '/StreamlitFilm.dxf')

    fqa.dxfWriter(Data=fDim, dxfFileName=dxffilePath,
                  AcqType='Acquired Portal', PatientId1=st.session_state.PatientId,
                  PatientId2=st.session_state.PatientId, LastName=st.session_state.LastName,
                  FirstName=st.session_state.FirstName, pxsp=pxsp, imsz=imsz)
    st.success('Exportada la dosis medida por la película en formato dxf: \n' + config['DEFAULT']['exportpath'] + st.session_state.PatientId + '/StremlitFilm.dxf')

st.title('3. Reorientar y exportar la dosis medida por la película')

helpmsg = 'Clickar el botón con la orientación correcta para exportar la imagen de dosis medida.'

if 'pDdf' not in st.session_state:
    st.error('Error: Plano de dosis del planificador no importado.')
else:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Referencia del planificador')
        pfig, pax = plt.subplots()
        sns.heatmap(st.session_state.pDdf, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(pfig)
    with col2:
        rgmax = float(st.session_state.pDdf.max(axis=1).max())
        dmin, dmax = st.slider(
            'Select a range of values',
            0.0, rgmax, (0.0, rgmax))
        st.write()

if 'fDim' not in st.session_state:
    st.error('Error: Plano de dosis de la película no procesado.')
else:
    st.subheader('Película')
    col1, col2 = st.columns(2)
    with col1:
        fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
        fDx = np.arange(st.session_state.fcols)
        fDy = np.arange(st.session_state.frows)

        st.button(label="Original", on_click=original, help=helpmsg)
        fDodf = pd.DataFrame(data=fDim, index=fDx, columns=fDy)
        fofig, foax = plt.subplots()
        sns.heatmap(fDodf, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(fofig)

        st.button(label="Rotar 90", on_click=rot90, help=helpmsg)
        fD90df = pd.DataFrame(data=np.rot90(fDim), index=fDy, columns=fDx)
        f90fig, f90ax = plt.subplots()
        sns.heatmap(fD90df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(f90fig)

        st.button(label="Rotar 180", on_click=rot180, help=helpmsg)
        fD180df = pd.DataFrame(data=np.rot90(fDim, k=2), index=fDx, columns=fDy)
        f180fig, f180ax = plt.subplots()
        sns.heatmap(fD180df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(f180fig)

        st.button(label="Rotar 270", on_click=rot180, help=helpmsg)
        fD270df = pd.DataFrame(data=np.rot90(fDim, k=3), index=fDy, columns=fDx)
        f270fig, f270ax = plt.subplots()
        sns.heatmap(fD270df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(f270fig)
    with col2:
        st.button(label="Voltear", on_click=voltear, help=helpmsg)
        fDv90df = pd.DataFrame(data=np.fliplr(fDim), index=fDx, columns=fDy)
        fv90fig, fv90ax = plt.subplots()
        sns.heatmap(fDv90df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(fv90fig)

        st.button(label="Voltear y rotar 90", on_click=vrot90, help=helpmsg)
        fDv90df = pd.DataFrame(data=np.rot90(np.fliplr(fDim)), index=fDy, columns=fDx)
        fv90fig, fv90ax = plt.subplots()
        sns.heatmap(fDv90df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(fv90fig)

        st.button(label="Voltear y rotar 180", on_click=vrot180, help=helpmsg)
        fDv180df = pd.DataFrame(data=np.rot90(fDim, k=2), index=fDx, columns=fDy)
        fv180fig, fv180ax = plt.subplots()
        sns.heatmap(fDv180df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(fv180fig)

        st.button(label="Voltear y rotar 270", on_click=vrot270, help=helpmsg)
        fDv270df = pd.DataFrame(data=np.rot90(fDim, k=3), index=fDy, columns=fDx)
        fv270fig, fv270ax = plt.subplots()
        sns.heatmap(fDv270df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(fv270fig)
