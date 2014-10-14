from PIL import Image
import logging

import requests
from StringIO import StringIO

log = logging.getLogger(__name__)

import itertools

def splitArrayIntoPairs(arr):
    pairs = list(itertools.combinations(arr, 2))
    log.debug('\n pairs: %s', pairs)
    return pairs


def getFileViaUrl(url):
    response = requests.get(url)
    return Image.open(StringIO(response.content))
