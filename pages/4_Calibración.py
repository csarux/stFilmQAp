import pyfilmqa as fqa
import configparser
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
st.set_page_config(page_title='FilmQAp', layout="wide")

st.title('4. Calibración')

config = configparser.ConfigParser()
configfile='config/filmQAp.config'
config.read(configfile)

caldf = st.session_state.caldf

cddf = st.session_state.cddf

cda = cddf[['dr', 'dg', 'db']].to_numpy()

vDa = fqa.validatecalibf(cda=cda, config=config, caldf=caldf)

cddf['vD'] = vDa
cddf['uD'] = cddf.D - cddf.vD
cddf['uDr'] = cddf.uD / cddf.D
cddf['uDr_%'] = cddf.uDr * 100

cddf = cddf[(-0.1  < cddf.uDr)  & (cddf.uDr < 0.1)]

colc, colr, colh = st.columns(3)

with colc:
    fig, ax = plt.subplots()
    ax.plot(cddf.D, cddf.dr, 'r-.', label = 'Red medidas')
    ax.plot(cddf.vD, cddf.dr, 'r-', label='Red calib')
    ax.plot(cddf.D, cddf.dg, 'g-.', label = 'Green medidas')
    ax.plot(cddf.vD, cddf.dg, 'g-', label='Green calib')
    ax.plot(cddf.D, cddf.db, 'b-.', label = 'Blue medidas')
    ax.plot(cddf.vD, cddf.db, 'b-', label='Blue calib')
    ax.set_xlabel('Dosis [Gy]')
    ax.set_ylabel('Densidad Óptica')

    ax.legend()

    st.pyplot(fig)

    cddf

with colr:

    fig, ax = plt.subplots()
    ax.plot(cddf.D, cddf['uDr_%'], '-', color='darkcyan')
    ax.set_xlabel('Dosis [Gy]')
    ax.set_ylabel('Residuo relativo [%]')

    st.pyplot(fig)


    fig, ax = plt.subplots()
    ax.plot(cddf.z, cddf.D, '-', color='darkcyan', label='Valor esperado')
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
