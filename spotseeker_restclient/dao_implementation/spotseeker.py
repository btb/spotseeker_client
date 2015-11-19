from spotseeker_restclient.dao_implementation.live import get_con_pool, \
    get_live_url
from spotseeker_restclient.dao_implementation.mock import get_mockdata_url
from django.conf import settings


class File(object):
    def getURL(self, url, headers):
        return get_mockdata_url("spotseeker", "file", url, headers)


class Live(object):
    def getURL(self, url, headers):

        return ""
