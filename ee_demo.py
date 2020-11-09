import ee 
import folium
import numpy as np
import matplotlib.pyplot as plt
ee.Initialize()
def generate_map(top_left_lalo, bot_right_lalo, filename):

    #=====================================================================================================
    # Define a method for displaying Earth Engine image tiles to folium map.
    def add_ee_layer(self, ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name = name,
            overlay = True,
            control = True,
            show = False
        ).add_to(self)

    folium.Map.add_ee_layer = add_ee_layer
    #=====================================================================================================

    centre_lalo = [
        np.mean([top_left_lalo[0], bot_right_lalo[0]]),
        np.mean([top_left_lalo[1], bot_right_lalo[1]])
    ]

    dem = ee.Image("USGS/SRTMGL1_003")
    sentinel_1 = ee.ImageCollection("COPERNICUS/S1_GRD")
    map_centre = ee.Geometry.Point(lat=centre_lalo[0], lon=centre_lalo[1])

    region = map_centre.buffer(5000)

    S1 = sentinel_1 \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filterBounds(map_centre)

    dates = ee.Filter.date('2018-11-01', '2018-11-30')

    VV = S1.select('VV').filter(dates).mean().updateMask(dem.neq(0)).clip(region)
    VH = S1.select('VH').filter(dates).mean().updateMask(dem.neq(0)).clip(region)

    Map = folium.Map(location=[centre_lalo[0], centre_lalo[1]], zoom_start=13, tiles=None)

    folium.TileLayer(
        tiles='http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        zoom_start=13,
        min_zoom=0,
        max_zoom=17,
        attr='&copy; <a href="http://www.esri.com/">Esri</a>, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        name='Optical'
    ).add_to(Map)

    # Add the elevation model to the map object.
    Map.add_ee_layer(VV, {'min': -23, 'max': -4}, 'S-1 VV')
    Map.add_ee_layer(VH, {'min': -27, 'max': -12}, 'S-1 VH')

    folium.raster_layers.ImageOverlay(
        image='./static/'+filename,
        name='MS NA',
        bounds=[top_left_lalo, bot_right_lalo],
        opacity=0.9,
        colormap=lambda x: (1, 0, 0, x)
    ).add_to(Map)

    # Add a layer control panel to the map.
    Map.add_child(folium.LayerControl())

    Map.save("./static/ProcessedImage.png.html")



def generate_map_2(top_left_lalo1, bot_right_lalo1, filename1, top_left_lalo2, bot_right_lalo2, filename2):
    
    #=====================================================================================================
    # Define a method for displaying Earth Engine image tiles to folium map.
    def add_ee_layer(self, ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name = name,
            overlay = True,
            control = True,
            show = False
        ).add_to(self)

    folium.Map.add_ee_layer = add_ee_layer
    #=====================================================================================================

    centre_lalo1 = [
        np.mean([top_left_lalo1[0], bot_right_lalo1[0]]),
        np.mean([top_left_lalo1[1], bot_right_lalo1[1]])
    ]

    dem = ee.Image("USGS/SRTMGL1_003")
    sentinel_1 = ee.ImageCollection("COPERNICUS/S1_GRD")
    map_centre = ee.Geometry.Point(lat=centre_lalo1[0], lon=centre_lalo1[1])

    region = map_centre.buffer(5000)

    S1 = sentinel_1 \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filterBounds(map_centre)

    dates = ee.Filter.date('2018-11-01', '2018-11-30')

    VV = S1.select('VV').filter(dates).mean().updateMask(dem.neq(0)).clip(region)
    VH = S1.select('VH').filter(dates).mean().updateMask(dem.neq(0)).clip(region)

    Map = folium.Map(location=[centre_lalo1[0], centre_lalo1[1]], zoom_start=13, tiles=None)

    folium.TileLayer(
        tiles='http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        zoom_start=13,
        min_zoom=0,
        max_zoom=17,
        attr='&copy; <a href="http://www.esri.com/">Esri</a>, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        name='Optical'
    ).add_to(Map)

    # Add the elevation model to the map object.
    Map.add_ee_layer(VV, {'min': -23, 'max': -4}, 'S-1 VV')
    Map.add_ee_layer(VH, {'min': -27, 'max': -12}, 'S-1 VH')


    folium.raster_layers.ImageOverlay(
        image='./static/'+filename1,
        name='MS 1',
        bounds=[top_left_lalo1, bot_right_lalo1],
        opacity=0.9,
        colormap=lambda x: (1, 0, 0, x)
    ).add_to(Map)

    folium.raster_layers.ImageOverlay(
        image='./static/'+filename2,
        name='MS 2',
        bounds=[top_left_lalo2, bot_right_lalo2],
        opacity=0.9,
        colormap=lambda x: (1, 0, 0, x)
    ).add_to(Map)

    # Add a layer control panel to the map.
    Map.add_child(folium.LayerControl())

    Map.save("./static/ProcessedImage.png.html")