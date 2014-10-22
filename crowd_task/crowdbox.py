import logging

from django.core.urlresolvers import reverse
from django.conf import settings

from client_crowdcafe.sdk import Unit
from client_dropbox.client import DropboxClient,DropboxFile

log = logging.getLogger(__name__)

class CrowdBoxImage(object):
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
        statuses = ('inprocess','completed')
        for status in statuses:
            if status+'_' in self.dropboxfile.getFilename():
                log.debug(status)
                return status
        return False
    # when we receive fileupdate as a webhook from dropbox
    def processFileUpdate(self, domain):
        log.debug('processFileUpdate is going, its unit is %s',self.unit)
        # if it was deleted from dropbox
        if self.dropboxfile.isDeleted():
            unit_id = self.checkFilenameUnitId()
            # if we can identify unit_id - then unpublish it from CrowdCafe
            if unit_id:
                self.unit.pk = unit_id
                self.unit.get()
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
    def checkFilenameUnitId(self):
        filename = self.dropboxfile.getFilename()
        UnitIdKeyword = 'ccunitid'

        if UnitIdKeyword in filename:
            unitid_with_filename = filename[filename.rfind(UnitIdKeyword)+len(UnitIdKeyword):len(filename)]
            log.debug(unitid_with_filename)
            unit_id = int(unitid_with_filename[:unitid_with_filename.find('_')])
            log.debug(unit_id)
            return unit_id
        log.debug(UnitIdKeyword+' is not in the '+filename)
        return False
    # ---------------------------------------------------------
    # CrowdCafe related methods
    def createUnit(self, domain):
        log.debug('pk before is %s',self.unit.pk)
        self.unit.create({'app':'pixelman'})
        log.debug('pk after is %s',self.unit.pk)

        # rename file
        new_filename = 'inprocess_CCunitid'+str(self.unit.pk)+'_'+self.dropboxfile.getFilename()


        unit_new_data = {
            'uid':self.dropboxfile.client.getUid(),
            'path':self.dropboxfile.getLocation()+'/'+new_filename,
            'image_filename':new_filename,
            'block_title':self.dropboxfile.getRoot()
        }
        unit_new_data['url'] = domain[:-1] + (reverse('task-thumbnail', kwargs={'uid': unit_new_data['uid']})+'?path='+unit_new_data['path'])
        log.debug('Update unit with data %s',unit_new_data)
        self.unit.input_data = unit_new_data
        self.unit.save()
        self.dropboxfile.rename(new_filename)
    # ---------------------------------------------------------
    # Image processing
    def getScaledPolygon(self, original_image, canvaspolygon):
        width, height = original_image.size
        canvaspolygon.polygon.scale(1.0*width/canvaspolygon.canvas['width'],1.0*height/canvaspolygon.canvas['height'])
        return canvaspolygon

    def getMaskPoints(self,canvaspolygon):
        return canvaspolygon.polygon.getSequence()