import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from dropbox_client.client import DropboxClient, DropboxFile
from imageunit import CrowdBoxImage


log = logging.getLogger(__name__)

@csrf_exempt
def webhook_dropbox(request):
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
                    dropboxfile = DropboxFile(dropboxclient, path, metadata)
                    # if updated file is an image
                    if dropboxfile.isImage():
                        crowdboximage = CrowdBoxImage(dropboxfile)
                        crowdboximage.processUpdateFromDropbox()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

def getMediaLink(request, uid):
    if uid and 'path' in request.GET:
        path = request.GET['path']
        dropboxclient = DropboxClient(uid)
        media = dropboxclient.getDirectLink(path)
        return redirect(media['url'])
    else:
        return HttpResponse(status=404)