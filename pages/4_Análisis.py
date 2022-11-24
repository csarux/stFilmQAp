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

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

st.set_page_config(page_title='FilmQAp', layout="wide")

st.title('4. Análisis')

with st.sidebar:
    profile= st.radio('Perfil', ['x', 'y', 'Ambos'], index=2, help='Seleccionar perfiles mostrados')

    method= st.radio('Comparación', ['blend', 'checkerboard', 'diff', 'gamma'], help='Modo de comparación entre las dos distribuciones de dosis')

    diffholder = st.empty()

    gammaholder = st.empty()

    dy = st.slider(
        'Desplazamiento x [mm]',
        -dmax, dmax, 0)

    dx = st.slider(
        'Desplazamiento y [mm]',
        -dmax, dmax, 0)

pDdf = st.session_state.pDdf
px, py = pDdf.columns.values, pDdf.index.values
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
fx, fy = fDdf.columns.values, fDdf.index.values
fps = st.session_state.fps
fDim = fDdf.values

fDo = RBSp(fy, fx, fDim)
yy, xx = np.meshgrid(py, px, sparse=True)
fDrim = fDo.ev(yy + dy, xx + dx)
fDrim[fDrim < 0] = 0 # Acotar la dosis a valores positivos para evitar artefactos producidos en la extrapolación
fDrdf = pd.DataFrame(data=fDrim, index=py, columns=px)
if method in ['blend', 'checkerboard']:
    diffholder.empty()
    gammaholder.empty()
    cmpim = cmpimgs(fDrim, pDim, method=method)

elif method is 'diff':
    gammaholder.empty()
    with diffholder.container():
        cmpim = fDrim - pDim
        diffmin, diffmax = floor(cmpim.min()), ceil(cmpim.max())
        diffrange = st.slider('Rango de la diferencia [Gy]', diffmin, diffmax, [diffmin, diffmax], key='diffrange')
        cmpim[cmpim > diffrange[1]] = np.nan
        cmpim[cmpim < diffrange[0]] = np.nan

elif method is 'gamma':
    diffholder.empty()
    with gammaholder.container():
        doseperc = st.slider('Diferencia de dosis [%]', 1, 5, 2, key='gdoseperc')
        distmm = st.slider('Distancia [mm]', 1, 5, 2, key='gdmm')
        dosecutoffperc = st.slider('Umbral de dosis [%]', 1, 50, 10, key='gth')
        local = st.checkbox('Local', value=True, key='glocal')

    gamma_options = {
        'dose_percent_threshold': doseperc,
        'distance_mm_threshold': distmm,
        'lower_percent_dose_cutoff': dosecutoffperc,
        'interp_fraction': 10,  # Should be 10 or more for more accurate results
        'max_gamma': 2,
        'random_subset': None,
        'local_gamma': local,
        'ram_available': 2**30,  # 1 GB
    }

    cmpim = gamma((py/10, px/10), pDim, ((py+dy)/10, (px+dx)/10), fDrim, **gamma_options)
    gamma1 = np.copy(cmpim)
    gamma1[gamma1 > 1] = np.nan

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

    if profile in ['x', 'Ambos']:
        ax.plot(px, pDim[pry, :], '-', color='darkred', label='Plan x')
        ax.plot(px, fDrim[pry, :], '-', color='red', label='Film x')
        ax.plot(prx, pDim[pry, prx], 'x', color='darkred', label='Plan {:.2f}'.format(pDim[pry, prx]))
        ax.plot(prx, fDrim[pry, prx], 'o', color='red', label='Film {:.2f}'.format(fDrim[pry, prx]))
        ax.set_xlabel('x [mm]')

    if profile in ['y', 'Ambos']:
        ax.plot(py, pDim[:, prx], '-', color='darkgreen', label='Plan y')
        ax.plot(py, fDrim[:, prx], '-', color='darkcyan', label='Film y')
        ax.plot(pry, pDim[pry, prx], 'x', color='darkgreen', label='Plan {:.2f}'.format(pDim[pry, prx]))
        ax.plot(pry, fDrim[pry, prx], 'o', color='darkcyan', label='Film {:.2f}'.format(fDrim[pry, prx]))
        ax.set_xlabel('y [mm]')

    if profile is 'Ambos':
        ax.set_xlabel('x, y [mm]')

    ax.set_ylabel('Dosis [Gy]')
    ax.legend()

    st.pyplot(fig)

with colr:
    cmpa = np.ravel(cmpdf.values)

    fig, ax = plt.subplots()
    if method is 'gamma':
        gamma1a = np.ravel(gamma1)
        sns.histplot(cmpa, binrange=(0, 2), bins=30, color='red')
        cmpacnts, bins = np.histogram(cmpa, range=(0, 2), bins=30)
        sns.histplot(gamma1a, binrange=(0, 2), bins=30)
        gamma1acnts, bins = np.histogram(gamma1a, range=(0, 2), bins=30)
        gammaresult = gamma1acnts.sum() / cmpacnts.sum() * 100
        ax.set_ylabel('Cuentas')
        ax.set_xlabel('Índice $\gamma$')
        gammamsg = 'Puntos con $\gamma$ < 1: {:.2f}%'.format(gammaresult)
        ax.text(0.65, 0.75, gammamsg,
            horizontalalignment='center',
            verticalalignment='center',
            transform = ax.transAxes)
    elif method is 'diff':
        bins = (diffrange[1]-diffrange[0])*10
        if bins < 50: bins = 50
        sns.histplot(cmpa, binrange=(diffrange[0], diffrange[1]), bins=bins)
        ax.set_ylabel('Cuentas')
        ax.set_xlabel('Diferencia de dosis [Gy]')
        meandiff = np.nanmean(cmpa)
        meanmsg = 'Diferencia media: {:.2f} Gy'.format(meandiff)
        stddiff = np.nanstd(cmpa)
        stdmsg = 'Sigma diferencia: {:.2f} Gy'.format(stddiff)
        ax.text(0.8, 0.95, meanmsg,
            horizontalalignment='center',
            verticalalignment='center',
            transform = ax.transAxes)
        ax.text(0.8, 0.90, stdmsg,
            horizontalalignment='center',
            verticalalignment='center',
            transform = ax.transAxes)

    if method not in ['blend', 'checkerboard']:
        st.pyplot(fig)
