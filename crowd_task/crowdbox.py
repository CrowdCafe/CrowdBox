import logging

from django.core.urlresolvers import reverse
from django.conf import settings
from social_auth.models import UserSocialAuth
from client_crowdcafe.sdk import Unit
from client_dropbox.client import DropboxClient,DropboxFile
from crowd_io.image_pro import getExifDictionary

from account.models import Account, FundTransfer
log = logging.getLogger(__name__)

IMAGE_STATUSES = ('syncing','working','completed','result')

STATUS_SYNC = IMAGE_STATUSES[0]
STATUS_WORK = IMAGE_STATUSES[1]
STATUS_DONE = IMAGE_STATUSES[2]
STATUS_RSLT = IMAGE_STATUSES[3]

RSLT_FOLDER = 'completed'

IMAGE_STATUS_SEPARATOR = '-'
IMAGE_UNIT_ID_KEYWORD = 'cafe_id='

class CrowdBoxImage:
    def __init__(self, dropboxfile = None, unit = None):
        if unit is None:
            self.unit = Unit(job_id = settings.CROWDCAFE['job_id'])
        else:
            self.unit = unit
        self.dropboxfile = dropboxfile
        if not self.dropboxfile:
            self.getDropboxFile()
    # ---------------------------------------------------------
    # Dropbox related methods
    def getDropboxFile(self):
        if self.unit.pk:
            input_data = self.unit.input_data
            log.debug('input data: %s',input_data)
            dropboxclient = DropboxClient(int(input_data['uid']))
            dropboxfile = DropboxFile(dropboxclient, input_data['path'])
            if dropboxfile.isImage():
                self.dropboxfile = dropboxfile
        else:
            log.debug('unit is not set')
    def checkFilenameStatus(self):
        for status in IMAGE_STATUSES:
            if status+IMAGE_STATUS_SEPARATOR in self.dropboxfile.getFilename():
                log.debug(status)
                return status
        return False
    def checkFilenameUnitId(self):
        filename = self.dropboxfile.getFilename()

        if IMAGE_UNIT_ID_KEYWORD in filename:
            unitid_with_filename = filename[filename.rfind(IMAGE_UNIT_ID_KEYWORD)+len(IMAGE_UNIT_ID_KEYWORD):len(filename)]
            log.debug(unitid_with_filename)
            unit_id = int(unitid_with_filename[:unitid_with_filename.find(IMAGE_STATUS_SEPARATOR)])
            log.debug(unit_id)
            return unit_id
        log.debug(IMAGE_UNIT_ID_KEYWORD+' is not in the '+filename)
        return False
    # when we receive fileupdate as a webhook from dropbox
    def processFileUpdate(self, domain):
        log.debug('processFileUpdate is going, its unit is %s',self.unit.pk)
        # if it was deleted from dropbox
        if self.dropboxfile.isDeleted():
            unit_id = self.checkFilenameUnitId()
            # if we can identify unit_id - then unpublish it from CrowdCafe
            if unit_id:
                self.unit.pk = unit_id
                self.unit.get()
                if self.unit.status != 'CD':
                    self.unit.published = False
                    self.unit.save()
        else:
            # if the file already was processed and has status in its name
            if self.checkFilenameStatus():
                log.debug('the file already exists and its Unit_id is, %s',self.checkFilenameUnitId())
                # if file was not processed - create new unit in CrowdCafe
            else:
                log.debug('we create a new unit at CrowdCafe')
                self.createUnit(domain)
    def getFilenameForStatus(self, status, original_filename):
        new_filename = status + IMAGE_STATUS_SEPARATOR
        if status in [STATUS_SYNC,STATUS_RSLT]:
            new_filename +=original_filename
        elif status in [STATUS_WORK, STATUS_DONE]:
            new_filename +=IMAGE_UNIT_ID_KEYWORD+str(self.unit.pk)+IMAGE_STATUS_SEPARATOR+original_filename
        return new_filename
    # ---------------------------------------------------------
    # CrowdCafe related methods
    def createUnit(self, domain):
        # rename file that we are syncing (to avoid getting duplicated updates)
        filename = self.dropboxfile.getFilename()
        self.dropboxfile.rename(self.getFilenameForStatus(STATUS_SYNC,filename))
        # create blank unit at CrowdCafe to receive pk
        log.debug('pk before is %s',self.unit.pk)
        self.unit.create({'app':'crowdbox'})
        log.debug('pk after is %s',self.unit.pk)
        # construct new filename with work status and unit_id
        work_filename = self.getFilenameForStatus(STATUS_WORK,filename)
        # construct crowdcafe unit data
        unit_new_data = {
            'uid':self.dropboxfile.client.getUid(),
            'path':self.dropboxfile.getLocation()+'/'+work_filename,
            'image_filename':filename,
            'block_title':self.dropboxfile.getRoot()
        }
        # construct url which returns thumbnail url
        unit_new_data['url'] = domain[:-1] + (reverse('task-thumbnail', kwargs={'uid': unit_new_data['uid']})+'?path='+unit_new_data['path'])
        log.debug('Update unit with data %s',unit_new_data)
        # update with new data crowdcafe unit
        self.unit.input_data = unit_new_data
        self.unit.save()
        # update filename at dropbox
        self.dropboxfile.rename(work_filename)
    # ---------------------------------------------------------
    # Image processing
    def getScaledPolygon(self, original_image, canvaspolygon):
        canvaspolygon.orient(original_image)
        width, height = original_image.size
        canvaspolygon.polygon.scale(1.0*width/canvaspolygon.canvas['height'],1.0*height/canvaspolygon.canvas['weight'])
        return canvaspolygon

    def getMaskPoints(self,canvaspolygon):
        return canvaspolygon.polygon.getSequence()
    # ---------------------------------------------------------
    # Other
    def setOwner(self, uid):
        social_user = UserSocialAuth.objects.get(uid=uid, provider='dropbox')
        self.user = social_user.user
        log.debug('set owner, %s, %s',uid, self.user)

    def chargeOwner(self, amount, description):
        admin_account = Account.objects.get(pk = settings.BUSINESS['admin_account_id'])
        if self.user:
            log.debug('create a payment')
            payment = FundTransfer(from_account = self.user.profile.personalAccount, to_account = admin_account, amount = float(amount), description = description)
            payment.save()



