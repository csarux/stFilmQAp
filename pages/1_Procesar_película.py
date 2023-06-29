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
st.set_page_config(page_title='chromLit')


def run(img_dir, labels):
    st.set_option("deprecation.showfileUploaderEncoding", False)
    idm = ImageDirManager(img_dir)

    if "files" not in st.session_state:
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"])
        idm.set_annotation_files(st.session_state["annotation_files"])

    def refresh():
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
#        else:
#            st.warning('This is the last image.')

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
#        else:
#            st.warning('This is the first image.')

    def next_annotate_file():
        image_index = st.session_state["image_index"]
        next_image_index = idm.get_next_annotation_image(image_index)
        if next_image_index:
            st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
        else:
#            st.warning("All images are annotated.")
            next_image()

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index

    # Sidebar: show status
    n_files = len(st.session_state["files"])
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Total annotate files:", n_annotate_files)
    st.sidebar.write("Remaining files:", n_files - n_annotate_files)

    st.sidebar.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["image_index"],
        on_change=go_to_image,
        key="file",
    )
#    col1, col2 = st.sidebar.columns(2)
#    with col1:
#        st.button(label="Previous image", on_click=previous_image)
#    with col2:
#        st.button(label="Next image", on_click=next_image)
#    st.sidebar.button(label="Next need annotate", on_click=next_annotate_file)
#    st.sidebar.button(label="Refresh", on_click=refresh)

    # Main content: annotate images
    img_file_name = idm.get_image(st.session_state["image_index"])
    img_path = os.path.join(img_dir, img_file_name)
    im = ImageManager(img_path)
    img = im.get_img()
    resized_img = im.resizing_img()
    resized_rects = im.get_resized_rects()
    rects = st_img_label(resized_img, box_color="red", rects=resized_rects)

    def nlm_process():
        imfile = 'img_dir/' + scim.name
        im.save_annotation()
        image_annotate_file_name = img_file_name.split(".")[0] + ".xml"
        if image_annotate_file_name not in st.session_state["annotation_files"]:
            st.session_state["annotation_files"].append(image_annotate_file_name)
        next_annotate_file()

        lbdf = pd.DataFrame(im._current_rects)
        lbdf.to_csv('tmp/bb.csv')

        # Segmentar la imagen
        fqa.segRegs(imfile=imfile)

        # Leer la configuración
        config = configparser.ConfigParser()
        configfile='config/filmQAp.config'
        config.read(configfile)

        # Leer el valor de la dosis máxima fijado en la configuración
        if 'Dmax' not in st.session_state:
            st.session_state.Dmax = fqa.getDmax(config=config)
        
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
        if 'Dmax' in st.session_state:
            st.session_state.fDim = fqa.postmphspcnlmprocf(Dim, config=config)
            if 'fDim' in st.session_state:
                fcols, frows, fchannels = Dim.shape
                st.session_state.fcols = fcols
                st.session_state.frows = frows
                st.success('Convertida a dosis la información de la película.')
        else:
            st.error('Error: No se ha configurado el valor de la dosis máxima medible.')

    def mayer_process():
        config = fqa.readConfig(os.path.join('config', 'filmQAp.config'))

        img_file_name = os.path.join('img_dir', 'Film.tif')

        abase = fqa.baseDetermination(imfile=img_file_name, config=config)

        caldf, cdf, sips = fqa.PDDCalibration(imfile=img_file_name, config=config, base=abase)
        ratcaldf = fqa.ratcalf(caldf)

        # Incorporar al estado de la aplicación
        if caldf not in st.session_state:
            st.session_state.caldf = caldf
        if cddf not in st.session_state:
            st.session_state.cddf = cddf
        if fps not in st.session_state:
            st.session_state.fps = fps

        # Calcular la dosis
        st.session_state.fDim = fqa.mayermltchprocf(imfile=img_file_name, config=config, ratcaldf=ratcaldf)
        
        return

    def red_process():
        config = fqa.readConfig(os.path.join('config', 'filmQAp.config'))

        img_file_name = os.path.join('img_dir', 'Film.tif')

        abase = fqa.baseDetermination(imfile=img_file_name, config=config)

        caldf, cdf, sips = fqa.PDDCalibration(imfile=img_file_name, config=config, base=abase)
        ratcaldf = fqa.ratcalf(caldf)

         # Incorporar al estado de la aplicación
        if caldf not in st.session_state:
            st.session_state.caldf = caldf
        if cddf not in st.session_state:
            st.session_state.cddf = cddf
        if fps not in st.session_state:
            st.session_state.fps = fps

        # Calcular la dosis
        st.session_state.fDim = fqa.redprocf(imfile=img_file_name, config=config, ratcaldf=ratcaldf)

        return 

    def green_process():
        config = fqa.readConfig(os.path.join('config', 'filmQAp.config'))

        img_file_name = os.path.join('img_dir', 'Film.tif')

        abase = fqa.baseDetermination(imfile=img_file_name, config=config)

        caldf, cdf, sips = fqa.PDDCalibration(imfile=img_file_name, config=config, base=abase)
        ratcaldf = fqa.ratcalf(caldf)

        # Incorporar al estado de la aplicación
        if caldf not in st.session_state:
            st.session_state.caldf = caldf
        if cddf not in st.session_state:
            st.session_state.cddf = cddf
        if fps not in st.session_state:
            st.session_state.fps = fps

        # Calcular la dosis
        st.session_state.fDim = fqa.greenprocf(imfile=img_file_name, config=config, ratcaldf=ratcaldf)

        return

    def blue_process():
        config = fqa.readConfig(os.path.join('config', 'filmQAp.config'))

        img_file_name = os.path.join('img_dir', 'Film.tif')

        abase = fqa.baseDetermination(imfile=img_file_name, config=config)

        caldf, cdf, sips = fqa.PDDCalibration(imfile=img_file_name, config=config, base=abase)
        ratcaldf = fqa.ratcalf(caldf)

        # Incorporar al estado de la aplicación
        if caldf not in st.session_state:
            st.session_state.caldf = caldf
        if cddf not in st.session_state:
            st.session_state.cddf = cddf
        if fps not in st.session_state:
            st.session_state.fps = fps

        # Calcular la dosis
        st.session_state.fDim = fqa.blueprocf(imfile=img_file_name, config=config, ratcaldf=ratcaldf)
        return 
        
    if rects:
        with st.sidebar:
            st.button(label="NLM Process", on_click=nlm_process)
            st.button(label="Multichannel Process", on_click=mayer_process)
            st.button(label="Red Channel Process", on_click=red_process)
            st.button(label="Green Channel Process", on_click=green_process)
            st.button(label="Blue Channel Process", on_click=blue_process)


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
    st.header('1. Procesar el plano de dosis medido mediante la película')

    scim = st.file_uploader('Digitalización de la película:', help='Seleccionar el archivo TIFF adquirido en el escáner.')

    if scim is not None:
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

        run("img_dir", custom_labels)
