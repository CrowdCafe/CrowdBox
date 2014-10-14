import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from dropbox_client.client import DropboxClient
from imageunit import ImageUnit


log = logging.getLogger(__name__)

@csrf_exempt
def webhook_dropbox(request):
    if 'challenge' in request.GET:
    	return HttpResponse(request.GET['challenge'])
    else:
    	for uid in json.loads(request.body)['delta']['users']:

            dbuser = DropboxClient(uid)
            updates = dbuser.checkUpdates()
            log.debug(updates)
            
            for path, metadata  in updates:
                rockpearl = ImageUnit(dbuser)
                rockpearl.decideWhatToDo(path, metadata)
                #crowdcrop.publishImage(path, metadata)
    	
        return HttpResponse(status=200)

def getMediaLink(request, uid):
    if uid and 'path' in request.GET:
        path = request.GET['path']
        dbuser = DropboxClient(uid)
        rockpearl = ImageUnit(dbuser)

        return redirect(rockpearl.getMediaURL(path))
    else:
        return HttpResponse(status=404)