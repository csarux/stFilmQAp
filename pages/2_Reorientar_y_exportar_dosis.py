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
    st.session_state.fOrDim = fDim

def rot90():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim)
    st.session_state.fOrDim = fDim

def rot180():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim, k=2)
    st.session_state.fOrDim = fDim

def rot270():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(fDim, k=3)
    st.session_state.fOrDim = fDim

def voltear():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.fliplr(fDim)
    st.session_state.fOrDim = fDim

def vrot90():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim))
    st.session_state.fOrDim = fDim

def vrot180():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim), k=2)
    st.session_state.fOrDim = fDim

def vrot270():
    fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
    fDim = np.rot90(np.fliplr(fDim), k=3)
    st.session_state.fOrDim = fDim

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
    if 'PatientId' not in st.session_state:
        st.session_state.PatientId = config['Demographics']['patientid']
    if 'FirstName' not in st.session_state:
        st.session_state.FirstName = config['Demographics']['patientname']
    if 'LastName' not in st.session_state:
        st.session_state.LastName = config['Demographics']['patientfamilyname']
    if 'Gender' not in st.session_state:
        st.session_state.Gender = config['Demographics']['gender']
    if 'DoseFilmFileName' not in st.session_state:
        st.session_state.DoseFilmFileName = config['FilmPlane']['filename']
    
    dxffilePath = Path(config['DEFAULT']['exportpath'] + st.session_state.DoseFilmFileName + '.dxf')

    fqa.dxfWriter(Data=fDim, dxfFileName=dxffilePath,
                  AcqType='Acquired Portal', PatientId1=st.session_state.PatientId,
                  PatientId2=st.session_state.PatientId, LastName=st.session_state.LastName,
                  FirstName=st.session_state.FirstName, pxsp=pxsp, imsz=imsz)

def tif2dxfString(fDim=None, config=None):
    pxsp = fqa.TIFFPixelSpacing(os.path.join("img_dir", st.session_state.FilmFileName))
    imsz = fqa.DoseImageSize(fDim)

    ya = np.linspace(0, (imsz[0]-1)*pxsp[0], imsz[0])
    xa = np.linspace(0, (imsz[1]-1)*pxsp[1], imsz[1])
    fDdf = pd.DataFrame(data=np.transpose(fDim), index=ya, columns=xa) # Impuesto por la manera en la que Eclipse orienta el plano de dosis en Portal Dosimetry
    st.session_state.fDdf = fDdf
    if 'fps' not in st.session_state:
        st.session_state.fps = pxsp

    if 'PatientId' not in st.session_state:
        st.session_state.PatientId = config['Demographics']['patientid']
    if 'FirstName' not in st.session_state:
        st.session_state.FirstName = config['Demographics']['patientname']
    if 'LastName' not in st.session_state:
        st.session_state.LastName = config['Demographics']['patientfamilyname']
    if 'Gender' not in st.session_state:
        st.session_state.Gender = config['Demographics']['gender']
    if 'DoseFilmFileName' not in st.session_state:
        st.session_state.DoseFilmFileName = config['FilmPlane']['filename']
    
    dxffilePath = Path(config['DEFAULT']['exportpath'] + st.session_state.DoseFilmFileName + '.dxf')

    dxffilmstr = fqa.dxfString(Data=fDim,
                               AcqType='Acquired Portal', PatientId1=st.session_state.PatientId,
                               PatientId2=st.session_state.PatientId, LastName=st.session_state.LastName,
                               FirstName=st.session_state.FirstName, pxsp=pxsp, imsz=imsz)
    return dxffilmstr

st.title('2. Reorientar y exportar')

st.markdown(
'''
Seleccionar la orientación deseada de la imagen de dosis y exportar en el formato elegido
'''
)

if 'fDim' not in st.session_state:
    st.error('Error: Plano de dosis de la película no procesado.')
else:
    st.subheader('Distribución de dosis medida')

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
        original()
    elif imSel == 1:
        rot90()
    elif imSel == 2:
        rot180()
    elif imSel == 3:
        rot270()
    elif imSel == 4:
        voltear()
    elif imSel == 5:
        vrot90()
    elif imSel == 6:
        vrot180()
    elif imSel == 7:
        vrot270()
    
    config = configparser.ConfigParser()
    configfile='config/filmQAp.config'
    config.read(configfile)

    if 'fOrDim' in st.session_state:
        dxffilmstr = tif2dxfString(st.session_state.fOrDim, config=config)
        dcmfilmstr = fqa.dcmWriter(Data=st.session_state.fOrDim, imfile=Path('img_dir', st.session_state.FilmFileName), config=config)
        with st.sidebar:
            st.download_button(label='Descargar dxf', data=dxffilmstr, file_name='Film.dxf', mime='text/csv')
            st.download_button(label='Descargar dcm', data=dcmfilmstr, file_name='Film.dcm')

