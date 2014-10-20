import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from client_dropbox.client import DropboxClient
from client_crowdcafe.sdk import Judgement
from crowd_task.evaluation import CanvasPolygon, CanvasPolygonSimilarity
log = logging.getLogger(__name__)
from background_tasks.tasks import processCrowdCafeNewJudgement

# return thumbnail of an image from dropbox with a given path

def getThumbnail(request, uid):
    if 'path' in request.GET:
        path = request.GET['path']
        dropboxclient = DropboxClient(uid)
        thumbnail = dropboxclient.getThumbnail(path)
        return HttpResponse(thumbnail.read(), mimetype="image/jpeg")
    else:
        return HttpResponse(status=404)

@csrf_exempt
def controlGold(request):
    log.debug('---------- webhook crowdcafe quality control --------------')
    if request.method == 'POST' and request.body:
        log.debug('request body: %s', request.body)
        data = json.loads(request.body)
        canvaspolygons = []
        # iterate through data about judgements
        for item in data:
            # init a judgement
            judgement = Judgement()
            judgement.setAttributes(item)
            # get canvaspolygon
            canvaspolygons.append(CanvasPolygon(judgement))
        test = CanvasPolygonSimilarity(canvaspolygons)
        #TODO fix it when we have approval for judgements
        # test whether polygons are similar to each other or not
        if test.areSimilar():
            return HttpResponse(status=200, content=json.dumps({'score': 1, 'correct': True}))
        else:
            return HttpResponse(status=200, content=json.dumps({'score': -1, 'correct': False}))
    else:
        return HttpResponse(status=405)

@csrf_exempt
def receiveNewJudgement(request):
    log.debug('---------- webhook crowdcafe new judgement --------------')
    if request.method == 'POST' and request.body:
        processCrowdCafeNewJudgement.delay(request)
        return HttpResponse(status=200)
    return HttpResponse(status=405)