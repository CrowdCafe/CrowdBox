from crowdcafe_client.client import CrowdCafeAPI
from crowdcafe_client.sdk import Unit
from marble3d.utils import getFileViaUrl
from django.conf import settings
import datetime

import logging
import numpy

log = logging.getLogger(__name__)

from PIL import Image, ImageDraw


class CrowdBoxImage:
    def __init__(self, dropboxfile):
        self.dropboxfile = dropboxfile
        self.unit = Unit(job_id = settings.CROWDCAFE['job_id'])

        # self.crowdcafe_client = CrowdCafeAPI()
    # ---------------------------------------------------------
    # Dropbox related methods
    def checkFilenameStatus(self):
        statuses = ('inprocess','completed')
        for status in statuses:
            if status+'_' in self.dropboxfile.getFilename():
                log.debug(status)
                return status
        return False
    def processUpdateFromDropbox(self):
        # if it was deleted from dropbox
        if self.dropboxfile.isDeleted():
            unit_id = self.checkFilenameUnitId()
            # if we can identify unit_id - then unpublish it from CrowdCafe
            if unit_id:
                self.unit.pk = unit_id
                self.unit.get()
                self.unit.published = False
                self.unit.deleted = datetime.datetime.now()
                self.unit.save()
        else:
            # if the file already was processed and has status in its name
            if self.checkFilenameStatus():
                log.debug(self.checkFilenameUnitId)
            # if file was not processed - create new unit in CrowdCafe
            else:
                self.createUnit()
    def checkFilenameUnitId(self):
        filename = self.dropboxfile.getFilename()
        UnitIdKeyword = 'ccunitid'

        if UnitIdKeyword in filename:
            unitid_with_filename = filename[filename.rfind(UnitIdKeyword)+len(UnitIdKeyword):len(filename)]
            log.debug(unitid_with_filename)
            unit_id = int(unitid_with_filename[:unitid_with_filename.find('_')])
            log.debug(unit_id)
            return unit_id
        log.debug(UnitIdKeyword+' is not in the '+filename)
        return False
    # ---------------------------------------------------------
    # CrowdCafe related methods

    def createUnit(self):
        new_unit_response = self.unit.create({'blank':'yes'})

        # rename file
        new_filename = 'inprocess_CCunitid'+str(self.unit.pk)+'_'+self.dropboxfile.getFilename()
        self.dropboxfile.rename(new_filename)

        #TODO add url to the image
        unit_new_data = {
            'uid':self.dropboxfile.client.getUid(),
            'path':self.dropboxfile.getPath(),
            'image_filename':self.dropboxfile.getFilename(),
            'block_title':self.dropboxfile.getRoot()
        }
        self.unit.input_data = unit_new_data
        self.unit.save()
    # ---------------------------------------------------------
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
