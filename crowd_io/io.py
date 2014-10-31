import logging

from django.conf import settings

from client_dropbox.client import DropboxClient,DropboxFile
from crowd_task.crowdbox import CrowdBoxImage, RSLT_FOLDER,STATUS_RSLT
from image_pro import getImageViaUrl
from crowd_task.utils.evaluation import CanvasPolygon
from image_pro import maskImage,placeMaskOnBackground,copyExifData
import os


log = logging.getLogger(__name__)


def processDropboxWebhook(data, domain):
    # we received list of judgements data
    log.debug('data from dropbox: %s', data)
    # to iterate list of users for whom there are any dropbox updates
    for uid in data['delta']['users']:
        dropboxclient = DropboxClient(uid)
        # get the latest updated files for a given user
        updates = dropboxclient.checkUpdates()
        log.debug('updates for user %s, are %s', str(uid), updates)
        # iterate the list of updated files
        for path, metadata in updates:
            dropboxfile = DropboxFile(dropboxclient, path)
            # if updated file is an image
            if dropboxfile.isImage():
                crowdboximage = CrowdBoxImage(dropboxfile=dropboxfile)
                crowdboximage.processFileUpdate(domain)


def makeOutputFromTaskResult(crowdcafeimage, judgement):
    # get original image
    original_image = getImageViaUrl(crowdcafeimage.dropboxfile.getMediaURL())
    # get canvaspolygon
    canvaspolygon = CanvasPolygon(judgement.output_data)
    # scale polygon of the judgement
    canvaspolygon.scale(original_image)
    # add margins to polygon
    canvaspolygon.polygon.enlargeAbs(settings.MARBLE_3D_ENLARGE_POLYGON)
    # get Mask points
    mask_points = crowdcafeimage.getMaskPoints(canvaspolygon)
    # create mask image
    mask = maskImage(original_image,mask_points)
    # get corners points of the polygon
    corners = canvaspolygon.polygon.getCorners()
    # crop mask by the corner points
    mask = mask.crop((corners[0]['x'], corners[0]['y'], corners[1]['x'], corners[1]['y']))
    # place on background
    result_image = placeMaskOnBackground(mask)
    # copy EXIF
    result_file = copyExifData(settings.MEDIA_ROOT, original_image,result_image)
    f = open(result_file, 'rb')
    # define path for locating image in dropbox
    path = crowdcafeimage.dropboxfile.getLocation()+'/'+RSLT_FOLDER+'/'+crowdcafeimage.getFilenameForStatus(STATUS_RSLT,crowdcafeimage.unit.input_data['image_filename'])
    log.debug('path of the new cropped image, %s',path)
    # paste buffer to dropbox
    #crowdcafeimage.dropboxfile.client.api.put_file(path, buffer)
    crowdcafeimage.dropboxfile.client.api.put_file(path, f)
    # remove file
    if os.path.exists(result_file):
        os.remove(result_file)


