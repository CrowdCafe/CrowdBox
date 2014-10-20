import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from client_dropbox.client import DropboxClient
from client_crowdcafe.sdk import Judgement
from control_task.evaluation import CanvasPolygon, CanvasPolygonSimilarity, findAgreement
from crowdbox import CrowdBoxImage
log = logging.getLogger(__name__)


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
        log.debug('request body: %s', request.body)
        # we received list of judgements data
        data = json.loads(request.body)
        for item in data:
            # get judgement
            judgement = Judgement()
            judgement.setAttributes(item)
            # get unit
            unit = judgement.unit()
            # if this unit is not gold
            if not unit.isGold():
                # get all judgements
                judgements = unit.judgements()
                # search for agreement among judgements
                agreement = findAgreement(judgements)
                if agreement:
                    log.debug('agreement is found, %s',agreement)
                    crowdboximage = CrowdBoxImage(unit = unit)
                    crowdboximage.processAgreement(agreement)
                    #update unit status as completed
                    unit.status = 'CD'
                else:
                    log.debug('agreement was not found')
                    #update unit status as not completed
                    unit.status = 'NC'
                #save unit
                unit.save()
        return HttpResponse(status=200)
    return HttpResponse(status=405)