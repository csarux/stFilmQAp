import os
import pydicom as dicom
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pyfilmqa as fqa
from skimage.io import imread, imsave
from skimage import img_as_ubyte
from skimage.exposure import rescale_intensity
from streamlit_img_label.manage import ImageManager, ImageDirManager
from streamlit_img_label import st_img_label
# - Config file
import configparser
import streamlit as st
st.set_page_config(page_title='FilmQAp')


def run(img_path, labels):
    st.set_option("deprecation.showfileUploaderEncoding", False)
    # Main content: annotate images
    st.subheader('Etiquetar regiones')
    im = ImageManager(img_path)
    img = im.get_img()
    resized_img = im.resizing_img()
    resized_rects = im.get_resized_rects()
    rects = st_img_label(resized_img, box_color="red", rects=resized_rects)

    def process():
        imfile = 'img_dir/' + scim.name
        im.save_annotation()
        image_annotate_file_name = scim.name.split(".")[0] + ".xml"
     
        lbdf = pd.DataFrame(im._current_rects)
        lbdf.to_csv('tmp/bb.csv')

        # Segmentar la imagen
        fqa.segRegs(imfile=imfile)

        # Leer la configuración
        config = configparser.ConfigParser()
        configfile='config/filmQAp.config'
        config.read(configfile)

        if 'Dmax' not in st.session_state:
            st.error('Error: Plano de dosis calculado en el planificador no introducido, no es posible completar el postprocesado de la dosis medida por la película.')
        else:
        # Determinar las coordenadas para la corrección lateral
            cdf = fqa.coordOAC(imfile=imfile)
            # Determinación del fondo
            abase = fqa.baseDetermination(imfile=imfile, config=config)
            # Calibración de la digitalización
            caldf, cddf, fps = fqa.PDDCalibration(config=config, imfile=imfile, base=abase)
            # Incorporar al estado de la aplicación
            if caldf not in st.session_state:
                st.session_state.caldf = caldf
            if cddf not in st.session_state:
                st.session_state.cddf = cddf
            if fps not in st.session_state:
                st.session_state.fps = fps
            
            # Determinación de la dosis en cada canal
            Dim = fqa.mphspcnlmprocf_multiprocessing(imfile=imfile, config=config, caldf=caldf, ccdf=cdf)

            st.session_state.fDim = fqa.postmphspcnlmprocf(Dim, config=config)
            if 'fDim' in st.session_state:
                fcols, frows, fchannels = Dim.shape
                st.session_state.fcols = fcols
                st.session_state.frows = frows
                st.success('Convertida a dosis la información de la película.')
    
    if rects:
        with st.sidebar:
            st.caption('Imagen digitalizada:')
            st.button(label="Procesar", on_click=process)

        preview_imgs = im.init_annotation(rects)

        for i, prev_img in enumerate(preview_imgs):
            prev_img[0].thumbnail((200, 200))
            col1, col2 = st.columns(2)
            with col1:
                col1.image(prev_img[0])
            with col2:
                default_index = 0
                if prev_img[1]:
                    default_index = labels.index(prev_img[1])

                select_label = col2.selectbox(
                    "Label", labels, key=f"label_{i}", index=default_index
                )
                im.set_annotation(i, select_label)

if __name__ == "__main__":
    st.header('2. Procesar el plano de dosis medido mediante la película')

    scim = st.file_uploader('Digitalización de la película:', help='Seleccionar el archivo TIFF adquirido en el escáner.')

    if scim is not None:
        st.session_state.scim = scim
        # Guardar una copia local de la imagen
        lcscim = os.path.join("img_dir",scim.name)
        with open(lcscim,"wb") as f:
            f.write(scim.getbuffer())
        # Crear un registro en el estado de la alicación con el nombre del archivo de imagen
        if 'FilmFileName' not in st.session_state:
            st.session_state.FilmFileName = scim.name

        # Guardar una copia local en formato png
        aim = imread(lcscim)
        imsave(os.path.join("img_dir",'Film.png'), img_as_ubyte(rescale_intensity(aim, out_range='uint8')))

        # Etiquetar la imagen
        custom_labels = ["", "Film", "Calibration", "Background", "Center"]

        run('img_dir/Film.png', custom_labels)
