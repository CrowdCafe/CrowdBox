'''
Celery tasks
'''
from celery import Celery
from django.conf import settings
from crowd_io.io import processDropboxWebhook
from crowd_task.judgements import processCrowdCafeNewJudgement


app = Celery('tasks', broker=settings.BROKER_URL)

@app.task()
def backgroundDropboxWebhook(data, domain):
    processDropboxWebhook(data, domain)
@app.task()
def backgroundCrowdCafeWebhook(data):
    processCrowdCafeNewJudgement(data)
