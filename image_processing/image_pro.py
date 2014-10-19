__author__ = 'pavelk'
import numpy
from PIL import Image, ImageDraw

import requests
from StringIO import StringIO
import logging

log = logging.getLogger(__name__)

def cropByPolygon(original_image, polygon_points):

    # read image as RGB and add alpha (transparency)
    im = original_image.convert("RGBA")
    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)
    # create mask
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    #polygon_points = self.polygon.offset(settings.MARBLE_3D_ENLARGE_POLYGON)

    ImageDraw.Draw(maskIm).polygon(polygon_points, outline=1, fill=1)
    mask = numpy.array(maskIm)
    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape,dtype='uint8')
    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]
    #transparency (4th column)
    newImArray[:,:,3] = mask*255

    # back to Image from numpy
    result_image = Image.fromarray(newImArray, "RGBA") #RGBA
    # Crop the image
    '''
    corners = self.polygon.getCorners()
    self.image = self.image.crop((corners[0]['x'], corners[0]['y'], corners[1]['x'], corners[1]['y']))
    # Create an image with green background and place image on it
    bg = Image.new("RGB", self.image.size, (0,255,0))
    bg.paste(self.image,self.image)
    self.image = bg
    '''
    buffer = StringIO()
    result_image.save(buffer, "JPEG")
    return buffer

def getImageViaUrl(url):
	response = requests.get(url)
	return Image.open(StringIO(response.content))