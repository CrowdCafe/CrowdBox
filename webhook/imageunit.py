from crowdcafe_client.sdk import Unit
from django.core.urlresolvers import reverse
from django.conf import settings
from dropbox_client.client import DropboxClient,DropboxFile
from image_processing.image_pro import getImageViaUrl,maskImage,placeMaskOnBackground,bufferImage
from qualitycontrol.evaluation import CanvasPolygon
import logging

log = logging.getLogger(__name__)

class CrowdBoxImage:
    def __init__(self, dropboxfile = None, unit = Unit(job_id = settings.CROWDCAFE['job_id'])):

        self.dropboxfile = dropboxfile
        self.unit = unit
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
    def processUpdateFromDropbox(self, request):
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
                self.createUnit(request)
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
    def createUnit(self, request):
        #TODO - check whether I can create a unit with empty inputdata

        self.unit.create({'blank':'yes'})
        # rename file
        new_filename = 'inprocess_CCunitid'+str(self.unit.pk)+'_'+self.dropboxfile.getFilename()
        self.dropboxfile.rename(new_filename)

        #TODO add url to the image
        unit_new_data = {
            'uid':self.dropboxfile.client.getUid(),
            'path':self.dropboxfile.getPath(),
            'image_filename':self.dropboxfile.getFilename(),
            'block_title':self.dropboxfile.getRoot()
        }
        unit_new_data['url'] = request.build_absolute_uri(reverse('webhook-image-thumbnail', kwargs={'uid': unit_new_data['uid']})+'?path='+unit_new_data['path'])
        log.debug('Update unit with data %s',unit_new_data)
        self.unit.input_data = unit_new_data
        self.unit.save()
    # ---------------------------------------------------------
    # Image processing
    def getScaledPolygon(self, original_image, canvaspolygon):
        width, height = original_image.size
        canvaspolygon.polygon.scale(1.0*width/canvaspolygon.canvas['width'],1.0*height/canvaspolygon.canvas['height'])
        return canvaspolygon

    def getMaskPoints(self,canvaspolygon):
        return canvaspolygon.polygon.getSequence()

    def processAgreement(self, agreement):
        # get original image
        original_image = getImageViaUrl(self.dropboxfile.getMediaURL())
        # select judgement based on which to cut image
        judgement = agreement[0]
        canvaspolygon = CanvasPolygon(judgement.output_data)
        # scale polygon of the judgement
        canvaspolygon = self.getScaledPolygon(original_image, canvaspolygon)
        # add margins to polygon
        canvaspolygon.polygon.enlargeAbs(settings.MARBLE_3D_ENLARGE_POLYGON)
        # get Mask points
        mask_points = self.getMaskPoints(canvaspolygon)
        # create mask image
        mask = maskImage(original_image,mask_points)
        # get corners points of the polygon
        corners = canvaspolygon.polygon.getCorners()
        # crop mask by the corner points
        mask = mask.crop((corners[0]['x'], corners[0]['y'], corners[1]['x'], corners[1]['y']))
        # place on background
        result_image = placeMaskOnBackground(mask)
        # add EXIV data to the result_image
        result_image.info = self.dropboxfile.metadata['photo_info']
        # place image in buffer
        buffer = bufferImage(result_image)
        # define path for locating image in dropbox
        path = self.dropboxfile.getLocation()+'/completed/'+self.dropboxfile.getFilename()
        log.debug('path of the new cropped image, %s',path)
        # paste buffer to dropbox
        self.dropboxfile.client.api.put_file(path, buffer)