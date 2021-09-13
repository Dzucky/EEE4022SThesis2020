# EEE4022SThesis2020
A web interface designed to parse, process and display SAR imagery. This was done for my Honours thesis at UCT.

Datafiles: contains the HDF5 data files used for the interface.

static: contains the images used.

Templates: contains the HTML templates used by the controller.

controller.py: Python framework of the web interface using Flask.

ee_demo.py: Contains functions related to google earth engine data used by the controller.py program.

hdf5.py: Program created to parse through the relevant data from an experiment and compile it into one HDF5 file. 

process_to_image.py: Contains functions that generate PNG files from SAR data. Used by controller.py
