from flask import Flask, render_template, request, jsonify, json 
import h5py
import numpy as np
import cv2
import folium
from ee_demo import generate_map, generate_map_2
import os, glob
from process_to_image import generatePNG, processPNG
from skimage import io, img_as_float
from skimage.filters import gaussian
import matplotlib.pyplot as plt

names = []
im = []
coords = []
attribsList = []
values = []
drs = []
dimensionslist = []
pulseslist = []
rangebinslist = []
timesteps = []
velocities = []
altitudes = []
Qs = []
times = []
courses = []

folder_path = './datafiles'
for filename in glob.glob(os.path.join(folder_path, '*.h5')):
  with h5py.File (filename,'r') as file:
    binaryFile = np.array(file['/MyGroup/bin']).astype('complex64')
    image_atribs = file['/MyGroup/bin'].attrs
    im.append(binaryFile)
    attribsList.append(list(image_atribs.keys()))
    values.append(list(image_atribs.values()))
    coords.append(image_atribs.get('CO-ORDINATES'))
    name = image_atribs.get('TIMESTAMP')
    names.append(name)

    dt = image_atribs.get("TIME STEPS")
    timesteps.append(dt)
    vel = image_atribs.get("VELOCITY")
    velocities.append(vel)
    alt = image_atribs.get("ALTITUDE")
    altitudes.append(alt)
    Q = image_atribs.get("Q POINTS")
    Qs.append(Q)

    dr = image_atribs.get('DYNAMIC RANGE').split(":")
    dr = list(map(int, dr))
    drs.append(dr)
    dimensions = image_atribs.get('DIMENSIONS').split("x")
    dimensions = list(map(float, dimensions))
    dimensionslist.append(dimensions)
    pulses = int(image_atribs.get('NUMBER OF PULSES'))
    pulseslist.append(pulses)
    rangebins = int(image_atribs.get('RANGE BINS TO PROCESS'))
    rangebinslist.append(rangebins)
    course = float(image_atribs.get('COURSE'))
    courses.append(course)

    count = 0
    time = np.zeros(len(dt))
    for i in range(len(dt)):
        count = count+dt[i]
        time[i] = count
    times.append(time)
    #generatePNG(binaryFile, name, rangebins, pulses, dimensions[0], dimensions[1], dr, course)  #run through the file and generate the image.
file.close()

rg_axis = 0 #global
az_axis = 0
procimage = []
dataset_name = ""

app = Flask(__name__)

@app.route('/') #the main page
def template_test():
    return render_template(
        'template.html', my_map= './static/ProcessedImage.png.html', key_list=attribsList, val_list=values,
        title="Home", names=names, first=names[0])


@app.route("/compare")
def compare():
    i = names.index(dataset_name)
    nrows = rangebinslist[i]  # [bins]
    ncols = pulseslist[i] # [bins]

    rng = dimensionslist[i][1] # [m]
    azi = dimensionslist[i][0] # [m]

    dr = drs[i]

    global rg_axis
    rg_axis = np.linspace(0, rng, nrows, endpoint=False)
    global az_axis
    az_axis = np.linspace(0, azi, ncols, endpoint=False)

    image = np.flipud(np.reshape(im[i], (nrows, ncols)))  #processing image 
    image = 20*np.log10(abs(image))
    image += 30*np.log10(rg_axis)[:, np.newaxis]
    image -= np.amax(image)
    image = np.clip(image, dr[0], dr[-1])
    global procimage 
    procimage = image

    axis_0_init, axis_1_init = np.unravel_index(procimage.argmax(), procimage.shape)

    return render_template(
        'chartjs.html', image='./static/'+dataset_name+'.png',
         rngy=rg_axis.tolist(), rngx=procimage[:, axis_1_init].tolist(), 
         azx=az_axis.tolist(), azy=procimage[axis_0_init].tolist())

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/graphs")
def graphs():
    i = names.index(dataset_name)
    velocity = velocities[i]
    altitude = altitudes[i]
    qflag = Qs[i]
    time = times[i]

    return render_template('graphs.html', vel=velocity.tolist(), alt=altitude.tolist(), q=qflag.tolist(), time=time.tolist())

@app.route("/gen2maps")
def gen2maps():
    set1 = request.args.get('set1', None)
    set2 = request.args.get('set2', None)
    i = names.index(set1)
    j = names.index(set2)
    generate_map_2([coords[i][0][1], coords[i][0][0]], [coords[i][1][1], coords[i][1][0]], set1+"new.png", [coords[j][0][1], coords[j][0][0]], [coords[j][1][1], coords[j][1][0]], set2+"new.png")
    return "True"

@app.route("/backgroundreload")
def update():
    global dataset_name
    dataset_name = request.args.get('datasetname', None)
    i = names.index(dataset_name)
    generate_map([coords[i][0][1], coords[i][0][0]], [coords[i][1][1], coords[i][1][0]], dataset_name+"new.png")
    return "True"

@app.route("/processCommand")
def processcommand():
    inputfunction = request.args.get('command', None)
    print(inputfunction)
    params = request.args.get('parameters', None)
    print(params)
    selected = request.args.get('selected', None)
    print(selected)
    i = names.index(selected)

    if inputfunction == "setColourMap":
        processPNG(im[i], names[i], rangebinslist[i], pulseslist[i], dimensionslist[i][0], dimensionslist[i][1], drs[i], params, courses[i])
    elif inputfunction == "gaussian":
        gaus_img = (io.imread("./static/"+ names[i] + "new.png", as_gray=True))
        skimage_gaussian = gaussian(gaus_img, sigma=int(params), mode='constant', cval= 0.0)

        plt.imsave(
                fname = "./static/"+names[i]+'new.png',
                arr = skimage_gaussian, 
                cmap = plt.cm.gray,
                dpi = 100
            )
        print("gaussian image saved.")
    elif inputfunction == "changeDR":
        params = params.split(",")
        params = list(map(int, params))
        print(params)
        generatePNG(im[i], names[i], rangebinslist[i], pulseslist[i], dimensionslist[i][0], dimensionslist[i][1], params, courses[i])
    elif inputfunction == "originalImage":
        generatePNG(im[i], names[i], rangebinslist[i], pulseslist[i], dimensionslist[i][0], dimensionslist[i][1], drs[i], courses[i])

    return "True"

@app.route("/updateGraphs")
def updateGraphs():
    x = request.args.get('x', None)
    y = request.args.get('y', None)
    
    x_indx = find_nearest_index(az_axis, float(x)/800*1750)
    y_indx = find_nearest_index(rg_axis, float(y)/253*700)
    xlist = procimage[:, x_indx].tolist()
    ylist = procimage[y_indx].tolist() 
    joined_list = [xlist,ylist]
    
    firstresponse = app.response_class(
        response = json.dumps(joined_list),
        status=200,
        mimetype='application/json'
    )
    return firstresponse

def find_nearest_index(array, value):
    """
    Returns the index of the element, in the array, closest to the given value.
    """
    array = np.asarray(array)
    # print(value, (np.abs(array - (value))).argmin())
    return (np.abs(array - (value))).argmin()

if __name__ == '__main__':
    app.run(debug=True)
