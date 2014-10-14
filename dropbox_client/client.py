from models import DropboxUser
from social_auth.models import UserSocialAuth
from dropbox import client, session
from django.conf import settings
from StringIO import StringIO

# class for managing dropbox operations:


class DropboxClient:
    def __init__(self, uid):
        self.uid = uid
        self.dropbox_user, created = DropboxUser.objects.get_or_create(uid=uid)

        social_user = UserSocialAuth.objects.get(uid=uid, provider='dropbox')
        secret = social_user.tokens['access_token'].split('&')[0].split('=')[1]
        token = social_user.tokens['access_token'].split('&')[1].split('=')[1]

        sess = session.DropboxSession(settings.DROPBOX_APP_ID, settings.DROPBOX_API_SECRET, 'app_folder')
        sess.set_token(token, secret)

        self.client = client.DropboxClient(sess)

    # manage webhook requests from dropbox
    def listen(self):
        return True

    # check updates (files and folders) for a specific user
    def checkUpdates(self):
        has_more = True
        updates = []
        while has_more:
            result = self.client.delta(self.dropbox_user.cursor)
            updates = updates + result['entries']
            # Update cursor
            self.dropbox_user.cursor = result['cursor']
            self.dropbox_user.save()
            # Repeat only if there's more to do
            has_more = result['has_more']

        return updates

    # upload a new file to a specific folder
    def getDirectLink(self, path):
        return self.client.media(path)

    def uploadFile(self, file_to_upload, path, file_type_for_buffer = None):
        buffer = file_to_upload
        if file_type_for_buffer:
            buffer = StringIO()
            file_to_upload.save(buffer, file_type_for_buffer)
        return self.dropbox_user.client.put_file(path, buffer)

        # rename folder
        # def renameFolder(self, path, name):
        # return True
