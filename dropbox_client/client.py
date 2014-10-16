from models import DropboxUser
from social_auth.models import UserSocialAuth
from dropbox import client, session
from django.conf import settings
from StringIO import StringIO

import logging

log = logging.getLogger(__name__)

# class for managing dropbox operations:


class DropboxClient:
    def __init__(self, uid):

        self.uid = uid
        self.user, created = DropboxUser.objects.get_or_create(uid=uid)

        social_user = UserSocialAuth.objects.get(uid=uid, provider='dropbox')
        secret = social_user.tokens['access_token'].split('&')[0].split('=')[1]
        token = social_user.tokens['access_token'].split('&')[1].split('=')[1]

        sess = session.DropboxSession(settings.DROPBOX_APP_ID, settings.DROPBOX_API_SECRET, 'app_folder')
        sess.set_token(token, secret)

        self.api = client.DropboxClient(sess)

    # manage webhook requests from dropbox
    def listen(self):
        return True

    # check updates (files and folders) for a specific user
    def checkUpdates(self):
        log.debug(self)
        has_more = True
        updates = []
        while has_more:
            result = self.api.delta(self.user.cursor)
            updates = updates + result['entries']
            # Update cursor
            self.user.cursor = result['cursor']
            self.user.save()
            # Repeat only if there's more to do
            has_more = result['has_more']

        return updates
    def getUid(self):
        return self.uid
    # upload a new file to a specific folder
    def getDirectLink(self, path):
        return self.api.media(path)
    def getMetadata(self,path):
        return self.api.metadata(path)
    def uploadFile(self, file_to_upload, path, file_type_for_buffer = None):
        buffer = file_to_upload
        if file_type_for_buffer:
            buffer = StringIO()
            file_to_upload.save(buffer, file_type_for_buffer)
        return self.user.client.put_file(path, buffer)

        # rename folder
        # def renameFolder(self, path, name):
        # return True


'''
        This is how the metadata looks like
        {
            u'revision': 32,
            u'bytes': 614040,
            u'thumb_exists': True,
            u'rev': u'202b999c17',
            u'modified': u'Thu,
            16Oct201414: 18: 42+0000',
            u'mime_type': u'image/jpeg',
            u'path': u'/Testonly/Block-2B-Wet(6)(1)copy15.jpg',
            u'is_dir': False,
            u'size': u'599.6KB',
            u'root': u'app_folder',
            u'client_mtime': u'Thu,
            09Oct201416: 36: 54+0000',
            u'icon': u'page_white_picture'
        }
        {
            u'is_deleted': True,
            u'revision': 34,
            u'bytes': 0,
            u'thumb_exists': True,
            u'rev': u'222b999c17',
            u'modified': u'Thu,
            16Oct201414: 20: 37+0000',
            u'mime_type': u'image/jpeg',
            u'path': u'/Testonly/Block-2B-Wet(6)(1)copy14.jpg',
            u'photo_info': {
                u'lat_long': None,
                u'time_taken': None
            },
            u'is_dir': False,
            u'size': u'0bytes',
            u'root': u'app_folder',
            u'client_mtime': u'Wed,
            31Dec196923: 59: 59+0000',
            u'icon': u'page_white_picture'
        }
'''

class DropboxFile:
    def __init__(self, dropbox_client, path, metadata):
        self.client = dropbox_client
        self.path = path
        self.updateMetadata()

        log.debug('path:')
        log.debug(self.path)

        log.debug('metadata:')
        log.debug(self.metadata)

    def getPath(self):
        return self.path

    def getMetadata(self):
        return self.metadata

    def getFilename(self):
        filename = self.path[self.path.rfind('/') + 1:len(self.path)]
        log.debug('filename: '+filename)
        return filename

    def getLocation(self):
        location = self.path[:self.path.rfind('/')]
        log.debug('location: '+location)
        return location

    def getRoot(self):
        # folder = rest_path[rest_path.rfind('/') + 1:len(rest_path)]
        if self.metadata:
            if 'root' in self.metadata:
                return self.metadata['root']
        return None
    def isFolder(self):
        if self.metadata:
            if 'is_dir' in self.metadata:
                return self.metadata['is_dir']
        return False

    def isDeleted(self):
        if self.metadata:
            if 'is_deleted' in self.metadata:
                return self.metadata['is_deleted']
        return True

    def rename(self, new_filename):
        old_path = self.getPath()
        new_path = self.getLocation()+'/'+new_filename
        self.client.api.file_move(old_path,new_path)
        self.path = new_path
        self.updateMetadata()

    def isImage(self):
        if self.metadata:
            if 'mime_type' in self.metadata:
                if 'image' in self.metadata['mime_type']:
                    return True
        return False

    def updateMetadata(self):
        path = self.getPath()
        log.debug('retrieve metadata for '+path)
        self.metadata = self.client.getMetadata(path)

    def getMediaURL(self):
        media = self.client.getDirectLink(self.path)
        return media['url']
