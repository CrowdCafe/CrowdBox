__author__ = 'pavelk'

from client import CrowdCafeAPI
import logging
log = logging.getLogger(__name__)

client = CrowdCafeAPI()

# CrowdCafe Unit API
# https://github.com/CrowdCafe/crowdcafe/blob/master/api/views.py#L103-L156

#TODO add pagination control to all requests

class Unit:
    def __init__(self, pk = None, job_id = None):
        self.pk = pk
        self.job_id = job_id

    def create(self, input_data):
        if not self.pk and self.job_id:
            url = 'job/' + str(self.job_id) + '/unit/'
            r = client('post', url, input_data)
            log.debug("Unit res %s" % r.text)
            self.setAttributes(r.json())
        else:
            log.debug('job_id is not set or unit_is is already set')
        return self

    def get(self):
        if self.pk:
            url = 'unit/' + str(self.pk) + '/'
            r = client('get', url)
            log.debug("Unit res %s" % r.text)
            self.setAttributes(r.json())
        else:
            log.debug('unit pk is not set')
            return False
    def save(self):
        if self.pk:
            url = 'unit/' + str(self.pk) + '/'
            r = client('patch', url, self.serialize())
            log.debug("Unit res %s" % r.text)
            self.setAttributes(r.json())
        else:
            log.debug('unit pk is not set')
            return False
    def serialize(self):
        return {
            'input_data':self.input_data,
            'status':self.status,
            'pk':self.pk,
            'published':self.published,
            'job':self.job_id,
            'gold':self.__gold
        }
    def judgements(self):
        url = 'unit/' + str(self.pk) + '/judgement/'
        r = client('get', url)
        log.debug("Judgement result %s" % r.text)
        judgements = []

        response = r.json()
        for judgement_data in response['results']:
            judgement = Judgement()
            judgement.setAttributes(judgement_data)
            judgements.append(judgement)
        return judgements

    def setAttributes(self, data):
        self.data = data

        self.pk = data['pk']
        self.job_id = data['job']
        self.input_data = data['input_data']
        self.status = data['status']
        self.published = data['published']
        # this is one is readonly
        self.__gold = data['gold']

    def isGold(self):
        return self.__gold



# CrowdCafe Judgement API
# https://github.com/CrowdCafe/crowdcafe/blob/master/api/views.py#L159-L183

class Judgement:
    def __init__(self, pk = None, unit_id = None):
        self.pk = pk
        self.unit_id = unit_id

    def get(self):
        url = 'unit/' + str(self.unit_id) + '/judgement/'+ str(self.pk)
        r = client('get', url)

        log.debug("Judgement result %s" % r.text)
        return r

    def unit(self):
        unit = Unit(pk = self.unit_id)
        unit.get()
        return unit

    def setAttributes(self, data):

        self.pk = data['pk']
        self.unit_id = data['unit']
        self.output_data = data['output_data']
        self.score = data['score']
        self.gold = data['gold']

    #TODO after you have approval at CrowdCafe - implement this method
    def update(self):
        return None