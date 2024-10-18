"""
Model exported as python.
Name : Сгенерировать XYZ тайлы и файл tiles.json
Group : Инструменты обработки растра 
With QGIS : 33603
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
import processing
import os
from PyQt5.QtGui import QColor
from PyQt5.Qt import *
from qgis.utils import iface
from qgis.core import (QgsCoordinateReferenceSystem, 
                        QgsCoordinateTransform, 
                        QgsProcessingParameterFolderDestination, 
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterString,
                        QgsProcessingParameterNumber)
from qgis.PyQt.QtWidgets import QDateTimeEdit

class GenerateTilesJson(QgsProcessingAlgorithm):


    def initAlgorithm(self, config=None):
        self.pathParameter = QgsProcessingParameterFolderDestination('FOLDER','Папка с картами')
        self.nameParameter = QgsProcessingParameterString('NAME','Название', defaultValue='MyMap')
        self.minZoomParameter = QgsProcessingParameterNumber('MINZOOM','Минимальный зум')
        self.maxZoomParameter = QgsProcessingParameterNumber('MAXZOOM','Максимальный зум', defaultValue=16)
        self.minZoomParameter.setMinimum(0)
        self.minZoomParameter.setMaximum(20)
        self.maxZoomParameter.setMinimum(0)
        self.maxZoomParameter.setMaximum(20)
        
        self.addParameter(self.nameParameter)
        self.addParameter(self.minZoomParameter)
        self.addParameter(self.maxZoomParameter)
        self.addParameter(self.pathParameter)
        

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        
        self.folder = self.parameterAsString(parameters,
                                             'FOLDER',
                                              context)
        self.name = self.parameterAsString(parameters,
                                             'NAME',
                                              context)
        self.minZoom = self.parameterAsInt(parameters,
                                             'MINZOOM',
                                              context)
        self.maxZoom = self.parameterAsInt(parameters,
                                             'MAXZOOM',
                                              context)  
        
        results = {}
        outputs = {}
        
        self.folder = self.folder + '\\' + self.name + '\\'
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.pathtomap = self.folder + '\\tiles.json'
        
        
        self.generate_tiles_info_json()
        

        #создаем новые тайлы
        processing.run("native:tilesxyzdirectory", 
        {'ANTIALIAS' : True, 
        'BACKGROUND_COLOR' : QColor(0, 0, 0, 0), 
        'DPI' : 96, 
        'EXTENT' : iface.mapCanvas().extent(), 
        'HTML_ATTRIBUTION' : '', 
        'HTML_OSM' : False, 
        'HTML_TITLE' : '', 
        'METATILESIZE' : 4, 
        'OUTPUT_DIRECTORY' : self.folder, 
        'OUTPUT_HTML' : 'TEMPORARY_OUTPUT', 
        'QUALITY' : 75, 
        'TILE_FORMAT' : 0, 
        'TILE_HEIGHT' : 256,
        'TILE_WIDTH' : 256, 
        'TMS_CONVENTION' : False, 
        'ZOOM_MAX' : self.maxZoom, 
        'ZOOM_MIN' : self.minZoom },
        context=context, feedback=model_feedback, is_child_algorithm=True)
        
        return results

    def name(self):
        return 'Сгенерировать XYZ тайлы и файл tiles.json'

    def displayName(self):
        return 'Сгенерировать XYZ тайлы и файл tiles.json'

    def group(self):
        return 'Инструменты обработки растра '

    def groupId(self):
        return 'RASTR'

    def createInstance(self):
        return GenerateTilesJson()

    #Создаем tiles.json файл
    def generate_tiles_info_json(self):
        canv = iface.mapCanvas()
        map_bound = canv.extent()
        center = canv.center()
        mercator = QgsCoordinateReferenceSystem("EPSG:3857")
        wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
        transformer = QgsCoordinateTransform(mercator, wgs84,0,1)

        map_bound_geo = transformer.transformBoundingBox(map_bound)
        center_geo = transformer.transform(center)

        map_bound_geo_xMax = map_bound_geo.xMaximum()
        map_bound_geo_yMax = map_bound_geo.yMaximum()
        map_bound_geo_xMin = map_bound_geo.xMinimum()
        map_bound_geo_yMin = map_bound_geo.yMinimum()

        center_geo_x = center_geo.x()
        center_geo_y = center_geo.y()
        

        string = '''{
            "tilejson":"1.0.0", 
            "name":"'''+ self.name +'''", 
            "description":"Made with QGis", 
            "attribution":"Map data © OpenStreetMap contributors", 
            "tiles":["tiles/{z}/{x}/{y}.png"], 
            "minzoom":'''+ self.minZoom.__str__() +''', 
            "maxzoom":'''+ self.maxZoom.__str__() +''', 
           "bounds":
            [
                '''+ map_bound_geo_xMax.__str__() +''', 
                '''+ map_bound_geo_yMax.__str__() +''', 
                '''+ map_bound_geo_xMin.__str__() +''', 
                '''+ map_bound_geo_yMin.__str__() +''', 
            ], 
            "center":
            [
                '''+ center_geo_x.__str__() +''',  
                '''+ center_geo_y.__str__() +''', 
                0
            ]
        }'''

        with open(self.pathtomap, "w") as outfile:
            outfile.write(string)