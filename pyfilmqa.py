# Module pyFilmQA
# File pyFilmQA.py
# Version 0.1

"""
A module to process radiochromic films and to export the results in dxf format.
It provides also a converter from DICOM RT Dose plane distributions to dxf format.
dxf is a format used by Varian as an interchange data tool.
Dose planes in dxf can be imported in the Varian Portal Dosinmetry application.

"""

# Module dependencies

# - Config file
import configparser
# - Date formats
from datetime import datetime
# - Paths and file extensions managing
from pathlib import Path
# - Numerical calculations
import numpy as np
# - Data mamaging
import pandas as pd
# - DICOM files editing
import pydicom as dicom
# - TIFF files
from tifffile import TiffFile
from tifffile import imread as timread, imwrite as timwrite
# - Image processing
from skimage.io import imread, imsave
from skimage import img_as_float, img_as_uint
from skimage.measure import profile_line
# - Non-local means
from skimage.restoration import denoise_nl_means
# - JSON Files
from json import dumps
# - Non-local means
from skimage.restoration import denoise_nl_means
# - Interpolation
from scipy.interpolate import interp1d
# - Numerical non linear fits
from scipy.optimize import curve_fit
from scipy.optimize import minimize
# - Non linear function inversion
from scipy.optimize import fsolve
# - Calibration models fits
from lmfit import Parameters, Model
# - Progress bar
from stqdm import stqdm
# - To pass additional parameters to map function
from itertools import repeat
# - Multiprocessing
from multiprocessing import Pool
# - streamlit
import streamlit as st


# Funcion definitions

def HeaderCreator(DataOriginDateTime='', AcqType='Acquired Portal', PatientId1='', PatientId2='', LastName='', FirstName='', pxsp=[], imsz=[]):
    """
    A function to create the header of the dxf file

    ...

    Attributes
    ----------
    DataOriginDateTime : str
        The date and time creation of the data origin

    AcqType : str
        The type of the orgin data: acquired or predicted

    PatientId1 : str
        The first patient identification

    PatientId2 : str
        The second patient identification

    LastName : str
        The patient family name

    First Name : str
        The patient given name

    pxsp : list
        A list with the pixel spacing in mm

    imsz : list
        A list with the image size in pixels

    Returns
    -------
    header : str
        The header of the dxf file
    """

    headerGeneral = '\n'.join(
        [ '[General]',
          'FileFormat=Generic Dosimetry Exchange Format',
          'Version=1.0',
          'Creator=Film Dosimetry',
          'CreatorVersion=0.1',
          '[Geometry]',
          'Dimensions=2',
          'Axis1=X',
          'Size1=' + str(int(imsz[0])),
          'Res1=' + str(pxsp[0]),
          'Offset1=0.0',
          'Unit1=mm',
          'Separator1=\\t',
          'Axis2=Y',
          'Size2=' + str(int(imsz[1])),
          'Res2=' + str(pxsp[1]),
          'Offset2=-0.0',
          'Unit2=mm',
          'Separator2=\\n',
        ]
    )

    headerInterpretation = '\n'.join(
        [ '[Interpretation]',
          'Type=' + AcqType,
          'DataType=%f',
          'Unit=CU',
          'Location=Imager',
          'Medium=Undefined',
        ]
    )

    headerPatient = '\n'.join(
        ['[Patient]',
        'PatientId1=' + PatientId1,
        'PatientId2=' + PatientId2,
        'LastName=' + LastName,
        'FirstName=' + FirstName,
        ]
    )

    headerField = '\n'.join(
        ['[Field]',
          'PlanId=QAP',
          'FieldId=Field 1',
          'ExternalBeamId=TrueBeam1',
          'BeamType=Photon',
          'Energy=6000',
          'SAD=100',
          'Scale=IEC1217',
          'GantryAngle=0',
          'CollRtn=0',
          'CollX1=10.0',
          'CollX2=10.0',
          'CollY1=10.0',
          'CollY2=10.0',
        ]
    )

    headerPortal = '\n'.join(
        ['[PortalDose]',
          'SID=100.0',
          'Date=' + DataOriginDateTime,
        ]
    )

    headerData = '\n'.join(
        ['[Data]'
        ]
    )

    header = headerGeneral + '\n' + headerInterpretation + '\n' + headerPatient + '\n' + headerField + '\n' + headerPortal + '\n' + headerData + '\n'

    return header


def dxfString(Data=None, AcqType='Acquired Portal', PatientId1='', PatientId2='', LastName='', FirstName='', pxsp=[], imsz=[], DataOriginDateTime=''):
    """
    A function to output the dxf string

    ...

    Attributes
    ----------
    Data : 2D numpy array
        The data to be exported

    AcqType : str
        The type of the orgin data: acquired or predicted

    PatientId1 : str
        The first patient identification

    PatientId2 : str
        The second patient identification

    LastName : str
        The patient family name

    First Name : str
        The patient given name

    pxsp : list
        A list with the pixel spacing in mm

    imsz : list
        A list with the image size in pixels

    DataOriginDateTime: str
        The date and time creation of the data origin

     Returns
    -------
    dxfstr : str
        The dxf string
    """

    # Write the header
    headerstr = HeaderCreator(DataOriginDateTime=DataOriginDateTime, AcqType=AcqType, PatientId1=PatientId1, PatientId2=PatientId2, LastName=LastName, FirstName=FirstName, pxsp=pxsp, imsz=imsz)

    # Write the data
    df = pd.DataFrame(Data)
    datastr = df.to_csv(sep='\t', header=False, index=False, float_format='%.2f')

    # Write the dxf string
    dxfstr = headerstr + datastr

    return dxfstr

def dxfWriter(Data=None, dxfFileName='Film.dxf', AcqType='Acquired Portal', PatientId1='', PatientId2='', LastName='', FirstName='', pxsp=[], imsz=[], DataOriginDateTime=''):
    """
    A function to write the dxf file

    ...

    Attributes
    ----------
    Data : 2D numpy array
        The data to be exported

    dxfFileName : str or Path
        The path file to be written in

    AcqType : str
        The type of the orgin data: acquired or predicted

    PatientId1 : str
        The first patient identification

    PatientId2 : str
        The second patient identification

    LastName : str
        The patient family name

    First Name : str
        The patient given name

    pxsp : list
        A list with the pixel spacing in mm

    imsz : list
        A list with the image size in pixels

    DataOriginDateTime: str
        The date and time creation of the data origin

     Returns
    -------
        No data returned on exit
    """

    with open(dxfFileName, 'w') as dxf:
        # Write the header
        header = HeaderCreator(DataOriginDateTime=DataOriginDateTime, AcqType=AcqType, PatientId1=PatientId1, PatientId2=PatientId2, LastName=LastName, FirstName=FirstName, pxsp=pxsp, imsz=imsz)
        for line in header:
            dxf.write(line)

        df = pd.DataFrame(Data)
        # Write the data
        df.to_csv(dxf, sep='\t', header=False, index=False, float_format='%.2f')

def dcm2dxf(dcmf=None, config=None):
    """
    A function to convert RT Dose DICOM files to dxf format

    ...

    Attributes
    ----------
    dcmf : BytesIO
        The RT Dose DICOM data

    config : ConfigParser
        An object with the functionalities of the configparser module


     Returns
    -------
    dxffilePath on exit if successful
        The Path to file exported

    """

    PatientId1 = dcmf.PatientID
    PatientId2 = ''
    PatientName = str(dcmf.PatientName)
    PatientNames = PatientName.split('^')
    LastName, FirstName = PatientNames[`0`], PatientNames[1]
    if len(PatientNames) == 3:
        FirstName = PatientNames[1] + ' ' + PatientNames[2]
    demodict = {'PatientId1' : PatientId1, 'PatientId2' : PatientId2, 'LastName' : LastName, 'FirstName' : FirstName}
    pxsp = dcmf.PixelSpacing
    imsz = [dcmf.Rows, dcmf.Columns]
    pDim = dcmf.pixel_array*dcmf.DoseGridScaling
    dxffilePath = Path(config['DEFAULT']['exportpath'] + demodict['PatientId1'] + '/PlanStreamlit.dxf')
    strDataOriginDateTime = datetime.strptime(dcmf.InstanceCreationDate + ' ' + dcmf.InstanceCreationTime, '%Y%m%d %H%M%S.%f').strftime('%m/%d/%Y, %H:%M:%S')
    dxfWriter(Data=pDim, dxfFileName=dxffilePath, DataOriginDateTime=strDataOriginDateTime,
              AcqType='Predicted Portal', PatientId1=demodict['PatientId1'],
              PatientId2=demodict['PatientId1'], LastName=demodict['LastName'],
              FirstName=demodict['FirstName'], pxsp=pxsp, imsz=imsz)
    return dxffilePath

def dcm2dxfString(dcmf=None, config=None):
    """
    A function to output RT Dose DICOM files into a dxf format string

    ...

    Attributes
    ----------
    dcmf : BytesIO
        The RT Dose DICOM data

    config : ConfigParser
        An object with the functionalities of the configparser module

    Returns
    -------
    dxfstr : str
        A dxf format string

    """

    PatientId1 = dcmf.PatientID
    PatientId2 = ''
    PatientName = str(dcmf.PatientName)
    PatientNames = PatientName.split('^')
    LastName, FirstName = PatientNames[`0`], PatientNames[1]
    if len(PatientNames) == 3:
        FirstName = PatientNames[1] + ' ' + PatientNames[2]
    demodict = {'PatientId1' : PatientId1, 'PatientId2' : PatientId2, 'LastName' : LastName, 'FirstName' : FirstName}
    pxsp = dcmf.PixelSpacing
    imsz = [dcmf.Rows, dcmf.Columns]
    pDim = dcmf.pixel_array*dcmf.DoseGridScaling
    strDataOriginDateTime = datetime.strptime(dcmf.InstanceCreationDate + ' ' + dcmf.InstanceCreationTime, '%Y%m%d %H%M%S.%f').strftime('%m/%d/%Y, %H:%M:%S')
    dxfstr = dxfString(Data=pDim, DataOriginDateTime=strDataOriginDateTime, 
                        AcqType='Predicted Portal', PatientId1=demodict['PatientId1'],
                        PatientId2=demodict['PatientId1'], LastName=demodict['LastName'],
                        FirstName=demodict['FirstName'], pxsp=pxsp, imsz=imsz)
    return dxfstr

def calf(D, f, phir, kr, phib, kb):
    """
    The two phase polymer model dose response general function for every channel

    ...

    Attributes
    ----------
    D : float64
        Absorbed dose

    f : float64
        The base optical density

    phir : float64
        The relative abundance of the red phase polymer

    kr : float64
        The exponent in the saturation term of the red phase polymer

    phib : float64
        The relative abundance of the blue phase polymer

    kb : float64
        The exponent in the saturation term of the blue phase polymer

    Returns
    -------
    d : float64
        The optical density in each channel corresponding to the absorbed dose D following the sensitometry model based on the growth of two polymer phases

    """

    return f + phir * (1-np.exp(-kr*D)) + phib * (1-np.exp(-kb*D))

def iratf(d, a, b, c):
    """
    The calibration function following a sensitometric model bases in rational functions

    ...

    Attributes
    ----------
    d : float64
        Optical density as measured by the scanner

    a : float64
        First rational function parameter

    b : float64
        Second rational function parameter

    c : float64
        Third rational function parameter

    Returns
    -------
    D : float64
        The abosrbed dose D corresponding to the optical density d in each channel following the sensitometry model based on rational functions

    """

    return (a - c * 10**-d)/(10**-d - b)

def coordOAC(imfile=None, bbfile='./tmp/bb.csv'):
    """
    A function to calculate the relavant coordiantes for the off-axis spatial correction

    ...

    Attributes
    ----------
    imfile : str
        The name of the image file, the file containing the scanned image of the dose distribution, the calibration strip and the base strip in TIFF format.
    bbfile : str
        the name of the bounding box file, the file containing the position and size of the bounding boxes of the image file. It should be a csv file.

    Returns
    -------
    cdf : pandas DataFrame
        A pandas DataFrame containing the relavant coordiantes for the off-axis spatial correction

    """
    bbdf = pd.read_csv(bbfile)

    creg = bbdf.loc[bbdf.label == 'Center'] # Image center
    o = creg.left.values[0] + int(creg.width.values[0]/2)
    calreg = bbdf.loc[bbdf.label == 'Calibration'] # Calibration strip
    c = calreg.left.values[0] + int(calreg.width.values[0]/2)
    dosereg = bbdf.loc[bbdf.label == 'Film'] # Film dose region
    p0 = dosereg.left.values[0]

    pxsp = TIFFPixelSpacing(imfile=imfile)
    s = pxsp[0]

    lcdf = pd.DataFrame({'o' : o, 'c' : c, 'p0' : p0, 's' : s}, index=[0])

    return lcdf

def TIFFPixelSpacing(imfile=None):
    """
    A function to get the pixel spacing from the TIFF file

    ...

    Attributes
    ----------
    imfile : str
        The name of the scan image with the measured dose distribution, the calibration strip and the background patch

     Returns
    -------
        pxsp :  List
        A list with the X and Y pixel spacing in mm
    """

    with TiffFile(imfile) as tif:
        page_tags = tif.pages[0].tags
    xres = page_tags['XResolution'].value
    yres = page_tags['YResolution'].value
    xdpi = xres[0]/xres[1]
    ydpi = yres[0]/yres[1]
    inch = 25.4 # mm
    return [inch/xdpi, inch/ydpi]

def DoseImageSize(im=None):
    """
    A function to get the image size of the film measured dose distribution

    ...

    Attributes
    ----------
    im : 2D numpy array
        The array containing the measured dose distribution

     Returns
    -------
        imsz :  List
        A list with the X and Y image size in pixels
    """
    imsz = [im.shape[1], im.shape[0]]
    return imsz


def segRegs(imfile=None, bbfile='tmp/bb.csv'):
    """
    A function to segment the film image

    ...

    Attributes
    ----------
    imfile : str
        The name of the image file, the file containing the scanned image of the dose distribution, the calibration strip and the base strip in TIFF format.
    bbfile : str
        The name of the bounding box file, the file containing the position and size of the bounding boxes of the image file. It should be a csv file.

    Returns
    -------
    No value returned

    """
    # Leer el archivo de regiones de interes y generar un dataframe con las coordenas y dimensiones de las regiones
    bbdf = pd.read_csv(bbfile)
    # Nombre del archivo de imagen
    filename = Path(imfile)
    # Segmentar el archivo de imagen
    im = imread(imfile)
    for r in ['Film', 'Calibration', 'Background', 'Center']:
        reg = bbdf.loc[bbdf.label == r]
        rim = im[reg.top.values[0]:reg.top.values[0]+reg.height.values[0], reg.left.values[0]:reg.left.values[0]+reg.width.values[0], :]
        # Leer los metadatos del archivo de imagen
        with TiffFile(imfile) as tif:
            page_tags = tif.pages[0].tags
            # Guardar cada regiÃ³n un archivo
            # Extratags
            metadata_tag = dumps({"PatientId": '001PATFILM', "PatientName": 'Prueba', 'PatientFamilyName' : 'PelÃ­culas', 'Sex' : 'Male'})
            extra_tags = [("MicroManagerMetadata", 's', 0, metadata_tag, True),
                          ('Make', 's', 0, page_tags['Make'].value, True),
                          ('Model', 's', 0, page_tags['Model'].value, True),
                          ('DateTime', 's', 0, page_tags['DateTime'].value, True),
                          ("ProcessingSoftware", 's', 0, "pyFilmQAModule", True)]
            timwrite(filename.with_suffix('.' + str(r) + '.tif'), rim, extratags=extra_tags)

def baseDetermination(imfile=None, config=None):
    """
    A function to calculate the base value in every color channel

    ...

    Attributes
    ---------
    imfile : str
        The name of the image file, the file containing the scanned image of the dose distribution, the calibration strip and the base strip in TIFF format.

    config : ConfigParser
        An object with the functionalities of the configparser module

    Returns
    -------
    imbase : float64 numpy array
        An array containing the value of the base digital signal in every color channel.

    """
    # Derivar el nombre del archivo de fondo
    bkgfilename = Path(imfile)
    bkgfilename = bkgfilename.with_suffix('.Background.tif')
    # Leer la imagen de fondo
    fim = imread(bkgfilename)
    # Tomar el valor del margen del arhivo de configuraciÃ³n
    mrg = int(config['Base']['margin'])
    # Tomar la parte central
    fim = fim[mrg:-mrg, mrg:-mrg, :]
    # Devolver el valor del fondo en cada canal
    return np.log10(2**16/fim.mean(axis=(0,1)))

def nlmf(imfile=None, config=None):
    """
    A function to denoise a multichannel image using a non-local means procedure.

    imfile : str
        The name of the image file, the file containing the image to be denoised.

    config : ConfigParser
        An object with the functionalities of the configparser module

    Returns
    -------
    udim = unsigned int numpy array
        A numpy array of unsigned ints with shape (xpixels, ypixels, channels)
    """
    im = imread(imfile)
    fim=img_as_float(im)
    dim=denoise_nl_means(fim,
                         patch_size = int(config['NonLocalMeans']['PatchSize']),
                         patch_distance = int(config['NonLocalMeans']['PatchDistance']),
                         h=float(config['NonLocalMeans']['h']),
                         channel_axis=int(config['NonLocalMeans']['ChannelAxis']))
    udim=img_as_uint(dim)

    return udim

def iratf(d, a, b, c):
    """
    The calibration function following a sensitometric model bases in rational functions

    ...

    Attributes
    ----------
    d : float64
        Optical density as measured by the scanner

    a : float64
        First rational function parameter

    b : float64
        Second rational function parameter

    c : float64
        Third rational function parameter

    Returns
    -------
    D : float64
        The abosrbed dose D corresponding to the optical density d in each channel following the sensitometry model based on rational functions

    """

    return (a - c * 10**-d)/(10**-d - b)

def readCalParms(config=None):
    """
    A function to read the established standard calibration parameters for the EBT3 film measured by the Microtek 1000 XL scanner

    ...

    Attributes
    ----------
    config : ConfigParser
        An object with the functionalities of the configparser module

    Returns
    -------
    caldf : DataFrame
        A pandas DataFrame with the calibration parameters for every color channel (multiphase model)

    """

    configpath = './config/'
    modelsfile = config['Models']['File']
    modelsheet = config['Models']['mphSheet']

    caldf = pd.read_excel(configpath + modelsfile, sheet_name=modelsheet)
    caldf.set_index('Unnamed: 0', inplace=True)
    caldf.index.names = ['ch']
    return caldf

def readRatParms(config=None):
    """
    A function to read a standard calibration set of parameters following the rational model for the EBT3 film measured by the Microtek 1000 XL scanner

    ...

    Attributes
    ----------
    config : ConfigParser
        An object with the functionalities of the configparser module

    Returns
    -------
    ratdf : DataFrame
        A pandas DataFrame with the calibration parameters for every color channel (rational model)

    """

    configpath = './config/'
    modelsfile = config['Models']['File']
    modelsheet = config['Models']['racSheet']
    ratdf = pd.read_excel(configpath + modelsfile, sheet_name=modelsheet)
    ratdf.set_index('Unnamed: 0', inplace=True)
    ratdf.index.names = ['ch']
    return ratdf

def rootcalf(D, d, f, phir, kr, phib, kb):
    """
    An internal module use function.
    It expresses the nonlinear equation to get the absorbed dose D from the optical density d using the multiphase model

    ...


    Returns
    -------
    rootcalf : float64
        The difference between the measured optical density d and the optical density as calculated for the multiphase model for the absorbed dose D

    """

    return d - calf(D, f, phir, kr, phib, kb)

def icalf(d, Dsem, f, phir, kr, phib, kb):
    """
    The calibration function following the multiphase model

    ...

    Attributes
    ----------
    d : float64
        The measured optical density
    Dsem : float64
        A seed value of the absorbed D to solve the nonlinear equation
    f : float64
        The base optical density

    phir : float64
        The relative abundance of the red phase polymer

    kr : float64
        The exponent in the saturation term of the red phase polymer

    phib : float64
        The relative abundance of the blue phase polymer

    kb : float64
        The exponent in the saturation term of the blue phase polymer

    Returns
    -------
    D : float64
        The calculated absorbed dose D corresponding to the measured optical density d

    """

    return fsolve(rootcalf, Dsem, (d, *[f, phir,  kr, phib, kb]))[0]

def Ricalf(d, rcalps, rratps):
    """
    The calibration function following the multiphase model for the red channel

    ...

    Attributes
    ----------
    d : float64
        The measured optical density

    rcalps : 1D numpy array
        The current scan calibration parameters for the red channel

    rratps : 1D numpy array
        The current scan calibration rational approximation for the red channel

    Returns
    -------
    D : float64
        The calculated absorbed dose D corresponding to the measured optical density d for the red channel

    """
    return icalf(d, iratf(d, *rratps), *rcalps)

Ricalfv = np.vectorize(Ricalf, excluded={1, 2})

def Gicalf(d, gcalps, gratps):
    """
    The calibration function following the multiphase model for the green channel

    ...

    Attributes
    ----------
    d : float64
        The measured optical density

    gcalps : 1D numpy array
        The current scan calibration parameters for the green channel

    gratps : 1D numpy array
        The current scan calibration rational approximation for the green channel


    Returns
    -------
    D : float64
        The calculated absorbed dose D corresponding to the measured optical density d for the green channel

    """

    return icalf(d, iratf(d, *gratps), *gcalps)

Gicalfv = np.vectorize(Gicalf, excluded={1, 2})

def Bicalf(d, bcalps, bratps):
    """
    The calibration function following the multiphase model for the blue channel

    ...

    Attributes
    ----------
    d : float64
        The measured optical density

    bcalps : 1D numpy array
        The current scan calibration parameters for the blue channel

    bratps : 1D numpy array
        The current scan calibration rational approximation for the blue channel


    Returns
    -------
    D : float64
        The calculated absorbed dose D corresponding to the measured optical density d for the blue channel

    """

    return icalf(d, iratf(d, *bratps), *bcalps)

Bicalfv = np.vectorize(Bicalf, excluded={1, 2})

def PDDCalibration(config=None, imfile=None, base=None):
    """
    A function to get the current scan calibration parameters

    ...

    Attributes
    ----------
    config : ConfigParser
        An object with the functionalities of the configparser module

    imfile : str
        The name of the image file, the file containing the scanned image of the dose distribution, the calibration strip and the base strip in TIFF format.

    base : 1D numpy array
        Array containing the calculated base values for every color channel

    Returns
    -------
    caldf : pandas DataFrame
        The current scan calibration parameters

    cdf : pandas dataframe
        The calibration data from which caldf is obtained

    sips : float
        Scanned image pixel size [mm]

    """

    # Read the calculated calibration absorbed dose distributiom (PDD)
    pddcalibfile = './config/' + config['Calibration']['File']
    cdf = pd.read_excel(pddcalibfile)

    # Read the calibration image segment data
    calfilename = Path(imfile)
    calfilename = calfilename.with_suffix('.Calibration.tif')
    cim = imread(calfilename)

    # Denoise
    dcim = nlmf(imfile=calfilename, config=config)

    # Calculate spatial coordinates
    with TiffFile(imfile) as tif:
        page_tags = tif.pages[0].tags
    xres = page_tags['XResolution'].value
    dpi = xres[0]/xres[1]
    zres = 2.54/dpi
    sips = zres
    zv = np.arange(0, (cim.shape[0]+0.5)*zres, zres)

    # Depth dose distribution in digital signal units
    dch, dcw, _chanels = dcim.shape
    cdd = profile_line(dcim, src=(0, dcw/2), dst=(dch, dcw/2), linewidth=20)

    # Depth dose distribution in optical density units
    ddf = pd.DataFrame({'z': zv, 'dr' : np.log10(2**16/cdd[:,0]), 'dg' : np.log10(2**16/cdd[:,1]), 'db' : np.log10(2**16/cdd[:,2])})
    ddf.replace([np.inf, -np.inf], np.nan, inplace=True)
    ddf.dropna(inplace=True)

    # Resampling to the used ratiotherapy planning system spatial resolution
    zsh, zmin, zmax = float(config['Calibration']['shift']), float(config['Calibration']['depthmin']), float(config['Calibration']['depthmax'])

    # Interpolation functions
    rddf = interp1d(ddf.z + zsh, ddf.dr, bounds_error=False)
    gddf = interp1d(ddf.z + zsh, ddf.dg, bounds_error=False)
    bddf = interp1d(ddf.z + zsh, ddf.db, bounds_error=False)

    # Add to the calibration DataFrame the optical density corresponding to the radiotherapy planning system data points
    cdf['dR'] = rddf(cdf.z)
    cdf['dG'] = gddf(cdf.z)
    cdf['dB'] = bddf(cdf.z)

    # Filter the calibration relevant depths
    cdf = cdf.loc[(cdf.z > zmin) & (cdf.z < zmax)]

    # Drop NA values
    cdf.dropna(inplace=True)

    # Read the standard calibration parameters (multiphse model)
    configpath = './config/'
    modelsfile = config['Models']['File']
    modelsheet = config['Models']['mphSheet']
    caldf = pd.read_excel(configpath + modelsfile, sheet_name=modelsheet)
    caldf.set_index('Unnamed: 0', inplace=True)
    caldf.index.names = ['ch']

    # Read the standard calibration parameters (rational model)
    modelsheet = config['Models']['racSheet']
    racdf = pd.read_excel(configpath + modelsfile, sheet_name=modelsheet)
    racdf.set_index('Unnamed: 0', inplace=True)
    racdf.index.names = ['ch']

    # Extract every color channel parameters
    # Multiphase
    rcalps = caldf.iloc[0].values
    gcalps = caldf.iloc[1].values
    bcalps = caldf.iloc[2].values
    # Rational
    rracps = racdf.iloc[0].values
    gracps = racdf.iloc[1].values
    bracps = racdf.iloc[2].values

    # Calibration models for every channel
    rcalfmodel = Model(calf)
    gcalfmodel = Model(calf)
    bcalfmodel = Model(calf)

    # Parameter initialization
    # Red
    rcalfparams = rcalfmodel.make_params(
        f = base[0],
        phir = rcalps[1],
        kr = rcalps[2],
        phib = rcalps[3],
        kb = rcalps[4]
    )

    rcalfparams['f'].vary = False
    rcalfparams['phir'].min = 0
    rcalfparams['kr'].vary = False
    rcalfparams['phib'].min = 0
    rcalfparams['kb'].vary = False

    # Green
    gcalfparams = gcalfmodel.make_params(
        f = base[1],
        phir = gcalps[1],
        kr = gcalps[2],
        phib = gcalps[3],
        kb = gcalps[4],
    )

    gcalfparams['f'].vary = False
    gcalfparams['phir'].min = 0
    gcalfparams['kr'].vary = False
    gcalfparams['phib'].min = 0
    gcalfparams['kb'].vary = False

    # Blue
    bcalfparams = bcalfmodel.make_params(
        f = base[2],
        phir = bcalps[1],
        kr = bcalps[2],
        phib = bcalps[3],
        kb = gcalps[4],
    )

    bcalfparams['f'].vary = False
    bcalfparams['phir'].min = 0
    bcalfparams['kr'].vary = False
    bcalfparams['phib'].min = 0
    bcalfparams['kb'].vary = False

    # Fit
    rcalfresult = rcalfmodel.fit(cdf.dR, rcalfparams, D = cdf.D)
    gcalfresult = gcalfmodel.fit(cdf.dG, gcalfparams, D = cdf.D)
    bcalfresult = bcalfmodel.fit(cdf.dB, bcalfparams, D = cdf.D)

    # Parameter reorganization
    caldf = pd.DataFrame({'f' : base[0], 'phir' : rcalfresult.params.get('phir').value, 'kr' : rcalps[2], 'phib' : rcalfresult.params.get('phib').value, 'kb' : rcalps[4]}, index=['R'])
    tcaldf = pd.DataFrame({'f' : base[1], 'phir' : gcalfresult.params.get('phir').value, 'kr' : gcalps[2], 'phib' : gcalfresult.params.get('phib').value, 'kb' : gcalps[4]}, index=['G'])
    caldf = pd.concat([caldf, tcaldf])
    tcaldf = pd.DataFrame({'f' : base[2], 'phir' : bcalfresult.params.get('phir').value, 'kr' : bcalps[2], 'phib' : bcalfresult.params.get('phib').value, 'kb' : bcalps[4]}, index=['B'])
    caldf = pd.concat([caldf, tcaldf])


    # Return the current scan calibration parameter DataFrmme, calibration dataframe and pixel size
    return caldf, cdf, sips

def validatecalibf(cda=None, config=None, caldf=None):
    """
    A function to validate de calibration parameters

    ...

    Attributes
    ----------
    cda : 3D numpy array
        Optical density array from the calibration film. Each dimension correspond to one color channel

    config : ConfigParser
        An object with the functionalities of the configparser module

    caldf : pandas DataFrame
        The current scan calibration parameters

    Returns
    -------
    validatecaliba : 1D numpy arrray
        The array of doses predicted by the calibration model
    """

    # Current multiphase calibration parameters
    rcalps = caldf.iloc[0].values
    gcalps = caldf.iloc[1].values
    bcalps = caldf.iloc[2].values

    # Rational approximation

    # Define models
    rratfmodel = Model(iratf)
    gratfmodel = Model(iratf)
    bratfmodel = Model(iratf)

    # Initialize parameters
    rratparams = rratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    gratparams = gratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    bratparams = bratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )


    # Generate calibration points

    vDrat = np.array([0.5, 0.75, 1., 1.25, 1.5, 2., 3., 4., 5., 7., 9.])

    vdrrat =  calf(vDrat, *rcalps)
    vdgrat =  calf(vDrat, *gcalps)
    vdbrat =  calf(vDrat, *bcalps)

    # Fit
    rratfit = rratfmodel.fit(data=vDrat, params=rratparams, d=vdrrat)
    gratfit = gratfmodel.fit(data=vDrat, params=gratparams, d=vdgrat)
    bratfit = bratfmodel.fit(data=vDrat, params=bratparams, d=vdbrat)

    # Rational calibration paramters
    rratps = np.array([k.value for k in rratfit.params.values()])
    gratps = np.array([k.value for k in gratfit.params.values()])
    bratps = np.array([k.value for k in bratfit.params.values()])

    # Dose calculation
    adDr = np.zeros_like(cda[...,0])
    adDg = np.zeros_like(cda[...,1])
    adDb = np.zeros_like(cda[...,2])
    nrs = cda.shape[0]
    for j in stqdm(np.arange(nrs), st_container=st.sidebar, desc='Validando la calibración:'):

        # Red channel
        adDr[j] = Ricalf(cda[j, 0], rcalps, rratps)

        # Green channel
        adDg[j] = Gicalf(cda[j, 1], gcalps, rratps)

        # Blue channel
        adDb[j] = Bicalf(cda[j, 2], bcalps, rratps)

    Dmax = float(config['DosePlane']['Dmax'])
    wr, wg, wb = float(config['NonLocalMeans']['wRed']), float(config['NonLocalMeans']['wGreen']), float(config['NonLocalMeans']['wBlue'])
    wT = wr + wg + wb

    validatecaliba = (wr*adDr + wg*adDg + wb*adDb)/wT

    validatecaliba = np.nan_to_num(validatecaliba, posinf=1e10, neginf=-1e10)

    validatecaliba[validatecaliba < 0] = 0

    validatecaliba[validatecaliba > Dmax] = Dmax

    # Return the dose array for validation purposes
    return validatecaliba

def mphspcnlmprocf(imfile=None, config=None, caldf=None, ccdf=None):
    """
    A function to process the dose distribution image using nonlocal means denoising and the multiphase calibration model with spatial correction

    ...

    Attributes
    ----------
    imfile : str
        The name of the image file, the file containing the scanned image of the dose distribution, the calibration strip and the base strip in TIFF format.

    config : ConfigParser
        An object with the functionalities of the configparser module

    caldf : pandas DataFrame
        The current scan calibration parameters

    ccdf : pandas DataFrame
        A data structure containing the relevant geometric parameters for the spatial correction

    Returns
    -------
    mphspcnlmprocim : 2D numpy arrray
        The dose distribution
    """

    dosefilename = Path(imfile)
    dosefilename = dosefilename.with_suffix('.Film.tif')

    # Denoise
    udim = nlmf(dosefilename, config)

    # Optical density image
    dim = np.log10(2**16/(udim+0.0000001))

    # Current multiphase calibration parameters
    rcalps = caldf.iloc[0].values
    gcalps = caldf.iloc[1].values
    bcalps = caldf.iloc[2].values

    # Spatial correction functions
    recadc = np.load('./config/' + config['Models']['oadcFile'], allow_pickle=True)
    phiRrf = recadc[0, 0].item()
    phiGrf = recadc[0, 1].item()
    phiBrf = recadc[0, 2].item()
    phiRbf = recadc[1, 0].item()
    phiGbf = recadc[1, 1].item()
    phiBbf = recadc[1, 2].item()

    # Rational approximation

    # Define models
    rratfmodel = Model(iratf)
    gratfmodel = Model(iratf)
    bratfmodel = Model(iratf)

    # Initialize parameters
    rratparams = rratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    gratparams = gratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    bratparams = bratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )


    # Generate calibration points

    vDrat = np.array([0.5, 0.75, 1., 1.25, 1.5, 2., 3., 4., 5., 7., 9.])

    vdrrat =  calf(vDrat, *rcalps)
    vdgrat =  calf(vDrat, *gcalps)
    vdbrat =  calf(vDrat, *bcalps)

    # Fit
    rratfit = rratfmodel.fit(data=vDrat, params=rratparams, d=vdrrat)
    gratfit = gratfmodel.fit(data=vDrat, params=gratparams, d=vdgrat)
    bratfit = bratfmodel.fit(data=vDrat, params=bratparams, d=vdbrat)

    # Rational calibration paramters
    rratps = np.array([k.value for k in rratfit.params.values()])
    gratps = np.array([k.value for k in gratfit.params.values()])
    bratps = np.array([k.value for k in bratfit.params.values()])

    # Dose calculation
    adDr = np.zeros_like(dim[...,0])
    adDg = np.zeros_like(dim[...,1])
    adDb = np.zeros_like(dim[...,2])
    nrs = dim.shape[1]
    for j in stqdm(np.arange(nrs), st_container=st.sidebar, desc='Procesando la película'):
        xc = np.abs(ccdf.o - ccdf.c) * ccdf.s / 25.4
        x = np.abs(ccdf.o - (ccdf.p0 + j)) * ccdf.s / 25.4
        npx = dim.shape[0]
        for i in np.arange(npx):

            # Red channel
            f, phir, kr, phib, kb = rcalps
            rcalcps = np.array([f, phir * phiRrf(x)/phiRrf(xc), kr, phib * phiRbf(x)/phiRbf(xc), kb])
            adDr[i, j] = Ricalf(dim[i, j, 0], rcalcps, rratps)

            # Green channel
            f, phir, kr, phib, kb = gcalps
            gcalcps = np.array([f, phir * phiGrf(x)/phiGrf(xc), kr, phib * phiGbf(x)/phiGbf(xc), kb])
            adDg[i, j] = Gicalf(dim[i, j, 1], gcalcps, rratps)

            # Blue channel
            f, phir, kr, phib, kb = bcalps
            bcalcps = np.array([f, phir * phiBrf(x)/phiBrf(xc), kr, phib * phiBbf(x)/phiBbf(xc), kb])
            adDb[i, j] = Bicalf(dim[i, j, 2], bcalcps, rratps)

    Dmax = float(config['DosePlane']['Dmax'])
    wr, wg, wb = float(config['NonLocalMeans']['wRed']), float(config['NonLocalMeans']['wGreen']), float(config['NonLocalMeans']['wBlue'])
    wT = wr + wg + wb

    mphspcnlmprocim = (wr*adDr + wg*adDg + wb*adDb)/wT

    mphspcnlmprocim = np.nan_to_num(mphspcnlmprocim, posinf=1e10, neginf=-1e10)

    mphspcnlmprocim[mphspcnlmprocim < 0] = 0

    mphspcnlmprocim[mphspcnlmprocim > Dmax] = Dmax

    # Return the dose image
    return mphspcnlmprocim

def premphspcnlmprocf(imfile=None, config=None, caldf=None, ccdf=None):
    """
    A function to preprocess the dose distribution image using nonlocal means denoising and the multiphase calibration model with spatial correction

    ...

    Attributes
    ----------
    imfile : str
        The name of the image file, the file containing the scanned image of the dose distribution, the calibration strip and the base strip in TIFF format.

    config : ConfigParser
        An object with the functionalities of the configparser module

    caldf : pandas DataFrame
        The current scan calibration parameters

    ccdf : pandas DataFrame
        A data structure containing the relevant geometric parameters for the spatial correction

    Returns
    -------
    mphspcnlmprocim : 2D numpy arrray
        The dose distribution
    """
    dosefilename = Path(imfile)
    dosefilename = dosefilename.with_suffix('.Film.tif')

    # Denoise
    udim = nlmf(dosefilename, config)

    # Optical density image
    dim = np.log10(2**16/(udim+0.0000001))

    # Current multiphase calibration parameters
    rcalps = caldf.iloc[0].values
    gcalps = caldf.iloc[1].values
    bcalps = caldf.iloc[2].values

    # Spatial correction functions
    recadc = np.load('./config/' + config['Models']['oadcFile'], allow_pickle=True)
    phiRrf = recadc[0, 0].item()
    phiGrf = recadc[0, 1].item()
    phiBrf = recadc[0, 2].item()
    phiRbf = recadc[1, 0].item()
    phiGbf = recadc[1, 1].item()
    phiBbf = recadc[1, 2].item()

    # Rational approximation

    # Define models
    rratfmodel = Model(iratf)
    gratfmodel = Model(iratf)
    bratfmodel = Model(iratf)

    # Initialize parameters
    rratparams = rratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    gratparams = gratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    bratparams = bratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )


    # Generate calibration points

    vDrat = np.array([0.5, 0.75, 1., 1.25, 1.5, 2., 3., 4., 5., 7., 9.])

    vdrrat =  calf(vDrat, *rcalps)
    vdgrat =  calf(vDrat, *gcalps)
    vdbrat =  calf(vDrat, *bcalps)

    # Fit
    rratfit = rratfmodel.fit(data=vDrat, params=rratparams, d=vdrrat)
    gratfit = gratfmodel.fit(data=vDrat, params=gratparams, d=vdgrat)
    bratfit = bratfmodel.fit(data=vDrat, params=bratparams, d=vdbrat)

    # Rational calibration paramters
    rratps = np.array([k.value for k in rratfit.params.values()])
    gratps = np.array([k.value for k in gratfit.params.values()])
    bratps = np.array([k.value for k in bratfit.params.values()])

    DimcolsList = []
    dimcols = [dim[:, y, :] for y in np.arange(dim.shape[1])]
    xc = np.abs(ccdf.o - ccdf.c) * ccdf.s / 25.4

    Dim = np.array(
        list(
            tqdm(
                map(wrapped_colDoseCalculationMphspcnlmprocf,
                    [
                        [col, dimcol, ccdf, xc, rcalps, gcalps, bcalps,
                        phiRrf, phiRbf, phiGrf, phiGbf, phiBrf, phiBbf,
                        rratps, gratps, bratps] for col, dimcol in enumerate(dimcols)
                    ]
                ), total=len(dimcols)
            )
        )
    )
    return Dim

def mphspcnlmprocf_multiprocessing(imfile=None, config=None, caldf=None, ccdf=None):
    """
    A function to preprocess the dose distribution image using nonlocal means denoising and the multiphase calibration model with spatial correction

    ...

    Attributes
    ----------
    imfile : str
        The name of the image file, the file containing the scanned image of the dose distribution, the calibration strip and the base strip in TIFF format.

    config : ConfigParser
        An object with the functionalities of the configparser module

    caldf : pandas DataFrame
        The current scan calibration parameters

    ccdf : pandas DataFrame
        A data structure containing the relevant geometric parameters for the spatial correction

    Returns
    -------
    mphspcnlmprocim : 2D numpy arrray
        The dose distribution
    """
    dosefilename = Path(imfile)
    dosefilename = dosefilename.with_suffix('.Film.tif')

    # Denoise
    udim = nlmf(dosefilename, config)

    # Optical density image
    dim = np.log10(2**16/(udim+0.0000001))

    # Current multiphase calibration parameters
    rcalps = caldf.iloc[0].values
    gcalps = caldf.iloc[1].values
    bcalps = caldf.iloc[2].values

    # Spatial correction functions
    scfile = './config/'+config['Models']['oadcFile']
    recadc = np.load(scfile, allow_pickle=True)
    phiRrf = recadc[0, 0].item()
    phiGrf = recadc[0, 1].item()
    phiBrf = recadc[0, 2].item()
    phiRbf = recadc[1, 0].item()
    phiGbf = recadc[1, 1].item()
    phiBbf = recadc[1, 2].item()

    # Rational approximation

    # Define models
    rratfmodel = Model(iratf)
    gratfmodel = Model(iratf)
    bratfmodel = Model(iratf)

    # Initialize parameters
    rratparams = rratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    gratparams = gratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )

    bratparams = bratfmodel.make_params(
        a = 0.1,
        b = 0.1,
        c = 0.1
    )


    # Generate calibration points

    vDrat = np.array([0.5, 0.75, 1., 1.25, 1.5, 2., 3., 4., 5., 7., 9.])

    vdrrat =  calf(vDrat, *rcalps)
    vdgrat =  calf(vDrat, *gcalps)
    vdbrat =  calf(vDrat, *bcalps)

    # Fit
    rratfit = rratfmodel.fit(data=vDrat, params=rratparams, d=vdrrat)
    gratfit = gratfmodel.fit(data=vDrat, params=gratparams, d=vdgrat)
    bratfit = bratfmodel.fit(data=vDrat, params=bratparams, d=vdbrat)

    # Rational calibration paramters
    rratps = np.array([k.value for k in rratfit.params.values()])
    gratps = np.array([k.value for k in gratfit.params.values()])
    bratps = np.array([k.value for k in bratfit.params.values()])


    DimcolsList = []
    dimcols = [dim[:, y, :] for y in np.arange(dim.shape[1])]
    xc = np.abs(ccdf.o - ccdf.c) * ccdf.s / 25.4
    xl = [np.abs(ccdf.o - (ccdf.p0 + col)) * ccdf.s / 25.4 for col, dimcol in enumerate(dimcols)]
    colsrcalps = np.array([rcalps * np.array([1, phiRrf(x)/phiRrf(xc), 1, phiRbf(x)/phiRbf(xc), 1]) for x in xl], dtype=object)
    colsgcalps = np.array([gcalps * np.array([1, phiGrf(x)/phiGrf(xc), 1, phiGbf(x)/phiGbf(xc), 1]) for x in xl], dtype=object)
    colsbcalps = np.array([bcalps * np.array([1, phiBrf(x)/phiBrf(xc), 1, phiBbf(x)/phiBbf(xc), 1]) for x in xl], dtype=object)

    with Pool(None) as p:
        Dim = np.array(
            list(
                stqdm(
                     p.imap(wrapped_colDoseCalculationMphspcnlmprocf,
                              [[dimcol,
                                colsrcalps[col], colsgcalps[col], colsbcalps[col],
                                rratps, gratps, bratps] for col, dimcol in enumerate(dimcols)]
                     ), total=len(dimcols), st_container=st.sidebar, desc='Procecesando la película:'
                )
            )
        )
    return Dim

def colDoseCalculationMphspcnlmprocf(parl):
    """
    A function to calculate the dose for every color channel in every pixel of a given colummn from the optical density image
    It is an accessory function for multiprocessing. It should not be call outside the premphspcnlmprocf function.

    ...

    Attributes
    ----------

    Returns
    -------
    Dimcol : 2D numpy arrray
        The column dose distribution for the three color channels
    """

    dimcol = parl[0]
    colrcalps = parl[1]
    colgcalps = parl[2]
    colbcalps = parl[3]
    rratps = parl[4]
    gratps = parl[5]
    bratps = parl[6]

    Dimcol  = np.empty_like(dimcol)

    for i in np.arange(len(dimcol)):
        # Red channel
        Dimcol[i, 0] = Ricalf(dimcol[i, 0], colrcalps, rratps)

        # Green channel
        Dimcol[i, 1] = Gicalf(dimcol[i, 1], colgcalps, gratps)

        # Blue channel
        Dimcol[i, 2] = Bicalf(dimcol[i, 2], colbcalps, bratps)

    return Dimcol

def wrapped_colDoseCalculationMphspcnlmprocf(parl):
    return colDoseCalculationMphspcnlmprocf(parl)

def postmphspcnlmprocf(Dim=None, config=None):
    """
    Postprocessing the dose distribution image

    ...

    Attributes
    ----------
    Dim : 3D numpy array
        A numpy array with the image dose from every color channel

    config : ConfigParser
        An object with the functionalities of the configparser module

    Returns
    -------
    mphspcnlmprocim : 2D numpy arrray
        The dose distribution

    """
    Dmax = float(config['DosePlane']['Dmax'])
    if 'Dmax' in st.session_state:
        Dmax = st.session_state.Dmax

    wr, wg, wb = float(config['NonLocalMeans']['wRed']), float(config['NonLocalMeans']['wGreen']), float(config['NonLocalMeans']['wBlue'])
    wT = wr + wg + wb

    mphspcnlmprocim = (wr*Dim[..., 0] + wg*Dim[..., 1] + wb*Dim[..., 2])/wT

    mphspcnlmprocim = np.nan_to_num(mphspcnlmprocim, posinf=1e10, neginf=-1e10)

    mphspcnlmprocim[mphspcnlmprocim < 0] = 0

    mphspcnlmprocim[mphspcnlmprocim > Dmax] = Dmax

    # Return the dose image
    return mphspcnlmprocim
