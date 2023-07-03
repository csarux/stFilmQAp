from PIL import Image
import streamlit as st
st.set_page_config(page_title='FilmQAp', layout="wide")

coll, colc, colr = st.columns([1, 3, 1])
with colc:
    st.title('Documentación')

    st.markdown(
    '''
    `chromLit` es una aplicación para procesar películas radiocrómicas mediante un esquema de digitalización única (*SSP, single scan protocol*) utilizando un algoritmo multicanal de promedios no locales. La calibración del algoritmo emplea un modelo de crecimiento con la dosis de dos tipos de absorbentes particularizado a las condiciones presentes durante la digitalización. El algoritmo corrige el efecto lateral del escáner.

    En este [video](https://youtu.be/Oq-mgwh8iR8) se muestra el flujo de trabajo en `chromLit`.

    `chromLit` genera la información de la dosis medida en archivos `dxf` (formato de intercambio de información de Varian). Estos archivos se pueden importar en la aplicación **Portal Dosimetry** para su posterior análisis y registro. `dxf` es una archivo de texo de tipo `csv` que puede ser importado y analizado por otros medios. Alternativamente `chromLit` también puede exportar la información procesada como un plano de dosis en formato `DICOM`.

    Esta documentación describe el procedimiento para completar una medida de una distribución espacial de dosis empleando películas radiocrómicas procesadas mediante `chromLit`.

    '''
    )

    st.header('Esquema de digitalización única')

    st.markdown(
    '''
    Para calibrar el sistema en la misma digitalización en la que se realiza la medida es necesario leer junto con la película problema otras muestras adicionales. `chromLit` espera que se introduzca una muestra de película sin irradiar para establecer el fondo y una película irradiada de forma controlada con valores conocidos de dosis para establecer los parámetros lineales del modelo sensitométrico. Estos parámetros particularizan la respuesta del sistema en el momento de la lectura.

    Para reducir la incertidumbre en la determinación de estos parámetros es recomendable emplear una película que registre las variaciones de dosis en un haz de radiación bajo condiciones conocidas, un rendimiento en profundidad de un haz de fotones por ejemplo. Esta documentación se basa en esta recomendación pero otras distribuciones de dosis son posibles. Estrictamente `chromLit` solo requiere conocer los valores de dosis con los que se ha irradiado la película de calibración independientemente de cómo se haya generado. La forma de describir las dosis de calibración es mediante una tabla en un archivo Excel con coordenadas espaciales, posiciones en la película, y sus valores de dosis correspondientes.
    '''
    )
   

    st.markdown(
    '''
    '''
    )

    st.header('Procedimiento')

    st.subheader('Preparación de la película para la medida')
    st.markdown(
    '''
    El tamaño de las películas con las que se mide está limitado por el tamaño del maniquí que las va a contener. Sí es posible irradiar películas de un tamaño inferior si se desea.

    Cortar la película con las dimensiones deseadas. Por ejemplo, para el maniquí I'mRT normalmente un cuadrado de 16 cm por 16 cm.
    '''
    )

    img = Image.open('Images/cortetransversal.jpg').rotate(270)
    #img = Image.rotate(img, rot=270)
    st.image(img)

    img = Image.open('Images/recortemedida.jpg')
    st.image(img, caption='Corte de las películas')

    st.markdown(
    '''
    Al leer la película su respuesta es diferente dependiendo de la orientación respecto al escáner. Para que el procedimiento funcione correctamente es necesario mantener un mismo criterio de orientación para la calibración y la medida. Para ayudar a mantener la orientación durante el procedimiento una posibilidad es, antes de cortar la película, marcar las esquinas superiores derechas de todas las áreas resultantes con un guión que sea paralelo a la dimensión estrecha de la película original. Ver la siguiente ilustración. 
    '''
    )

    img = Image.open('Images/marcasrecortes.png')
    st.image(img, caption='Corte de las películas')


    st.markdown(
    '''
    Es arbitrario la orientación que se elija. Nuestro criterio es emplear la orientación *portrait* o retrato.
    '''
    )

    st.subheader('Preparación de la película de calibración')

    st.markdown(
    '''
    El tamaño de la película de calibración dependerá de la distribución de dosis de referencia que se elija. Si se sigue nuestra recomendación y se emplea un procedimiento basado en rendimientos en profundidad puede ser una tira de unos centímetros de ancho por 16 cm de largo (tamaño del maniquí), con su dimensión longitudinal en la dirección *portrait*.

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

    Irradiar en la unidad de tratamiento de acuerdo al plan de calibración calculado. A modo de ejemplo las condiciones de calibración empleadas en nuestro procedimiento son distancia fuente superficie de 75 cm, energía 6X, campo de 10x10, Gantry 0º, Colimador 0º, 346.5 unidades monitor.
    '''
    )

    st.header('Digitalización')

    st.markdown(
    '''
    Colocar las muestras de película en la bandeja del escáner: película a medir, película de fondo, película de calibración y el indicador de la posición. En este momento es importante emplear las señales de orientación para respetar el criterio elegido. Si se ha seguido la recomendación dada todas las señales de orientación deben ser paralelas a la dirección longitudinal de la lámpara del escáner. 
    '''
    )


    img = Image.open('Images/disposicionEscaner.jpg').rotate(270)
    st.image(img, caption='Disposición de muestras en el escáner')

    st.markdown(
    '''
    Para poder introducir la corrección por efecto lateral es necesario contar con una referencia de la posición de las películas en el escáner. En este imagen se obtiene mediante la regla móvil inferior.

    Las condiciones de digitalización son en modo transmisión en color 48 bits. Una resolución de 72 puntos por pulgada es suficiente aunque este parámetro es configurable en `chromLit`.

    Realizar un prescan y fijar una ROI que incluya completamente al menos todas las películas y la marca de centraje de la regla inferior.

    '''
    )

    st.header('Procesado')

    st.subheader('Película')

    st.markdown(
    '''
    Seleccionar en la barra lateral la opción **Procesar película**.
    '''
    )

    img = Image.open('Images/menuProcesarPelicula.png')
    st.image(img, caption='Menú de la barra lateral, opción "Procesar película"')

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

    `chromLit` muestra cuatro regiones predefinidas que corresponden a las cuatro zonas anteriores. Los bordes y las posiciones de las regiones son ajustables. La aplicación mantiene las dimensiones y posiciones del último análisis realizado.
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
    Cuando se han identificado correctamente las regiones relevantes elegir una opción de procesado en la barra lateral.

    - **NLM Process**: procesado mediante *promedios no locales* y la opción *recomendada* por `chromLit`
    - **Multichannel Process**: Implementación de Mayer del procedimiento muticanal propuesto por Micke. *Experimental, probablemente necesite una revisión del código*
    - **Red Channel Process**: procesado monocanal a partir de la señal roja.
    - **Green Channel Process**: procesado monocanal a partir de la señal verde.
    - **Blue Channel Process**: procesado monocanal a partir de la señal azul.
    '''
    )

    img = Image.open('Images/botonesOpcionesProcesado.png')
    st.image(img, caption='Diferentes opciones para procesar la película')

    st.markdown(
    '''
    Una barra de progreso indica el avance del procesado de la imagen
    '''
    )

    img = Image.open('Images/barraProgreso.jpg')
    st.image(img, caption='Barra de progreso', width=350)

    st.markdown(
    '''
    Al final del proceso, si no se han producido errores, un mensaje indica que ha terminado con éxito.
    '''
    )
    img = Image.open('Images/mensajeExitoDosisPelicula.png')
    st.image(img, caption='Mensaje de éxito mostrado al final del procesado de la película. El mensaje aparece en la parte superior de la pantalla principal.')

    st.header('Orientación y exportación de la distribución de dosis medida')

    st.markdown(
    '''
    Tras completar con éxito el procesado de la película, seleccionar en la barra lateral la opción **Reorientar y exportar dosis**
    '''
    )

    img = Image.open('Images/menuReorientarExportarDosis.png')
    st.image(img, caption='Opción "Reorientar exportar dosis"')

    st.markdown(
    '''
    `chromLit` muestra en su ventana principal las ocho orientaciones posibles de la distribución de dosis medida. Pinchar sobre la que corresponda a la orientación calculada. La opción seleccionada aparace enmarcada en rojo.
    '''
    )

    img = Image.open('Images/opcionesOrientacion.png')
    st.image(img, caption='Selección de la orientación espacial de la distribución de dosis')

    st.markdown(
    '''
    En la barra lateral `chromLit` ofrece dos botones para exporar en formato `dxf`, formato de texto para intercambio de datos de Varian, o `dcm`para exportar como un plano de dosis en formato DICOM.
   '''
    )

    img = Image.open('Images/botonesExportacion.png')
    st.image(img, caption='Selección del formato de exportación')

    st.markdown(
    '''
    `chromLit` escribe por defecto estos ficheros en la carpeta de Descargas fijada por el navegador con el que trabajemos. 
    '''
    )

    st.subheader('Calibración')

    st.markdown(
    '''
    Para obtener información sobre la calibración empleada en el procesado seleccionar la opción **Calibración** en la barra lateral.
    '''
    )

    img = Image.open('Images/menuCalibracion.png')
    st.image(img, caption='Opción Calibración.', width=315)

    st.markdown(
    '''
    FilmQAp muestra varios gráficos y tablas con la información sobre los ajustes de calibración, sus parámetros y estimaciones de incertidumbre.
    '''
    )

    img = Image.open('Images/pantallaCalibracion.png')
    st.image(img, caption='Vista de la información sobre la calibración.', width=750)

    st.markdown(
    '''
    El primero de los gráficos muestra para los tres canales de color las curvas de la densidad óptica determinada a partir de la señal digital del escáner en función de la dosis absorbida.
    La línea formada por guiones y puntos son los valores medidos, la línea continua la forman las densidades ópticas esperadas a partir del modelo ajustado de calibración para las dosis empleadas y la línea de guiones la constituyen los valores de densidades ópticas calculadas por el modelo cuando se introducen las dosis determinadas por el procesado de la película de calibración.
    '''
    )

    img = Image.open('Images/curvasCalibracion.jpg')
    st.image(img, caption='Densidad óptica en función de la dosis para los tres canales.', width=500)

    st.markdown(
    '''
    El segundo de los gráficos muestra la curva del error relativo entre la dosis esperada de calibración y la realmente medida con el modelo en función de la dosis.
    '''
    )

    img = Image.open('Images/curvaErrorRelvsDosis.jpg')
    st.image(img, caption='Error relativo en función de la dosis.', width=500)

    st.markdown(
    '''
    La tercera gráfica es el histograma del error relativo para todas la dosis absorbidas empleadas en la calibración.
    '''
    )

    img = Image.open('Images/HistogramaErrorRel.jpg')
    st.image(img, caption='Histograma del error relativo de la dosis.', width=500)

    st.markdown(
    '''
    La cuarta gráfica muestra la comparación entre la dosis de irradiación y la determinada por la tira de calibración en función de la posición espacial.
    '''
    )

    img = Image.open('Images/curvaDosisMedidavsCalibracion.jpg')
    st.image(img, caption='Dosis medida frente a dosis de calibración.', width=500)

    st.markdown(
    '''
    Tabla con los valores de calibración en función de la profundidad, los valores ajustados por el modelo y sus incertidumbres.
    '''
    )

    img = Image.open('Images/valoresCalibracion.jpg')
    st.image(img, caption='Tabla navegable con los valores de calibración.', width=500)

    st.markdown(
    '''
    Tabla con los parámetros de calibración para los tres canales.
    '''
    )

    img = Image.open('Images/parametrosCalibracion.png')
    st.image(img, caption='Tabla con los parámetros de calibración.')

    st.header('Configuración')

    st.markdown(
    '''
    La página de configuración muestra y permite cambiar los valores de configuración utilizados por la aplicación `chromLit`

    `chromLit` emplea el módulo `configparser`. El archivo de configuración sigue una estructura similar a la de los archivos `INI` en Windows.

    La aplicación es por tanto configurable también modificando el archivo `filmQAp.config` y es posible extender fácilmente la configuración con nuevos parámetros.

    Las siguientes tablas explican los parámetros de configuración. Se indican como *informativo* los parámetros que no es esperable que se modifiquen o que realmente solo tienen un valor informativo.

    '''
    )
    st.subheader('Sección DEFAULT')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | module      | Nombre del módulo con las funcionalidades para realizar el procesado de las películas. Valor por defecto: `pyfilmqa`. *Informativo*     |
    | language    | Lenguaje de programación en el que está escrito el módulo. Valor por defecto: `python`. *Informativo*      |
    | version     | Versión del lenguaje de programación. Valor por defecto: **3.x**. *Informativo*| 
    | configpath  | Ruta relativa del archivo de cofiguración. Valor por defecto: **./config**      |
    | exportpath  | Ruta de exportación. Valor por defecto: **./**      |
    '''
    )

    st.subheader('Sección Scanner')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | brand       | Marca del fabricante del escáner. *Informativo*     |
    | model       | Modelo del escáner. *Informativo*      |
    | format      | Formato de archivo digital de la imagen digitalizada. Formato requerido: **TIFF**. *Informativo*| 
    | mode        | Modo de lectura del escáner. Valor por defecto: **transmission**      |
    | dpi         | Frecuencia espacial de la digitalización en puntos por pulgada. Valor recomendado: **72**      |
    | coding      | Codificación de la digitalizacion. Modo requerido **RGB**. *Informativo*     |
    | bitdepth    | Profundidad de bits de la digitalización. Valor requerido: **16**. *Informativo*      |
    '''
    )

    st.subheader('Sección DosePlane (no utilizada por chromLit)')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | dmax        | Dosis máxima esperable en la distribución calculada. Utilizado para acotar las dosis medidas.  |
    | pixelsize   | Tamaño de pixel de la disitrbución de dosis calculada       |
    | pixelunit   | Unidades del tamaño de pixel. Valor por defecto: **mm**.| 
    | pixelnumber | Número de pixeles en la distribución calculada. Valor por defecto **160x160**      |
    | sizeunit    | Unidades para especificar el tamaño del plano calculado. Valor por defecto: **mm**      |
    | width       | Anchura en número de píxeles del plano calculado     |
    | height      | Altura en número de píxeles del plano calculado     |
    '''
    )

    st.subheader('Sección FilmPlane')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | filmname    | Nombre del archivo con la imagen digitalizada. *Informativo*  |
    '''
    )

    st.subheader('Sección Segmentation')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | file     | Archivo en el que se almacenan las coordendas de las regiones segmentadas en la imagen digitalizada  |
    '''
    )

    st.subheader('Sección Base')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | margin     | Número de píxeles descartados en la imagen de fondo para evitar efecto de borde debidos al corte  |
    | marginunit | Unidad para especificar el margen. Valor por defecto: **pixel**. *Informativo*  |
    '''
    )

    st.subheader('Models')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | file        | Nombre del archivo Excel con las tablas de parámetros de calibración. Valor por defecto: **RacMPhCalibs.xlsx**. *Informativo*  |
    | mphsheet    | Nombre de la hoja en la que se almacenan los valores por defecto del modelo de dos fases. Valor por defecto: **MultiFase**. *Informativo*      |
    | racsheet    | nombre de la hoja en la que se almacenan los valores por defecto del modelo racional. Valor por defecto: *Racionales**. *Informativo*| 
    | oadcfile    | Archivo con funciones `numpy` para la corrección del efecto lateral. Describen la variación con la posición de los coeficientes lineales del modelo de dos fases. Es específico del modelo y marca de escáner empleado. Valor por defecto: **Microtek1000XLOADc.npy**.     |
    '''
    )

    st.subheader('Calibration')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | mode     | Modo de calibración. Valor por defecto: **PDD**. *Informativo*  |
    | dmax     | Dosis máxima en la distribución de calibración.       |
    | energy   | Energía del haz de calibración. Valor por defecto: **6**. *Informativo*| 
    | eunit    | Unidad en la que se da la energía del haz de calibración. Valor por defecto: **MV**. *Informativo*     |
    | unit     | Unidad de longitud en la que dan las dimensiones y localización del haz de calibración. Valor por defecto: **cm**. *Informativo*  |
    | fieldwidth     | Anchura del haz de calibración. Valor por defecto: **10**      |
    | fieldheigth    | Alto del haz de calibración. Valor por defecto: **10**      |
    | um       | Unidades monitor de la irradiación de calibración. *Informativo*| 
    | dfs      | Distancia fuente superficie fijada para el montaje de calibración. Valor por defecto: **75**. *Informativo*     |
    | path     | Ruta relativa a la localización del archivo de calibración. Valor por defecto: **./config/**. *Informativo*  |
    | file     | Nombre del archivo Excel de calibración. Valor por defecto: **PDDCalib.xlsx**. *Informativo*       |
    | sheet    | Hoja en la que se encuentran los datos de calibracicón. Valor por defecto: **Hoja1**. *Informativo*| 
    | shift    | Desplazamiento hasta el comienzo de los datos. Valor por defecto: **1**. *Informativo*     |
    | depthmin | Profundidad mínima considerada en la calibración. Tiene en cuenta el espesor de plástico que rodea a la película en el maniquí de medida más un margen para evitar efectos de borde. Valor por defecto: **2**. *Informativo*   |
    | depthmin | Profundidad máxima considerada en la calibración. Tiene en cuenta el espesor de plástico que rodea a la película en el maniquí de medida más un margen para evitar efectos de borde. Valor por defecto: **2**. *Informativo*   | '''
    )

    st.subheader('NonLocalMeans')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | patchsize     | Tamaño en píxeles de la región considerada para reducir ruido. Valor por defecto: **3**. *Informativo*  |
    | patchdistance | Distancia máxima en píxeles donde buscar regiones para reducir ruido. Valor por defecto: **10**. *Informativo* |
    | h             | Parámetro de filtrado. Cuanto más alto más regiones se consideran. Valor por defecto: **0.05**. *Informativo*| 
    | multichannel  | Variable booleana que indica si el algoritmo considera o no simultaneamente la información de los tres canales de color. Valor por defecto: **True**. *Informativo*     |
    | channelaxis   | Índice del canal de color. Valor por defecto: **2**. *Informativo*  |
    | wred          | Peso de la dosis correspondiente al canal rojo en el promedio de la dosis. Valor por defecto: **10**. *Informativo*     |
    | wgreen        | Peso de la dosis correspondiente al canal verde en el promedio de la dosis. Valor por defecto: **5**. *Informativo*     |
    | wblue         | Peso de la dosis correspondiente al canal azul en el promedio de la dosis. Valor por defecto: **1**. *Informativo*      |
    '''
    )

    st.subheader('Demographics')
    
    st.markdown(
    '''     
    | **Parámetro** | **Significado** |
    |----------|---------|
    | patientid     | Identificación del paciente, normalmente el número de historia. Valor por defecto: **Demo001**. *Informativo*  |
    | patientname   | Nombre de pila del paciente. Valor por defecto: **Test**. *Informativo* |
    | patientfamilyname | Apellido del paciente. Valor por defecto: **chromLit**. *Informativo*| 
    | gender        | Sexo del paciente. Valor por defecto: **M**. *Informativo*     |
    '''
    )


