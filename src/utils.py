import numpy as np
import ezdxf
from src.entityClass import Pier, GroundLine
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

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
    tmp = []
    for p in pierList:
        p.fitFlood(floodY)
        if(p.data != []):
            tmp.append(p)
    pierList = tmp
    ground.fit(floodY)
    tmp = []
    for p in pierList:
        aa = p.fitGround(ground)
        if(aa != False):
            tmp.append(p)
    pierList = tmp
    return ground, floodY, pierList

def saveData(ground, pierList, config):
    # ground
    names = []
    geometries = []
    areas = []
    types = []
    groundData = ground.data.tolist()
    groundArea = calculate_polygon_area(groundData)
    groundData.append(groundData[0])
    groundPoly = Polygon(groundData)
    names.append(config['groundOutputName'])
    geometries.append(groundPoly)
    areas.append(groundArea)
    types.append(config['groundType'])

    for pier in pierList:
        if pier.is_main == False:
            continue
        for pier2 in pierList:
            if pier == pier2:
                continue
            if pier2.is_main == False:
                continue
            if pier.xMin <= pier2.xMin and pier.xMax >= pier2.xMax and pier.yMin <= pier2.yMin and pier.yMax >= pier2.yMax:
                pier.fittings.append(pier2)
                pier2.is_main = False

    # pier
    k = 0
    kk = 0
    for pier in pierList:
        pierData = pier.data.tolist()
        if pier.is_main == True:
            k += 1
            pierArea = calculate_polygon_area(pierData)
            for hole in pier.fittings:
                pierArea -= calculate_polygon_area(hole.data.tolist())
            names.append(config['pierOutputName'] + str(k))
        else:
            kk += 1
            pierArea = calculate_polygon_area(pierData)
            names.append(config['holeOutputName'] + str(kk))
        pierData.append(pierData[0])
        pierPoly = Polygon(pierData)
        geometries.append(pierPoly)
        areas.append(pierArea)
        types.append(config['pierType'])

    gdf = gpd.GeoDataFrame(
        {'name': names, 'type': types, 'area': areas, 'geometry': geometries},
        crs="EPSG:3857"
    )

    gdf.to_file(config['outputFileName'], driver='GeoJSON')
    file = open(config['outputFileName'], 'r')
    content = file.read()
    file.close()
    newContent = content.replace('Polygon', 'Polyline')
    file = open(config['outputFileName'], 'w')
    file.write(newContent)
    file.close()
    gdf.boundary.plot(edgecolor='black', aspect=1)
    plt.show()

def changeCoordinate(pierList, ground):
    xMin = ground.xMin
    yMin = ground.yMin
    for pier in pierList:
        xMin = min(pier.xMin, xMin)
        yMin = min(pier.yMin, yMin)
    ground.data[:, 0] -= xMin
    ground.data[:, 1] -= yMin
    for pier in pierList:
        pier.data[:, 0] -= xMin
        pier.data[:, 1] -= yMin
    return pierList, ground

class FileError(Exception):
    def __init__(self, message):
        super(FileError, self).__init__(message)
        self.message = message
    def __str__(self):
        return self.message