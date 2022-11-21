import pyfilmqa as fqa
import configparser
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.interpolate import RectBivariateSpline as RBSp
from skimage.transform import resize
from math import ceil, floor
from skimage.util import compare_images as cmpimgs
import streamlit as st

st.set_page_config(page_title='FilmQAp', layout="wide")

st.title('4. Análisis')

config = configparser.ConfigParser()
configfile='config/filmQAp.config'
config.read(configfile)

pDdf = st.session_state.pDdf
px, py = pDdf.columns, pDdf.index
pps = float(config['DosePlane']['pixelsize'])
pDim = pDdf.values

fDim, fcols, frows, fps = st.session_state.fDim, st.session_state.fcols, st.session_state.frows, st.session_state.fps*10
fDim = np.transpose(fDim)
fx, fy = np.arange(0, fcols*fps-1e-6, fps), np.arange(0, frows*fps, fps)
fDdf = pd.DataFrame(data=fDim, index=fy, columns=fx)
frx, fry = np.arange(0, ceil(fx[-1]) * pps, pps), np.arange(0, ceil(fy[-1]) * pps, pps)
fDrim = resize(fDim, (fry.shape[0], frx.shape[0]))
fDrdf = pd.DataFrame(data=fDrim, index=fry, columns=frx)
fDo = RBSp(fy, fx, fDim)
yy, xx = np.meshgrid(py, px, sparse=True)
fDrim = fDo.ev(yy, xx)
fDrdf = pd.DataFrame(data=fDrim, index=py, columns=px)
difim = cmpimgs(fDrim, pDim)
difim = fDrim - pDim
difdf = pd.DataFrame(data=difim, index=py, columns=px)

with st.sidebar:
    pry = st.slider(
        'Posición perfil x [mm]',
        floor(py.min()), floor(py.max()), floor((py.max() - py.min())*.5))

    prx = st.slider(
        'Posición perfil y [mm]',
        floor(px.min()), floor(px.max()), floor((px.max() - px.min())*.5))

coll, colc, colr = st.columns([3)

with coll:

    fig, ax = plt.subplots()
    sns.heatmap(pDdf, cmap='jet', cbar_kws={'label': 'Dosis [Gy]'})
    ax.xaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')

    ax.plot([px.min(), px.max()], [pry, pry], 'r-')
    ax.plot([prx, prx], [py.min(), py.max()], 'r-')

    st.pyplot(fig)

    fig, ax = plt.subplots()
    ax.plot(px, pDim[pry, :], '-', color='darkred')
    ax.plot(py, fDrim[pry, :], '-', color='red')
    ax.plot(px, pDim[:, prx], '-', color='darkgreen')
    ax.plot(py, fDrim[:, prx], '-', color='green')

    st.pyplot(fig)

with colc:

    fig, ax = plt.subplots()
    sns.heatmap(difdf, cmap='jet', cbar_kws={'label': 'Dosis [Gy]'})
    ax.xaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')

    ax.plot([px.min(), px.max()], [pry, pry], 'r-')
    ax.plot([prx, prx], [py.min(), py.max()], 'r-')

    st.pyplot(fig)

with colr:
    fig, ax = plt.subplots()
    sns.heatmap(fDrdf, cmap='jet', cbar_kws={'label': 'Dosis [Gy]'})
    ax.xaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_locator(ticker.MultipleLocator(40))
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')

    ax.plot([px.min(), px.max()], [pry, pry], 'r-')
    ax.plot([prx, prx], [py.min(), py.max()], 'r-')

    st.pyplot(fig)

    difa = np.ravel(difdf.values)

    fig, ax = plt.subplots()
    sns.histplot(difa, binrange=(difa.min(), difa.max()), bins=30)
    ax.set_xlabel('Diferencia de dosis [Gy]')
    ax.set_ylabel('Cuentas')
    st.pyplot(fig)
