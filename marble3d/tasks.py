"""
Celery tasks
"""
import os
from celery import Celery, task
from social_auth.models import UserSocialAuth
from django.conf import settings
import json
from crowdcafe_qualitycontrol.judgements import Judgement, Evaluation
from utils import splitArrayIntoPairs
from crowdcafe_client.client import CrowdCafeAPI
import logging
from social_auth.models import UserSocialAuth
from models import Image

log = logging.getLogger(__name__)

# app = Celery('tasks', broker=settings.BROKER_URL)
app = Celery('tasks', broker=settings.BROKER_URL)
crowdcafe = CrowdCafeAPI()


@app.task()
def processCrowdCafeResult(item):
    crowdcafe = CrowdCafeAPI()
    unit = crowdcafe.getUnit(item['unit'])
    judgements_of_unit = crowdcafe.listJudgements(item['unit'])

    log.debug('judgements in the unit are: ' + str(judgements_of_unit['count']))

    if judgements_of_unit['count'] >= 2 and not unit['gold']:
        judgement_to_pick = getGoodJudgement(judgements_of_unit['results'])
        if judgement_to_pick:
            processGoodJudgement(judgement_to_pick, unit)
            crowdcafe.updateUnit(item['unit'], {'status': 'CD'})
        #call.updateUnitStatus(unit['pk'],'CD')
        else:
            crowdcafe.updateUnit(item['unit'], {'status': 'NC'})
        #call.updateUnitStatus(unit['pk'],'NC')
    else:
        log.debug('judgements in the unit are less than 2 or the unit is gold')


def getGoodJudgement(unit_judgements):
    log.debug('get good judgement')

    judgement_to_pick = False
    # split judgements of the unit in pairs
    for pair in splitArrayIntoPairs(unit_judgements):
        judgement1 = Judgement(crowdcafe_data=pair[0])
        judgement2 = Judgement(crowdcafe_data=pair[1])
        # we check if judgements in the pair are similar to each other
        evaluation = Evaluation(judgement1=judgement1, judgement2=judgement2,
                                threashold=settings.MARBLE_3D_ERROR_THREASHOLD)

        if evaluation.judgementsAreSimilar():
            # if they are similar, we pick the first judgement from the pair
            judgement_to_pick = judgement1
    return judgement_to_pick


def processGoodJudgement(judgement_to_pick, unit):
    # get image to which this judgement belongs
    img_query = Image.objects.filter(pk=unit['input_data']['image_id'])
    if img_query.count() > 0:
        img = img_query.all()[0]
        # get user created the block in which this image is
        user = img.block.user
        # get dropbox credentials to send this image to dropbox of the user
        social_user = UserSocialAuth.objects.get(user=user)
        secret = social_user.tokens['access_token'].split('&')[0].split('=')[1]
        token = social_user.tokens['access_token'].split('&')[1].split('=')[1]
        # create cropped image based on the selected judgement and send to dropbox
        judgement_to_pick.cropAndSave(unit['input_data'], token, secret)
        # update image in Rockpearl
        img.status = 'CD'
        img.crowdcafe_unit_id = unit['pk']
        img.save()
    else:
        log.debug('image with id:' + str(unit['input_data']['image_id']) + ', does not exist. We did nothing.')
