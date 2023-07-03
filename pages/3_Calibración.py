import pyfilmqa as fqa
import configparser
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
st.set_page_config(page_title='FilmQAp', layout="wide")

st.title('Calibración')

config = configparser.ConfigParser()
configfile='config/filmQAp.config'
config.read(configfile)

caldf = st.session_state.caldf

cddf = st.session_state.cddf

cda = cddf[['dR', 'dG', 'dB']].to_numpy()

vDa = fqa.validatecalibf(cda=cda, config=config, caldf=caldf)

cddf['vD'] = vDa
cddf['uD'] = cddf.vD - cddf.D
cddf['uDr'] = cddf.uD / cddf.D
cddf['uDr_%'] = cddf.uDr * 100

cddf = cddf[(-0.1  < cddf.uDr)  & (cddf.uDr < 0.1)]

cddf['dRm'] = fqa.calf(cddf.D, *caldf.loc['R'].values)
cddf['dGm'] = fqa.calf(cddf.D, *caldf.loc['G'].values)
cddf['dBm'] = fqa.calf(cddf.D, *caldf.loc['B'].values)

colc, colr, colh = st.columns(3)

with colc:
    fig, ax = plt.subplots()

    ax.plot(cddf.D, cddf.dR, 'r-.', label = 'Red medidas')
    ax.plot(cddf.vD, cddf.dR, 'r-', label='Red calib')
    ax.plot(cddf.D, cddf.dRm, 'r--', label='Red modelo')
    ax.plot(cddf.D, cddf.dG, 'g-.', label = 'Green medidas')
    ax.plot(cddf.vD, cddf.dG, 'g-', label='Green calib')
    ax.plot(cddf.D, cddf.dGm, 'g--', label = 'Green modelo')
    ax.plot(cddf.D, cddf.dB, 'b-.', label = 'Blue medidas')
    ax.plot(cddf.vD, cddf.dB, 'b-', label='Blue calib')
    ax.plot(cddf.D, cddf.dBm, 'b--', label = 'Blue modelo')
    ax.set_xlabel('Dosis [Gy]')
    ax.set_ylabel('Densidad Óptica')

    ax.legend()

    st.pyplot(fig)

    cddf

with colr:

    fig, ax = plt.subplots()
    ax.plot(cddf.D, cddf['uDr_%'], '-', color='darkcyan', label=r'$\frac{D_m - D_c}{D_c}100$'
                                                                '\n' r'$D_m$: Dosis medida'
                                                                '\n' r'$D_c$: Dosis calibración')
    ax.set_xlabel('Dosis [Gy]')
    ax.set_ylabel('Residuo relativo [%]')

    ax.legend()

    st.pyplot(fig)


    fig, ax = plt.subplots()
    ax.plot(cddf.z, cddf.D, '-', color='darkcyan', label='Calibración')
    ax.plot(cddf.z, cddf.vD, '-.', color='darkcyan', label='Medida')
    ax.set_xlabel('z [cm]')
    ax.set_ylabel('Dosis [Gy]')

    ax.legend()

    st.pyplot(fig)


with colh:
    fig, ax = plt.subplots()
    sns.histplot(cddf['uDr_%'])

    ax.set_xlabel('Residuo relativo [%]')
    ax.set_ylabel('Cuentas')
    st.pyplot(fig)

    caldf
