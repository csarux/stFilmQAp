import os
from pathlib import Path
import configparser
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import pyfilmqa as fqa
from skimage.io import imread, imsave
from skimage import img_as_ubyte
from skimage.exposure import rescale_intensity
from skimage.util import invert
from streamlit_image_select import image_select
import streamlit as st

def original():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def rot90():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim)
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def rot180():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim, k=2)
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def rot270():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim, k=3)
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def voltear():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.fliplr(fDim)
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def vrot90():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim))
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def vrot180():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim), k=2)
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def vrot270():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim), k=3)
    dxffilmstr = tif2dxfString(fDim=fDim)
    return dxffilmstr

def tif2dxf(fDim=None):
    pxsp = fqa.TIFFPixelSpacing(os.path.join("img_dir", st.session_state.FilmFileName))
    imsz = fqa.DoseImageSize(fDim)

    if 'fDdf' not in st.session_state:
        ya = np.linspace(0, (imsz[0]-1)*pxsp[0], imsz[0])
        xa = np.linspace(0, (imsz[1]-1)*pxsp[1], imsz[1])
        fDdf = pd.DataFrame(data=np.transpose(fDim), index=ya, columns=xa) # Impuesto por la manera en la que Eclipse orienta el plano de dosis en Portal Dosimetry
        st.session_state.fDdf = fDdf
    if 'fps' not in st.session_state:
        st.session_state.fps = pxsp

    config = configparser.ConfigParser()
    configfile='config/filmQAp.config'
    config.read(configfile)
    dxffilePath = Path(config['DEFAULT']['exportpath'] + st.session_state.PatientId + '/StreamlitFilm.dxf')

    fqa.dxfWriter(Data=fDim, dxfFileName=dxffilePath,
                  AcqType='Acquired Portal', PatientId1=st.session_state.PatientId,
                  PatientId2=st.session_state.PatientId, LastName=st.session_state.LastName,
                  FirstName=st.session_state.FirstName, pxsp=pxsp, imsz=imsz)
    st.success('Exportada la dosis medida por la película en formato dxf: \n' + config['DEFAULT']['exportpath'] + st.session_state.PatientId + '/StremlitFilm.dxf')

def tif2dxfString(fDim=None):
    pxsp = fqa.TIFFPixelSpacing(os.path.join("img_dir", st.session_state.FilmFileName))
    imsz = fqa.DoseImageSize(fDim)

    if 'fDdf' not in st.session_state:
        ya = np.linspace(0, (imsz[0]-1)*pxsp[0], imsz[0])
        xa = np.linspace(0, (imsz[1]-1)*pxsp[1], imsz[1])
        fDdf = pd.DataFrame(data=np.transpose(fDim), index=ya, columns=xa) # Impuesto por la manera en la que Eclipse orienta el plano de dosis en Portal Dosimetry
        st.session_state.fDdf = fDdf
    if 'fps' not in st.session_state:
        st.session_state.fps = pxsp

    dxfstr = fqa.dxfString(Data=fDim, AcqType='Acquired Portal', PatientId1=st.session_state.PatientId,
                           PatientId2=st.session_state.PatientId, LastName=st.session_state.LastName,
                           FirstName=st.session_state.FirstName, pxsp=pxsp, imsz=imsz)
    return dxfstr

st.title('3. Reorientar con respecto al planificador y exportar la dosis medida por la película')


if 'pDdf' not in st.session_state:
    st.error('Error: Plano de dosis del planificador no importado.')
else:
    imPlan = invert(img_as_ubyte(rescale_intensity(st.session_state.pDdf.values, out_range='uint8')))
    st.subheader('Planificador')
    st.image(imPlan)

if 'fDim' not in st.session_state:
    st.error('Error: Plano de dosis de la película no procesado.')
else:
    st.subheader('Película')

    fDim = st.session_state.fDim

    imOrig = invert(img_as_ubyte(rescale_intensity(fDim, out_range='uint8')))
    imR90  = invert(img_as_ubyte(rescale_intensity(np.rot90(fDim), out_range='uint8')))
    imR180 = invert(img_as_ubyte(rescale_intensity(np.rot90(fDim, k=2), out_range='uint8')))
    imR270 = invert(img_as_ubyte(rescale_intensity(np.rot90(fDim, k=3), out_range='uint8')))

    imV     = invert(img_as_ubyte(rescale_intensity(np.fliplr(fDim), out_range='uint8')))
    imVR90  = invert(img_as_ubyte(rescale_intensity(np.rot90(np.fliplr(fDim)), out_range='uint8')))
    imVR180 = invert(img_as_ubyte(rescale_intensity(np.rot90(np.fliplr(fDim), k=2), out_range='uint8')))
    imVR270 = invert(img_as_ubyte(rescale_intensity(np.rot90(np.fliplr(fDim), k=3), out_range='uint8')))

    imSel = image_select("Seleccionar la orientación", [imOrig, imR90, imR180, imR270, imV, imVR90, imVR180, imVR270], use_container_width=False, return_value='index')

    if imSel == 0:
        dxffilmstr = original()
    elif imSel == 1:
        dxffilmstr = rot90()
    elif imSel == 2:
        dxffilmstr = rot180()
    elif imSel == 3:
        dxffilmstr = rot270()
    elif imSel == 4:
        dxffilmstr = voltear()
    elif imSel == 5:
        dxffilmstr = vrot90()
    elif imSel == 6:
        dxffilmstr = vrot180()
    elif imSel == 7:
        dxffilmstr = vrot270()

    if dxffilmstr:
        with st.sidebar:
            st.download_button(label='Descargar dxf', data=dxffilmstr, file_name='Film.dxf', mime='text/csv')

