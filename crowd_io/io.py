import json
from client_dropbox.client import DropboxClient,DropboxFile
from crowd_task.crowdbox import CrowdBoxImage

from image_pro import maskImage,placeMaskOnBackground,bufferImage

import logging
log = logging.getLogger(__name__)

def processDropboxWebhook(request):
    # to iterate list of users for whom there are any dropbox updates
    for uid in json.loads(request.body)['delta']['users']:
        dropboxclient = DropboxClient(uid)
        # get the latest updated files for a given user
        updates = dropboxclient.checkUpdates()
        log.debug('updates for user %s, are %s',str(uid),updates)
        # iterate the list of updated files
        for path, metadata  in updates:
            dropboxfile = DropboxFile(dropboxclient, path)
            # if updated file is an image
            if dropboxfile.isImage():
                crowdboximage = CrowdBoxImage(dropboxfile = dropboxfile)
                crowdboximage.processFileUpdate(request)

def makeOutputFromTaskResult(dropboxfile, original_image, mask_points, corners):

    # create mask image
    mask = maskImage(original_image,mask_points)
    # crop mask by the corner points
    mask = mask.crop((corners[0]['x'], corners[0]['y'], corners[1]['x'], corners[1]['y']))
    # place on background
    result_image = placeMaskOnBackground(mask)
    # place image in buffer
    buffer = bufferImage(result_image)
    # define path for locating image in dropbox
    path = dropboxfile.getLocation()+'/completed/'+dropboxfile.getFilename()
    log.debug('path of the new cropped image, %s',path)
    # paste buffer to dropbox
    dropboxfile.client.api.put_file(path, buffer)