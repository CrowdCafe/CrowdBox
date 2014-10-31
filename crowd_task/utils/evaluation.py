__author__ = 'pavelk'


import logging
log = logging.getLogger(__name__)

import json
from django.conf import settings
from coordinates import getRectangleCoordinates, getPolygonPoints, getCanvasSize
from polygons import Polygon, Edge
import itertools
from crowd_io.image_pro import getExifDictionary

class CanvasPolygon:
    def __init__(self, data):
        self.data = data
        # self.polygon
        # self.canvas
        if self.isValid():
            shapes = json.loads(self.data['_shapes'])
            for shape in shapes['objects']:
                if shape['type'] == 'image':
                    self.canvas = getCanvasSize(shape)
                if shape['type'] == 'rect':
                    self.polygon = Polygon(getRectangleCoordinates(shape))
                if shape['type'] == 'polygon':
                    self.polygon = Polygon(getPolygonPoints(shape))
    def orient(self,original_image):
        exif = getExifDictionary(original_image)
        log.debug('exif data of the image is: %s',exif)
        orientation = exif['Orientation']
        # get orientation from EXIF data of the image
        log.debug('orientation is: %s',orientation)
        
        # orientation: 
        #   1 - top left (nothing),
        #   6 - top right (270), 
        #   3 - bottom left (180)
        #   8 - bottom right (90)

        if orientation == 1:
            self.polygon.points = self.polygon.points
        elif orientation == 6:
            self.polygon.points = [{'x':p['x'],'y':self.canvas['width']-p['y']} for p in self.polygon.points]
        elif orientation == 3:
            self.polygon.points = [{'x':self.canvas['width']-p['x'],'y':self.canvas['height']-p['y']} for p in self.polygon.points]
        elif orientation == 8:
            self.polygon.points = [{'x':self.canvas['height']-p['y'],'y':p['x']} for p in self.polygon.points]
    def isValid(self):
        if '_shapes' in self.data:
            return True
        else:
            return False

def findAgreement(judgements):
    # if judgements are 2 and more, else do nothing
    if len(judgements) > 1:
        # get all the possible combinations of existing judgements
        pairs = list(itertools.combinations(judgements, 2))
        # search similar pairs of similar judgements:
        for pair in pairs:
            canvaspolygons = [CanvasPolygon(pair[0].output_data),CanvasPolygon(pair[1].output_data)]
            test = CanvasPolygonSimilarity(canvaspolygons)
            if test.areSimilar():
                # return 2 judgements which are similar to each other (agreement)
                return pair
    return None

class CanvasPolygonSimilarity:
    def __init__(self, canvaspolygons):
        # we expect to have 2 canvaspolygons
        self.canvaspolygons = canvaspolygons
        self.threashold = settings.MARBLE_3D_ERROR_THREASHOLD

    def areSimilar(self):
        # bring polygons to one scale:
        for canvaspolygon in self.canvaspolygons:
            log.debug('polygon points: %s',canvaspolygon.polygon.points)
            log.debug('canvas info: %s',canvaspolygon.canvas)
            width = 800
            height = 600
            canvaspolygon.polygon.scale(1.0 * width / canvaspolygon.canvas['width'], 1.0 * height / canvaspolygon.canvas['height'])
            log.debug('polygon points: %s',canvaspolygon.polygon.points)
            log.debug('canvas info: %s',canvaspolygon.canvas)
        # check if their Perimetr, Area and Center are similar
        if self.haveSimilarPerimetr() and self.haveSimilarArea() and self.haveSimilarCenter():
            return True
        else:
            return False

    def haveSimilarPerimetr(self):
        perimeters = [cp.polygon.getPerimeter() for cp in self.canvaspolygons]
        divergence = self.getDivergence(perimeters)
        log.debug('perimetr divergence, %s , threashold is, %s', divergence,self.threashold['perimetr'] )

        return float(divergence) <= float(self.threashold['perimetr'])

    def haveSimilarArea(self):
        areas = [cp.polygon.getArea() for cp in self.canvaspolygons]
        divergence = self.getDivergence(areas)
        log.debug('area divergence, %s , threashold is, %s', divergence,self.threashold['area'] )

        return float(divergence) <= float(self.threashold['area'])

    def haveSimilarCenter(self):
        centers = [self.getDistanceToCenter(cp.polygon.getCenter()) for cp in self.canvaspolygons]
        divergence = self.getDivergence(centers)
        log.debug('center divergence, %s , threashold is, %s', divergence,self.threashold['center'] )

        return float(divergence) <= float(self.threashold['center'])

    def getDistanceToCenter(self, center_dot):
        edge = Edge({'x':0,'y':0},center_dot)
        return edge.getLength()

    def getDivergence(self, arr):
        arr = [float(el) for el in arr]
        return (max(arr) - min(arr)) / min(arr)


