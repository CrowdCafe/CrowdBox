from crowdcafe_client.client import CrowdCafeAPI
from marble3d.utils import getFileViaUrl
import logging
import numpy

log = logging.getLogger(__name__)

crowdcafe = CrowdCafeAPI()
from PIL import Image, ImageDraw


class ImageUnit:
    def __init__(self, dropbox_user):
        self.dropbox_user = dropbox_user
        self.job_id = 8
        self.rockpearl_url = 'http://crowdcrop.crowdcafe.io/'

    def getMediaURL(self, path):
        media = self.dropbox_user.getDirectLink(path)
        return media['url']

    def decideWhatToDo(self, path, metadata):
        filename = path[path.rfind('/') + 1:len(path)]
        rest_path = path[:path.rfind('/')]
        folder = rest_path[rest_path.rfind('/') + 1:len(rest_path)]
        if metadata and metadata['mime_type'] in ['image/jpeg', 'image/png']:
            if 'inprogress_' not in filename and 'completed_' not in filename:
                self.publishImage(path, metadata)
            else:
                unit_id = self.getUnitIdByPath(path)
                if unit_id:
                    self.unpublishImage()

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

    def unpublishImage(self, path, metadata):
        return False

    def getUnitIdByPath(self, path):
        key = 'inprogress_'
        filename = path[path.rfind('/') + 1:len(path)]
        if key in filename:
            filename_left = filename[len(key), len(filename)]
            return int(filename_left[0:filename_left.lfind('_')])
        else:
            return None

    def publishImage(self, path, metadata):
        filename = path[path.rfind('/') + 1:len(path)]
        rest_path = path[:path.rfind('/')]
        folder = rest_path[rest_path.rfind('/') + 1:len(rest_path)]

        if metadata and metadata['mime_type'] in ['image/jpeg','image/png'] and 'inprogress_' not in filename and 'completed_' not in filename:
            uid = self.dropbox_user.uid
            log.debug('path and metadata:')
            log.debug(path)
            log.debug(metadata)
            log.debug('updated metadata:')
            new_metadata = self.dropbox_user.client.metadata(path, include_media_info=True)
            log.debug(new_metadata)

        return True