__author__ = 'pavelk'
import logging
import json
from client_crowdcafe.sdk import Judgement
from crowdbox import CrowdBoxImage
from crowd_task.evaluation import findAgreement
from crowd_io.io import makeOutputFromTaskResult

log = logging.getLogger(__name__)
def processCrowdCafeNewJudgement(request):
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
                # pick correct judgement (any from agreement)
                judgement = agreement[0]
                result = crowdboximage.processResult(judgement)
                makeOutputFromTaskResult(result)
                #update unit status as completed
                unit.status = 'CD'
            else:
                log.debug('agreement was not found')
                #update unit status as not completed
                unit.status = 'NC'
            #save unit
            unit.save()