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
# - Data mamaging
import pandas as pd
# - DICOM files editing
import pydicom as dicom

# Funcion definitions

def HeaderCreator(DataOriginDateTime='', AcqType='Acquired Portal', PatientId1='', PatientId2='', LastName='', FirstName='', pxsp=[], imsz=[]):
    """
    A function to create the heaer of the dxf file

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

def dcm2dxf(dcmf=None):
    """
    A function to convert RT Dose DICOM files to dxf format

    ...

    Attributes
    ----------
    dcmf : BytesIO
        The RT Dose DICOM data

     Returns
    -------
    dxffilePath on exit if successful
        The Path to file exported

    """

    PatientId1 = dcmf.PatientID
    PatientId2 = ''
    PatientName = str(dcmf.PatientName)
    LastName, FirstName = PatientName.split('^')
    demodict = {'PatientId1' : PatientId1, 'PatientId2' : PatientId2, 'LastName' : LastName, 'FirstName' : FirstName}
    pxsp = dcmf.PixelSpacing
    imsz = [dcmf.Rows, dcmf.Columns]
    pDim = dcmf.pixel_array*dcmf.DoseGridScaling
    dxffilePath = Path('/home/radiofisica/Shares/Radiofisica/Medidas Pacientes/IMRT/' + demodict['PatientId1'] + '/PlanStreamlit.dxf')
    strDataOriginDateTime = datetime.strptime(dcmf.InstanceCreationDate + ' ' + dcmf.InstanceCreationTime, '%Y%m%d %H%M%S.%f').strftime('%m/%d/%Y, %H:%M:%S')
    dxfWriter(Data=pDim, dxfFileName=dxffilePath, DataOriginDateTime=strDataOriginDateTime,
              AcqType='Predicted Portal', PatientId1=demodict['PatientId1'],
              PatientId2=demodict['PatientId1'], LastName=demodict['LastName'],
              FirstName=demodict['FirstName'], pxsp=pxsp, imsz=imsz)
    return dxffilePath
