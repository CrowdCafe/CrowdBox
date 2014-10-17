from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


from crowdcafe_qualitycontrol.judgements import Evaluation, Judgement
from tasks import processCrowdCafeResult

import json

def home(request):
    return render_to_response('marble3d/home.html', context_instance=RequestContext(request))

def splitJudgementsData(data):
    judgements = {}
    for item in data:
        if item['gold']:
            judgements['gold'] = Judgement(crowdcafe_data=item)
        else:
            judgements['given'] = Judgement(crowdcafe_data=item)
    return judgements['gold'], judgements['given']

@csrf_exempt
def assesJudgementAgainstGold(request):
    data = json.loads(request.body)
    gold, given = splitJudgementsData(data)
    evaluation = Evaluation(judgement1=given, judgement2=gold)
    if evaluation.judgementsAreSimilar():
        return HttpResponse(status=200, content=json.dumps({'score': 1, 'correct': True}))
    else:
        return HttpResponse(status=200, content=json.dumps({'score': -1, 'correct': False}))

@csrf_exempt
def receiveJudgement(request):

    data = request.body
    judgements = json.loads(data)
    for item in judgements:
        processCrowdCafeResult.delay(item)
    return HttpResponse(status=200)