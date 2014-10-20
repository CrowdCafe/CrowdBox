import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


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
            backgroundDropboxWebhook.delay(request)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

