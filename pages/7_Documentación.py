from PIL import Image
import streamlit as st
st.set_page_config(page_title='FilmQAp', layout="wide")

coll, colc, colr = st.columns([1, 3, 1])
with colc:
    st.title('Documentación')

    st.markdown(
    '''
    `FilmQAp` es una aplicación para procesar películas radiocrómicas mediante un esquema de digitalización única (*SSP, single scan protocol*) utilizando un algoritmo multicanal de promedios no locales. La calibración del algoritmo emplea un modelo de crecimiento con la dosis de dos tipos de absorbentes particularizado a las condiciones presentes durante la digitalización. El algoritmo corrige el efecto lateral del escáner.

    La información dosimétrica se genera en `dxf` (formato de archivos de intercambio de información de Varian). Estos archivos se pueden importar en la aplicación **Portal Dosimetry** para su posterior análisis y registro.

    Esta documentación describe el procedimiento para completar un control de calidad paciente específico mediante *dosimetría fotográfica* y `FilmQAp`.
    '''
    )

    st.header('Procedimiento')

    st.subheader(' Cálculo del plano de dosis en el planificador')

    st.markdown(
    '''
    En Eclipse desde el plan que se quiere medir, seleccionar Create Verification Plan y seguir el procedimiento del planificador.

    La selección de planos de dosis en Eclipse requiere que el plano contenga el isocentro de un campo como referencia. Si se quiere seleccionar un plano que no contenga el isocentro del plan de tratamiento es necesario añadir un campo con peso 0 con su isocentro situado sobre el plano de interés y centrado en el plano de dosis.
    '''
    )

    img = Image.open('Images/PlaneSelection.jpg')
    st.image(img, caption='Selección de planes en Eclipse')

    st.markdown(
    '''
    En la imagen anterior a un plan HyperArc se le han añadido dos campos para exportar planos sagitales desplazados 1 cm respecto al centro del maniquí. Los campos se han centrado en x = 0 , y = +1, z = 0, y en  x = 0 , y = -1, z = 0

    Calcular la distribución de dosis y seleccionar la ventana que contenga el plano que se quiere exportar. Registrar si se trata de un plano axial, sagital o coronal. En la imagen anterior puede verse que la ventana iluminada es la que corresponde a los planos sagitales.

    Con el botón derecho sobre el icono Dose ir a la opción Export Dose Plan.

    '''
    )
    img = Image.open('Images/ExportDosePlane.jpg')
    st.image(img, caption='Exportación de dosis en Eclipse')

    st.markdown(
    '''
    Seleccionar dosis absoluta y el campo que tiene su isocentro situado sobre el plano que se exporta. No activar la opción del marcado de la película. Indicar las dimensiones del plano que se exporta, normalmente 16 cm por 16 cm. Una resolución espacial razonable es 1 pixel por milímetro.
    '''
    )
    img = Image.open('Images/ExportDosePlaneOptions.jpg')
    st.image(img, caption='Selección de las opciones de exportación')

    st.markdown(
    '''
    En la ventana de configuración de la exportación se puede seleccionar la carpeta en la que se exporta el plano de dosis, que debería ser la carpeta del paciente en Radiofisica\Medidas Pacientes\IMRT
    '''
    )
    img = Image.open('Images/ExportDosePlaneConfigureOptions.jpg')
    st.image(img, caption='Configuración de las opciones de exportación en Eclipse')

    st.subheader('Preparación de la película para la medida')
    st.markdown(
    '''
    El tamaño de las películas con las que se mide está limitado por el tamaño del maniquí sobre el que se ha calculado el plan de verificación. Sí es posible irradiar películas de un tamaño inferior si se desea.

    Cortar la película con las dimensiones del plan calculado, normalmente un cuadrado de 16 cm por 16 cm.
    '''
    )

    img = Image.open('Images/cortetransversal.jpg').rotate(270)
    #img = Image.rotate(img, rot=270)
    st.image(img)

    img = Image.open('Images/recortemedida.jpg')
    st.image(img, caption='Corte de las películas')

    st.markdown(
    '''
    Antes de cortar la película marcar las esquinas superiores de las áreas a cortar y restantes con un guión que sea paralelo a la dimensión estrecha de la película original. Ver la siguiente ilustración
    '''
    )

    img = Image.open('Images/marcasrecortes.png')
    st.image(img, caption='Corte de las películas')

    st.subheader('Preparación de la película de calibración')

    st.markdown(
    '''
    El tamaño de la tira de calibración tiene que ser de unos centímetros de ancho por 16 cm de largo, con su dimensión longitudinal en la dirección *portrait*.

    La forma óptima de prepararla es ir cortando tiras a partir de un recorte sin irradiar de una película de medida. No olvidar marcar la orientación de los recortes.
    '''
    )

    st.header('Irradiación')

    st.subheader('Control de calidad del plan de un paciente')

    st.markdown(
    '''
    Colocar la película en el interior del maniquí de calidad en la localización del plano cálculado. La orientación de la película en este momento no es relevante.

    Situar el maniquí en el acelerador, alinear, cargar el plan e irradiar.
    '''
    )

    st.subheader('Calibración')

    st.markdown(
    '''
    Colocar la tira de calibración en el plano central del maniquí con su dimensión longitudinal según el eje vertical del acelerador. Tapar el maniquí.

    En un acelerador Artiste alinear el maniquí con los láseres y subir la mesa hasta una distancia fuente superficie de 75 cm. Con energía 6X programar un campo de 10x10, Gantry 0º y Colimador 0º. Irradiar 346.5 unidades monitor.
    '''
    )

    st.header('Digitalización')

    st.markdown(
    '''
    Colocar las muestras de película en la bandeja del escáner de acuerdo a la siguiente distribución
    '''
    )


    img = Image.open('Images/disposicionEscaner.jpg').rotate(270)
    st.image(img, caption='Disposición de muestras en el escáner')

    st.markdown(
    '''
    Para poder introducir la corrección por efecto lateral es necesario contar con una referencia de la posición de las películas en el escáner. En este imagen se obtiene mediante la regla móvil inferior.

    Las condiciones de digitalización son en modo transmisión en color 48 bits con una resolución de 72 puntos por pulgada.

    Realizar un prescan y fijar una ROI que incluya completamente todas las películas y al menos la marca de centraje de la regla inferior.
    '''
    )

    st.header('Procesado')

    st.subheader('Planificador')

    st.markdown(
    '''
    Convertir el plano de dosis calculado en el planificador de formato `DICOM` a `dxf`. Seleccionar en la barra lateral la página **Plano dosis planificador**.
    '''
    )

    img = Image.open('Images/menuPlanoDosisPlanificador.jpg')
    st.image(img, caption='Selección de opción en la barra lateral')

    st.markdown(
    '''
    Pulsar el botón **Browse Files**. Ir a la carpeta en la que se haya exportado el plano de dosis en formato `DICOM` y seleccionarlo. Alternativamente arrastrar el archivo al área de subida.
    '''
    )

    img = Image.open('Images/areaUploadPlanoDosisPlanificador.jpg')
    st.image(img, caption='Área de subida.')

    st.markdown(
    '''
    La aplicación muestra una tabla con datos de identificación del paciente y representa el plano de dosis. En ausencia de errores un mensaje de éxtio indica que se ha creado en la misma carpera del paciente el archivo de dosis en formato `dxf`. Por defecto la aplicación utiliza la información DICOM para identificar el número de historia del paciente y su correspondiente carpeta.
    '''
    )

    img = Image.open('Images/salidaPlanoDosisPlanificador.jpg')
    st.image(img, caption='Página "Plano dosis planificador" tras procesar la información exportada')

    st.subheader('Película')

    st.markdown(
    '''
    Seleccionar en la barra lateral la opción **Plano dosis película**.
    '''
    )

    img = Image.open('Images/menuPlanoDosisFilm.jpg')
    st.image(img, caption='Opción "Plano dosis película"')

    st.markdown(
    '''
    Pulsar el botón **Browse Files**. Ir a la carpeta que contenga la imagen digitalizada de las muestras de película y seleccionarlo. Alternativamente arrastrar el archivo al área de subida.
    '''
    )

    img = Image.open('Images/areaUploadImagenFilm.jpg')
    st.image(img, caption='Área de subida.')

    st.markdown(
    '''
    Al subir la imagen digitalizada la aplicación habilita herramientas para identificar las zonas relavantes de la imagen:

    * **Film**: Región que contiene la distribución de dosis que se quiere medir

    * **Calibración**: Región con la distribución utilizada para particularizar la calibración, normalmente un PDD

    * **Fondo**: Región con un trozo de película sin irradiar

    * **Centro**: Un área cuyo centro geométrico esté contenido en el eje de digitalización del escáner, entendido como la línea que define el centro de la lámpara al avanzar durante la digitalización. La identificación de este eje es relevante para poder aplicar la correción por efecto lateral.

    `FilmQAp` muestra cuatro regiones predefinidas que corresponden a las cuatro zonas anteriores. Los bordes y las posiciones de las regiones son ajustables. La aplicación mantiene las dimensiones y posiciones del último análisis realizado.
    '''
    )

    img = Image.open('Images/etiquetadoImagen.jpg')
    st.image(img, caption='Segmentación de la imagen')

    st.markdown(
    '''
    Cada región se muestra de forma independiente en la parte inferior de la ventana junto con su etiqueta.
    '''
    )

    img = Image.open('Images/imagenesRecortadas.jpg')
    st.image(img, caption='Imágenes recortadas con sus etiquetas')

    st.markdown(
    '''
    Cuando se han identificado correctamente las regiones relevantes pulsar el botón **Process** en la barra lateral.
    '''
    )

    img = Image.open('Images/processButton.jpg')
    st.image(img, caption='Botón para procesar la película', width=350)

    st.markdown(
    '''
    Una barra de progreso indica el avance del procesado de la imagen y al final del mismo, si no se han producido errores, un mensaje indica que el proceso ha terminado con éxito.
    '''
    )

    img = Image.open('Images/barraProgreso.jpg')
    st.image(img, caption='Barra de progreso', width=350)

    img = Image.open('Images/mensajeExito.jpg')
    st.image(img, caption='Mensaje de éxito al final del procesado de la película')

    st.markdown(
    '''
    Seleccionar en la barra lateral la opción **Reorientar y exportar la dosis**
    '''
    )

    img = Image.open('Images/menuReorientarExportarDosis.jpg')
    st.image(img, caption='Opción "Reorientar exportar dosis"')
