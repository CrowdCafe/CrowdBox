__author__ = 'pavelk'
# -*- coding: utf-8 -*-
import numpy
from PIL import Image, ImageDraw, ExifTags

import requests
from StringIO import StringIO
import logging
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

def copyExifData(media_root, image_from, image_to):
    filepath_to = getRandomImageName('to')
    filepath_to   = os.path.join( media_root, filepath_to )

    os.chmod(media_root,0777)
    exif = image_from.info['exif']

    image_to.save(filepath_to, 'JPEG', exif = exif)
    return filepath_to

def getRandomImageName(key):
    return key+'_'+str(randint(10000,99999))+'.jpeg'

# http://stackoverflow.com/questions/1606587/how-to-use-pil-to-resize-and-apply-rotation-exif-information-to-the-file

def orientImage(image):
    '''
    EXIF Orientations:
      1        2       3      4         5            6           7          8

    888888  888888      88  88      8888888888  88                  88  8888888888
    88          88      88  88      88  88      88  88          88  88      88  88
    8888      8888    8888  8888    88          8888888888  8888888888          88
    88          88      88  88
    88          88  888888  888888

    '''
    # We rotate regarding to the EXIF orientation information
    mirror = image.copy()

    exif = {
        ExifTags.TAGS[k]: v
        for k, v in image._getexif().items()
        if k in ExifTags.TAGS
    }

    log.debug('exif data %s',exif)
    if 'Exif.Image.Orientation' in image.info['exif']:
        orientation = image['Exif.Image.Orientation']
        if orientation == 1:
            # Nothing
            mirror = image.copy()
        elif orientation == 2:
            # Vertical Mirror
            mirror = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotation 180
            mirror = image.transpose(Image.ROTATE_180)
        elif orientation == 4:
            # Horizontal Mirror
            mirror = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            # Horizontal Mirror + Rotation 90 CCW
            mirror = image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_90)
        elif orientation == 6:
            # Rotation 270
            mirror = image.transpose(Image.ROTATE_270)
        elif orientation == 7:
            # Horizontal Mirror + Rotation 270
            mirror = image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
        elif orientation == 8:
            # Rotation 90
            mirror = image.transpose(Image.ROTATE_90)
    return mirror