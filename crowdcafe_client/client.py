__author__ = 'pavelk'

import json
import requests
import logging


log = logging.getLogger(__name__)

from django.conf import settings

# class to interact with CrowdCafe via API

class CrowdCafeAPI:
    def __init__(self):
        self.user_token = settings.CROWDCAFE['user_token']
        self.app_token = settings.CROWDCAFE['app_token']

    def getHeaders(self):
        return {
            'Content-type': 'application/json',
            'Authorization': 'Token ' + self.user_token + '|' + self.app_token
        }
    def apiCall(self, method, url, data = {}):
        log.debug('url %s', url)
        log.debug('data %s', data)

        request_url = settings.CROWDCAFE['api_url'] + url
        headers = self.getHeaders()
        r = None
        if method == 'post':
            r = requests.post(request_url, data=json.dumps(data), headers=headers)
        elif method == 'get':
            r = requests.get(request_url, headers=headers)
        elif method == 'patch':
            r = requests.patch(request_url, data=json.dumps(data), headers=headers)

        return r

    def getValue(self, r, field):
        ret = r.json()[field]
        log.debug("%s = %s" % (field, ret))
        return ret

    # Units

    def getUnit(self, unit_id):
        url = 'unit/' + str(unit_id) + '/'
        r = self.apiCall('get', url)
        log.debug("Unit res %s" % r.text)
        return r

    def createUnit(self, job_id, data):
        url = 'job/' + str(job_id) + '/unit/'
        r = self.apiCall('post', url, data)
        log.debug("Unit res %s" % r.text)

        return r

    def updateUnit(self, unit_id, data_to_update):
        url = 'unit/' + str(unit_id) + '/'
        r = self.apiCall('patch', url, data_to_update)
        log.debug("Unit res %s" % r.text)

        return r

    # Judgements

    def listJudgements(self, unit_id):
        url = 'unit/' + str(unit_id) + '/judgement/'
        r = self.apiCall('get', url)

        log.debug("Judgement result %s" % r.text)

        return r