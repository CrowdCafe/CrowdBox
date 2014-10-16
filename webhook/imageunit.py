from crowdcafe_client.client import CrowdCafeAPI
from marble3d.utils import getFileViaUrl
from django.conf import settings

import logging
import numpy

log = logging.getLogger(__name__)

from PIL import Image, ImageDraw



class CrowdBoxImage:
    def __init__(self, dropboxfile):
        self.dropboxfile = dropboxfile
        self.job_id = settings.CROWDCAFE['job_id']
        self.crowdcafe_client = CrowdCafeAPI()

    def checkFilenameStatus(self):
        statuses = ('inprocess','completed')
        for status in statuses:
            if status+'_' in self.dropboxfile.getFilename():
                return status
        return False
    def checkFilenameUnitId(self):
        filename = self.dropboxfile.getFilename()
        UnitIdKeyword = 'CCunitid'

        if UnitIdKeyword in filename:
            unitid_with_filename = filename[filename.rfind(UnitIdKeyword)+len(UnitIdKeyword):len(filename)]
            log.debug(unitid_with_filename)
            unit_id = int(unitid_with_filename[:unitid_with_filename.lfind('_')])
            log.debug(unit_id)
            return unit_id
        log.debug(UnitIdKeyword+' is not in the '+filename)
        return False

    def unpublishCrowdCafeUnit(self, unit_id):

        return False
    def createCrowdCafeUnit(self):
        new_unit_response = self.crowdcafe_client.createUnit(self.job_id, {'blank':'yes'})

        unit = new_unit_response.json()
        # rename file
        new_filename = 'inprocess_CCunitid'+str(unit['pk'])+'_'+self.dropboxfile.getFilename()
        self.dropboxfile.rename(new_filename)

        #TODO add url to the image
        unit_new_data = {
            'uid':self.dropboxfile.client.getUid(),
            'path':self.dropboxfile.getPath(),
            'image_filename':self.dropboxfile.getFilename(),
            'block_title':self.dropboxfile.getRoot()
        }
        unit['input_data'] = unit_new_data
        self.crowdcafe_client.updateUnit(self.job_id,unit)
'''
class ImageUnit:
    def __init__(self, dropbox_user):
        self.dropbox_user = dropbox_user
        self.job_id = 8
        self.rockpearl_url = 'http://crowdcrop.crowdcafe.io/'



    def makeCroppedImage(self, original_image, judgement):
        # read image as RGB and add alpha (transparency)
        im = original_image.convert("RGBA")  # imagefile.convert("RGBA")
        # convert to numpy (for convenience)
        imArray = numpy.asarray(im)
        # create mask
        maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
        # polygon_points = self.polygon.offset(settings.MARBLE_3D_ENLARGE_POLYGON)
        polygon_points = judgement.polygon.getSequence()
        log.debug(polygon_points)

        ImageDraw.Draw(maskIm).polygon(polygon_points, outline=1, fill=1)
        mask = numpy.array(maskIm)
        # assemble new image (uint8: 0-255)
        newImArray = numpy.empty(imArray.shape, dtype='uint8')
        # colors (three first columns, RGB)
        newImArray[:, :, :3] = imArray[:, :, :3]
        # transparency (4th column)
        newImArray[:, :, 3] = mask * 255


        # back to Image from numpy
        cropped_image = Image.fromarray(newImArray, "RGBA")  # RGBA
        # Crop the image
        corners = judgement.polygon.getCorners()
        cropped_image = cropped_image.crop((corners[0]['x'], corners[0]['y'], corners[1]['x'], corners[1]['y']))
        # Create an image with green background and place image on it
        bg = Image.new("RGB", cropped_image.size, (0, 255, 0))
        bg.paste(cropped_image, cropped_image)
        return bg

    def uploadCroppedImage(self, cropped_image, path):
        return self.dropbox_user.uploadFile(cropped_image, path, 'JPEG')

    def getOriginalImage(self, input_data):
        return getFileViaUrl(input_data['url'])



    def getUnitIdByPath(self, path):
        key = 'inprogress_'
        filename = path[path.rfind('/') + 1:len(path)]
        if key in filename:
            filename_left = filename[len(key), len(filename)]
            return int(filename_left[0:filename_left.lfind('_')])
        else:
            return None

'''
