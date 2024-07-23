import numpy as np
import ezdxf
from src.entityClass import Pier, GroundLine
import geopandas as gpd
from shapely.geometry import Polygon

def calculate_polygon_area(coords):
    n = len(coords)
    area = 0

    j = n - 1
    for i in range(0, n):
        area += (coords[j][0] + coords[i][0]) * (coords[j][1] - coords[i][1])
        j = i

    return abs(area / 2)

def dataLoad(dataPath, config) :
    data = ezdxf.readfile(dataPath)
    msp = data.modelspace()
    pierList = []
    ground = None
    floodY = 0
    for e in msp:
        if e.dxf.layer == config['pierLayerName']:
            li = []
            for i in e:
                li.append(i)
            li = np.array(li)[:, :2]
            p = Pier(li)
            pierList.append(p)
        if e.dxf.layer == config['floodLayerName']:
            for j in e:
                floodY = j[1]
        if e.dxf.layer == config['groundLayerName']:
            li = []
            for i in e:
                li.append(i)
            li = np.array(li)[:, :2]
            ground = GroundLine(li)
    for p in pierList:
        p.fitFlood(floodY)
    ground.fit(floodY)
    for p in pierList:
        p.fitGround(ground)
    return ground, floodY, pierList

def saveData(ground, pierList, config):
    # ground
    names = []
    geometries = []
    areas = []
    groundData = ground.data.tolist()
    groundArea = calculate_polygon_area(groundData)
    groundData.append(groundData[0])
    groundPoly = Polygon(groundData)
    names.append(config['groundOutputName'])
    geometries.append(groundPoly)
    areas.append(groundArea)

    # pier
    for pier in pierList:
        pierData = pier.data.tolist()
        pierArea = calculate_polygon_area(pierData)
        pierData.append(pierData[0])
        pierPoly = Polygon(pierData)
        names.append(config['pierOutputName'])
        geometries.append(pierPoly)
        areas.append(pierArea)

    gdf = gpd.GeoDataFrame(
        {'name': names, 'area': areas, 'geometry': geometries},
        crs="EPSG:4326"
    )

    gdf.to_file(config['outputFileName'], driver='GeoJSON')

class FileError(Exception):
    def __init__(self, message):
        super(FileError, self).__init__(message)
        self.message = message
    def __str__(self):
        return self.message