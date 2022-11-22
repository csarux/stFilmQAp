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
from pymedphys import gamma
import logging
import streamlit as st

dmax = 20 # Desplazamiento másximo permitido

gamma_options = {
    'dose_percent_threshold': 3,
    'distance_mm_threshold': 3,
    'lower_percent_dose_cutoff': 1,
    'interp_fraction': 10,  # Should be 10 or more for more accurate results
    'max_gamma': 2,
    'random_subset': None,
    'local_gamma': True,
    'ram_available': 4**29,  # 1/2 GB
}

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

st.set_page_config(page_title='FilmQAp', layout="wide")

st.title('4. Análisis')

with st.sidebar:
    method= st.radio('Comparación', ['blend', 'checkerboard', 'diff', 'gamma'], help='Modo de comparación entre las dos distribuciones de dosis')

    dx = st.slider(
        'Desplazamiento x [mm]',
        -dmax, dmax, 0)

    dy = st.slider(
        'Desplazamiento y [mm]',
        -dmax, dmax, 0)

pDdf = st.session_state.pDdf
px, py = pDdf.columns, pDdf.index
pps = st.session_state.pps
pDim = pDdf.values

with st.sidebar:
    pry = st.slider(
        'Posición perfil x [mm]',
        floor(py.min()), floor(py.max()), floor((py.max() - py.min())*.5))

    prx = st.slider(
        'Posición perfil y [mm]',
        floor(px.min()), floor(px.max()), floor((px.max() - px.min())*.5))

fDdf = st.session_state.fDdf
fx, fy = fDdf.columns, fDdf.index
fps = st.session_state.fps
fDim = fDdf.values

fDo = RBSp(fy, fx, fDim)
yy, xx = np.meshgrid(py, px, sparse=True)
fDrim = fDo.ev(yy + dx, xx + dy)
fDrim[fDrim < 0] = 0 # Acotar la dosis a valores positivos para evitar artefactos producidos en la extrapolación
fDrdf = pd.DataFrame(data=fDrim, index=py, columns=px)
if method in ['blend', 'checkerboard']:
    cmpim = cmpimgs(fDrim, pDim, method=method)
elif method is 'diff':
    cmpim = fDrim - pDim
elif method is 'gamma':
    cmpim = gamma((px, py), pDim, (fy+dy, fx+dx), fDim, **gamma_options)

cmpdf = pd.DataFrame(data=cmpim, index=py, columns=px)

coll, colc, colr = st.columns([1, 1, 1])

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

with colc:

    fig, ax = plt.subplots()
    sns.heatmap(cmpdf, cmap='jet', cbar_kws={'label': 'Dosis [Gy]'})
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

coll, colr = st.columns(2)

with coll:
    fig, ax = plt.subplots()
    ax.plot(px, pDim[pry, :], '-', color='darkred', label='Plan x')
    ax.plot(py, fDrim[pry, :], '-', color='red', label='Film x')
    ax.plot(px, pDim[:, prx], '-', color='darkgreen', label='Plan y')
    ax.plot(py, fDrim[:, prx], '-', color='darkcyan', label='Film y')
    ax.plot(prx, pDim[pry, prx], 'x', color='darkred', label='Plan {:.2f}'.format(pDim[pry, prx]))
    ax.plot(prx, fDrim[pry, prx], 'o', color='red', label='Film {:.2f}'.format(fDrim[pry, prx]))
    ax.plot(pry, pDim[pry, prx], 'x', color='darkgreen', label='Plan {:.2f}'.format(pDim[pry, prx]))
    ax.plot(pry, fDrim[pry, prx], 'o', color='darkcyan', label='Film {:.2f}'.format(fDrim[pry, prx]))

    ax.set_xlabel('x, y [mm]')
    ax.set_ylabel('Dosis [Gy]')

    ax.legend()

    st.pyplot(fig)

with colr:
    cmpa = np.ravel(cmpdf.values)

    fig, ax = plt.subplots()
    sns.histplot(cmpa, binrange=(cmpa.min(), cmpa.max()), bins=30)
    ax.set_xlabel('Diferencia de dosis [Gy]')
    ax.set_ylabel('Cuentas')
    if method not in ['blend', 'checkerboard']:
        st.pyplot(fig)
