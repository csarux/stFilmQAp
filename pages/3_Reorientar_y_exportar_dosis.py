import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

st.title('3. Reorientar y exportar la dosis medida por la película')

col1, col2 = st.columns(2)
with col1:
    st.subheader('Referencia del planificador')
    pfig, pax = plt.subplots()
    sns.heatmap(st.session_state.pDdf, cmap='jet', xticklabels=False, yticklabels=False)
    st.pyplot(pfig)

if 'fDim' not in st.session_state:
    st.error('Error: Plano de dosis de la película no procesado.')
else:
    st.subheader('Película')
    col1, col2 = st.columns(2)
    with col1:
        fDim = np.array(st.session_state.fDim).reshape((st.session_state.fcols, st.session_state.frows))
        fDx = np.arange(st.session_state.fcols)
        fDy = np.arange(st.session_state.frows)
        fDodf = pd.DataFrame(data=fDim, index=fDx, columns=fDy)
        fofig, foax = plt.subplots()
        sns.heatmap(fDodf, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(fofig)
    with col2:
        fD90df = pd.DataFrame(data=np.rot90(fDim), index=fDy, columns=fDx)
        f90fig, f90ax = plt.subplots()
        sns.heatmap(fD90df, cmap='jet', xticklabels=False, yticklabels=False)
        st.pyplot(f90fig)
