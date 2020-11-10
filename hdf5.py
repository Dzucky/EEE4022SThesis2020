import h5py
import numpy as np
import json
import configparser
import cv2
from bs4 import BeautifulSoup

#metadata attributes:
NomGroundSpeed = 0
inputfilesazpts = 0
RngbinsToProcess = 0
numLooks = 0
indatatype = 0
outdatatype = 0

nomAzRes = 0
DoppBandProc = 0
NearSlntRng = 0
FarSlntRng = 0
RngsmplstoProc = 0

coords = []

ns = 0
absvelocity = []
alti = []
Q = []
dt = []

timeStamp = ""
comment = ""
Mbyts = 0
seconds = 0
prf = 0
nPulses = 0
sampleRate = 0
numSamplesPerPri = 0
numPri = 0
startInd = 0
endInd = 0

dimensions = 0
course = 0
switch = 0
dynamicRange = 0


#opening cmd file
f = open('./18_11_21_09_57_00/18_11_21_10_04_13.cmd',)
for line in f:
    i = line.find("=>")
    if ("NomGroundSpeed" in line):
        NomGroundSpeed = float(line[i+2:])
    elif ("InputFileAzPts" in line):
        inputfilesazpts = int(line[i+2:])
    elif ("RngBinsToProcess" in line):
        RngbinsToProcess = int(line[i+2:])
    elif ("NumLooks" in line):
        numLooks = int(line[i+2:])
    elif ("InputDataType" in line):
        indatatype = int(line[i+2:])
    elif ("OutputDataType" in line):
        outdatatype = int(line[i+2:])

#print(NomGroundSpeed, inputfilesazpts, RngbinsToProcess, numLooks, indatatype, outdatatype)

f.close()

f = open('./18_11_21_09_57_00/18_11_21_10_04_13.log',)
log = f.read()
for line in log.split("\n"):
    i = line.find(":")
    if ('Nominal azimuth resolution' in line):
        nomAzRes = line[i+2:]
    if ('Doppler bandwidth processed' in line):   
        DoppBandProc = line[i+2:]
    if ('Processed near slant range' in line):
        NearSlntRng = line[i+2:]
    if ('Processed far slant range' in line):
        FarSlntRng = line[i+2:]
    if ('Range samples to process' in line):
        RngsmplstoProc = line[i+2:]

f.close()

#print(nomAzRes, DoppBandProc, NearSlntRng, FarSlntRng, RngsmplstoProc)

# Opening JSON file 
f = open('./18_11_21_09_57_00/18_11_21_10_04_14.json',) 

jsondata = [] 
# Iterating through the json 
# list 
for line in f: 
    jsondata.append(json.loads(line))
# Closing file 
f.close()

for i in range(len(jsondata)):
    ns = jsondata[0]['ns']
    Q.append(jsondata[i]['Q'])
    absvelocity.append(jsondata[i]['abs_vel'])
    alti.append(jsondata[i]['alt'])
    dt.append(jsondata[i]['dt'])

#opening geoJSON file
f = open('./18_11_21_09_57_00/18_11_21_10_04_13.geojson',)

for line in f:
    coords = (json.loads(line)['coordinates'])
f.close()


#reading from summary.ini
read_config = configparser.ConfigParser()
read_config.read('./18_11_21_09_57_00/summary.ini')

timeStamp = read_config.get("general","time_stamp")
comment = read_config.get("general","operator_comment")
Mbyts = int(read_config.get("dataset","bytes"))/1000
seconds = int(read_config.get("dataset","n_seconds"))
prf = int(read_config.get("dataset","prf"))
nPulses = int(read_config.get("dataset","n_pulses"))
sampleRate = float(read_config.get("dataset","sampling_rate"))

numSamplesPerPri = int(read_config.get("integration","n_samples_per_pri"))
numPri = int(read_config.get("integration","n_pris"))
startInd = int(read_config.get("integration","start_index"))
endInd = int(read_config.get("integration","end_index"))

#reading PNG files
# img = cv2.imread('./18_11_21_09_57_00/18_11_21_10_04_13.noco')
# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

#reading bin file
binFile = np.fromfile('./18_11_21_09_57_00/image.bin', dtype='complex64')  
#print(binFile)


#reading txt file
f = open('./18_11_21_09_57_00/18_11_21_10_04_13.txt', 'r')
html_doc = f.read()

soup = BeautifulSoup(html_doc, 'html.parser')
i=0
for line in soup.get_text().split("\n"):
    i = line.find(":")
    if (line[:i] == 'Dimensions'):
        dimensions = line[i+2:]
    if (line[:i] == 'Course'):   
        course = line[i+2:]
    if (line[:i] == 'Switch'):
        switch = line[i+2:]
    if (line[:i] == 'Dynamic Range'):
        dynamicRange = line[i+2:]
f.close()


#create hdf5 file
file = h5py.File ('file1.h5','w')
group = file.create_group('MyGroup')
image = group.create_dataset("bin",data=binFile)  

#attributes being assigned to the image
image.attrs['CLASS'] = 'IMAGE'
image.attrs['TIMESTAMP'] = timeStamp
image.attrs['NUMBER OF SATELLITES'] = ns
image.attrs['VELOCITY'] = absvelocity
image.attrs['ALTITUDE'] = alti
image.attrs['Q POINTS'] = Q
image.attrs['TIME STEPS'] = dt
image.attrs['CO-ORDINATES'] = coords
image.attrs['COMMENTS'] = comment
image.attrs['SECONDS'] = seconds
image.attrs['PRF'] = prf
image.attrs['NUMBER OF PULSES'] = nPulses
image.attrs['SAMPLE RATE'] = sampleRate
image.attrs['SAMPLES PER PRI'] = numSamplesPerPri
image.attrs["NUMBER OF PRI'S"] = numPri
image.attrs['START INDEX'] = startInd
image.attrs['END INDEX'] = endInd
image.attrs['DIMENSIONS'] = dimensions
image.attrs['COURSE'] = course
image.attrs['SWITCH'] = switch
image.attrs['DYNAMIC RANGE'] = dynamicRange
image.attrs['NOMINAL GROUND SPEED'] = NomGroundSpeed

image.attrs['MEGABYTES'] = Mbyts
image.attrs['INPUT FILE AZIMUTH POINTS'] = inputfilesazpts
image.attrs['RANGE BINS TO PROCESS'] = RngbinsToProcess
image.attrs['NUMLOOKS'] = numLooks
image.attrs['INPUT DATA TYPE'] = indatatype
image.attrs['OUTPUT DATA TYPE'] = outdatatype
image.attrs['NOMINAL AZIMUTH RESOLUTION'] = nomAzRes
image.attrs['DOPPLER BANDWIDTH PROCESSED'] = DoppBandProc
image.attrs['NEAR SLANT RANGE'] = NearSlntRng
image.attrs['FAR SLANT RANGE'] = FarSlntRng
image.attrs['RANGE SAMPLES TO PROCESS'] = RngsmplstoProc

file.close()