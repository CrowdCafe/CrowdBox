__author__ = 'pavelk'
import numpy
from PIL import Image, ImageDraw

import requests
from StringIO import StringIO
import logging
import pyexiv2
from random import randint
import os

log = logging.getLogger(__name__)

def maskImage(original_image, mask_points):

    # read image as RGB and add alpha (transparency)
    im = original_image.convert("RGBA")
    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)
    # create mask
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    #polygon_points = self.polygon.offset(settings.MARBLE_3D_ENLARGE_POLYGON)

    ImageDraw.Draw(maskIm).polygon(mask_points, outline=1, fill=1)
    mask = numpy.array(maskIm)
    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape,dtype='uint8')
    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]
    #transparency (4th column)
    newImArray[:,:,3] = mask*255
    # back to Image from numpy
    result_image = Image.fromarray(newImArray, "RGBA") #RGBA
    return result_image

def placeMaskOnBackground(original_image, color = (0,255,0)):
    bg = Image.new("RGB", original_image.size, color)
    bg.paste(original_image,original_image)
    return bg

def bufferImage(original_image, format="JPEG"):
    buffer = StringIO()
    original_image.save(buffer, format)
    return buffer

def getImageViaUrl(url):
	response = requests.get(url)
	return Image.open(StringIO(response.content))

def copyExifData(media_root, image_from,image_to):
    filepath_from = getRandomImageName()
    filepath_to = getRandomImageName()

    image_from.save(filepath_from)
    image_to.save(filepath_to)

    filepath_from = os.path.join( media_root, filepath_from )
    filepath_to   = os.path.join( media_root, filepath_to )

    m1 = pyexiv2.ImageMetadata(filepath_from)
    m1.read()
    m1.modified = True # not sure what this is good for
    m2 = pyexiv2.metadata.ImageMetadata(filepath_to)
    m2.read() # yes, we need to read the old stuff before we can overwrite it
    m1.copy( m2 )
    m2.write()

    return filepath_to
def getRandomImageName():
    str(randint(10000,99999))+'.jpeg'