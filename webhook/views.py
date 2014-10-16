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
    if 'challenge' in request.GET:
    	return HttpResponse(request.GET['challenge'])
    else:
        if request.body:
            log.debug(request.body)
            for uid in json.loads(request.body)['delta']['users']:
                log.debug(uid)
                dropboxclient = DropboxClient(uid)
                updates = dropboxclient.checkUpdates()
                log.debug(updates)

                for path, metadata  in updates:
                    dropboxfile = DropboxFile(dropboxclient, path, metadata)
                    if dropboxfile.isImage():
                        crowdboximage = CrowdBoxImage(dropboxfile)
                        if dropboxfile.isDeleted():
                            crowdboximage.unpublishCrowdCafeUnit()
                        else:
                            if crowdboximage.checkFilenameStatus():
                                log.debug(crowdboximage.checkFilenameUnitId)
                            else:
                                crowdboximage.createCrowdCafeUnit()
                    #dropboxfile = ImageUnit(dbuser)
                    #dropboxfile.decideWhatToDo(path, metadata)
                    #crowdcrop.publishImage(path, metadata)
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