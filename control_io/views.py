import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from client_dropbox.client import DropboxClient, DropboxFile
from control_task.crowdbox import CrowdBoxImage

log = logging.getLogger(__name__)

@csrf_exempt
def webhook_dropbox(request):
    log.debug('---------- webhook dropbox --------------')
    if request.method == 'GET':
        # if it is only a verification request from Dropbox - send back challenge parameter
        if 'challenge' in request.GET:
            return HttpResponse(request.GET['challenge'])
    elif request.method == 'POST':
        if request.body:
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
                        crowdboximage.processUpdateFromDropbox(request)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)