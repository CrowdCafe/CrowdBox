__author__ = 'pavelk'


import logging
log = logging.getLogger(__name__)

import json
from django.conf import settings
from crowdcafe_client.sdk import Judgement
from shapes.coordinates import getRectangleCoordinates, getPolygonPoints, getCanvasSize
from shapes.polygons import Polygon, Edge
import itertools

class CanvasPolygon:
    def __init__(self, judgement):
        self.data = judgement.output_data
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
        log.debug('canvaspolygon %s',self)
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
            canvaspolygons = [CanvasPolygon(pair[0]),CanvasPolygon(pair[1])]
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
            width = 800
            height = 600
            canvaspolygon.polygon.scale(1.0 * width / canvaspolygon.canvas['width'], 1.0 * height / canvaspolygon.canvas['height'])

        # check if their Perimetr, Area and Center are similar
        if self.haveSimilarPerimetr() and self.haveSimilarArea() and self.haveSimilarCenter():
            return True
        else:
            return False

    def haveSimilarPerimetr(self):
        perimeters = [cp.polygon.getPerimeter() for cp in self.canvaspolygons]
        divergence = self.getDivergence(perimeters)
        log.debug('perimetr divergence, %i', divergence)

        return float(divergence) <= float(self.threashold['perimetr'])

    def haveSimilarArea(self):
        areas = [cp.polygon.getArea() for cp in self.canvaspolygons]
        divergence = self.getDivergence(areas)
        log.debug('area divergence, %i', divergence)

        return float(divergence) <= float(self.threashold['area'])

    def haveSimilarCenter(self):
        centers = [self.getDistanceToCenter(cp.polygon.getCenter()) for cp in self.canvaspolygons]
        divergence = self.getDivergence(centers)
        log.debug('centers divergence, %i', divergence)

        return float(divergence) <= float(self.threashold['center'])

    def getDistanceToCenter(self, center_dot):
        edge = Edge({'x':0,'y':0},center_dot)
        return edge.getLength()

    def getDivergence(self, arr):
        arr = [float(el) for el in arr]
        return (max(arr) - min(arr)) / min(arr)


