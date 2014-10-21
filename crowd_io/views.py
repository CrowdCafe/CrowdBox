import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from background_tasks.tasks import backgroundDropboxWebhook
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
            data = json.loads(request.body)
            backgroundDropboxWebhook.delay(data, request.build_absolute_uri('/'))
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

