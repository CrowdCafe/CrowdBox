__author__ = 'pavelk'
import logging

from client_crowdcafe.sdk import Judgement
from crowdbox import CrowdBoxImage,STATUS_DONE
from crowd_task.utils.evaluation import findAgreement
from crowd_io.io import makeOutputFromTaskResult

log = logging.getLogger(__name__)
def processCrowdCafeNewJudgement(data):
    log.debug('new judgements: %s',data)
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
                crowdboximage.dropboxfile.rename(crowdboximage.getFilenameForStatus(STATUS_DONE, crowdboximage.unit.input_data['image_filename']))
                # pick correct judgement (any from agreement)
                judgement = agreement[0]
                makeOutputFromTaskResult(crowdboximage,judgement)
                #update unit status as completed
                unit.status = 'CD'
            else:
                log.debug('agreement was not found')
                #update unit status as not completed
                unit.status = 'NC'
            #save unit
            unit.save()