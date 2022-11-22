from PIL import Image
import streamlit as st
st.set_page_config(page_title='FilmQAp', layout="wide")

coll, colc, colr = st.columns([1, 7, 1])
with colc:
    st.title('Documentación para realizar el análisis')

    st.header('Elementos')

    st.markdown(
    '''
    Tenemos dos distribuciones de dosis: planificador y película.

    Ambas distribuciones pueden tener diferente resolución espacial y localización en el espacio. Necesitamos representarlas y compararlas, por lo que será necesario remuestrearlas e indicar su posición en el espacio de manera flexible.

    Para representarlas lo más sencillo es hacerlo con un remuestreo a la resolución más baja, que será siempre la del planificador. Se tiene que imponer como condición pero es fácil de cumplir. Con una resolución de 72 dpi tenemos un tamaño de pixel de 0.353 mm y configuramos Eclipse para exportar tamaños de pixel de 1 mm. El problema solo aparecería para resoluciones de digitalizaciones inferiores a 26 dpi que no se utilizan en la práctica y se podría arreglar exportando del planificador con otra resolución menor.

    La comparación se puede hacer de dos maneras, mediante diferencias de dosis y mediante índice gamma. La funcionalidad del índice gamma no requiere que las imágenes tengan la misma resolución, pero para la diferencia necesitamos poder tener un remuestreo de una de las distribuiones para hacerla coincidir con la de la otra.

    La representación de las imágenes se va a realizar mediante seaborn (heatmap) para las distribuciones espaciales de dosis, mezclado con matplotlib para indicar la posición de los perfiles. En Seaborn es fácil pasar los datos en forma de pandas DataFrames. Las distribuciones de dosis se van a tratar mediante pandas DataFrames. Los datos del DataFrame corresponderán a las dosis, los nombres de las columnas serán las posiciones *x* y el índice las posiciones *y*.

    Vamos a tener entonces tres DataFrames: una del planificador y dos de la película: la original (resultado del procesdo de la imagen digitalizada) y la remuestreada y reubicda espacialmente.

    La del planificador se genera en la página `1_Plano_dosis_planificador.py` y se almacena en `st.session_state.pDdf`.

    La original de la película se genera en la página `3_Reorientar_y_exportar_dosis.py` y se almacena en `st.session_state.fDdf`.

    '''
    )
