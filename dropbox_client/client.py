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
    def getMedia(self, path):
        return self.api.media(path)

    def getMetadata(self,path, include_media_info = True):
        return self.api.metadata(path, include_media_info = include_media_info)

    def uploadFile(self, file_to_upload, path, file_type_for_buffer = None):
        buffer = file_to_upload
        if file_type_for_buffer:
            buffer = StringIO()
            file_to_upload.save(buffer, file_type_for_buffer)
        return self.user.client.put_file(path, buffer)

    def getThumbnail(self, path, size = 'l', format = "JPEG"):
        return self.api.thumbnail(path, size, format)
        # rename folder
        # def renameFolder(self, path, name):
        # return True

class DropboxFile:
    def __init__(self, dropbox_client, path):
        self.client = dropbox_client
        self.path = path
        self.updateMetadata()


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
            else:
                return False
        return False

    def rename(self, new_filename):
        old_path = self.getPath()
        log.debug('old_path '+old_path)
        new_path = self.getLocation()+'/'+new_filename
        log.debug('new_path '+new_path)

        self.client.api.file_move(old_path,new_path)
        log.debug('file renamed')
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
        metadata = self.client.getMetadata(path)
        log.debug('retrieve metadata for %s,: %s ',path,metadata)
        self.metadata = metadata

    def getMediaURL(self):
        media = self.client.getMedia(self.path)
        return media['url']
