import numpy as np
import cv2
import matplotlib.pyplot as plt
import skimage.io
import h5py
from PIL import Image

def image_scaler(image_path, width, height):
    image = Image.open("./static/"+image_path+".png")
    image.load()
    image = image.resize((int(width), int(height)), resample=Image.LANCZOS)
    image.save("./static/"+image_path+"new.png")

def image_rotator(image_path, angle):
    image = Image.open(image_path)
    image.load()
    image = image.rotate(angle, expand=True)
    image.save(image_path)



def processPNG(im, name, nrows, ncols, azi, rng, dr, color, angle):

    image = []
    rg_axis = np.linspace(0, rng, nrows, endpoint=False)
    az_axis = np.linspace(0, azi, ncols, endpoint=False)

    image = np.flipud(np.reshape(im, (nrows, ncols)))
    image = 20*np.log10(abs(image))
    image += 30*np.log10(rg_axis)[:, np.newaxis]
    image -= np.amax(image)
    image = np.clip(image, dr[0], dr[-1])
    image = np.flipud(image)

    plt.imsave(
                fname = "./static/"+name+'.png',
                arr = image, 
                cmap=plt.cm.get_cmap(color),
                dpi = 100
            )

    image_scaler(name, azi, rng)
    image_rotator("./static/"+name+'new.png', (90 + angle))
    return image

def generatePNG(im, name, nrows, ncols, azi, rng, dr, angle):

    image = []
    rg_axis = np.linspace(0, rng, nrows, endpoint=False)
    az_axis = np.linspace(0, azi, ncols, endpoint=False)

    image = np.flipud(np.reshape(im, (nrows, ncols)))
    image = 20*np.log10(abs(image))
    image += 30*np.log10(rg_axis)[:, np.newaxis]
    image -= np.amax(image)
    image = np.clip(image, dr[0], dr[-1])
    image = np.flipud(image)    

    plt.imsave(
                fname = "./static/"+name+'.png',
                arr = image, 
                dpi = 100
            )

    image_scaler(name, azi, rng)
    image_rotator("./static/"+name+'new.png', (90 + angle))
    
    return image
