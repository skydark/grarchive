# -*- coding: utf-8 -*-

import requests
from requests.compat import urlencode, urlparse

# import urllib2

import time

try:
    import json
except:
    # Python 2.6 support
    import simplejson as json

try:
    import oauth2 as oauth
    has_oauth = True
except:
    has_oauth = False

try:
    import httplib2
    has_httplib2 = True
except:
    has_httplib2 = False

def toUnicode(obj, encoding='utf-8'):
    return obj
    # if isinstance(obj, basestring):
    #     if not isinstance(obj, unicode):
    #         obj = unicode(obj, encoding)
    # return obj

class AuthenticationMethod(object):
    """
    Defines an interface for authentication methods, must have a get method
    make this abstract?
    1. auth on setup
    2. need to have GET method
    """
    def __init__(self):
        self.client = "libgreader" #@todo: is this needed?

    def getParameters(self, extraargs=None):
        parameters = {'ck':time.time(), 'client':self.client}
        if extraargs:
            parameters.update(extraargs)
        return urlencode(parameters)

    def postParameters(self, post=None):
        return post

class ClientAuthMethod(AuthenticationMethod):
    """
    Auth type which requires a valid Google Reader username and password
    """
    CLIENT_URL = 'https://www.google.com/accounts/ClientLogin'

    def __init__(self, username, password):
        super(ClientAuthMethod, self).__init__()
        self.username   = username
        self.password   = password
        self.auth_token = self._getAuth()
        # self.token      = self._getToken()

    def postParameters(self, post=None):
        raise NotImplementedError
        post.update({'T': self.token})
        return super(ClientAuthMethod, self).postParameters(post)

    def get(self, url, parameters=None):
        """
        Convenience method for requesting to google with proper cookies/params.
        """
        getString = self.getParameters(parameters)
        headers = {'Authorization':'GoogleLogin auth=%s' % self.auth_token}
        req = requests.get(url + "?" + getString, headers=headers)
        return req.text

    def post(self, url, postParameters=None, urlParameters=None):
        """
        Convenience method for requesting to google with proper cookies/params.
        """
        if urlParameters:
            url = url + "?" + self.getParameters(urlParameters)
        headers = {'Authorization':'GoogleLogin auth=%s' % self.auth_token,
                    'Content-Type': 'application/x-www-form-urlencoded'
                    }
        postString = self.postParameters(postParameters)
        req = requests.post(url, data=postString, headers=headers)
        return req.text

    def _getAuth(self):
        """
        Main step in authorizing with Reader.
        Sends request to Google ClientAuthMethod URL which returns an Auth token.

        Returns Auth token or raises IOError on error.
        """
        parameters = {
            'service'     : 'reader',
            'Email'       : self.username,
            'Passwd'      : self.password,
            'accountType' : 'GOOGLE'}
        req = requests.post(ClientAuthMethod.CLIENT_URL, data=parameters)
        if req.status_code != 200:
            raise IOError("Error getting the Auth token, have you entered a"
                    "correct username and password?")
        data = req.text
        #Strip newline and non token text.
        token_dict = dict(x.split('=') for x in data.split('\n') if x)
        return token_dict["Auth"]

    def _getToken(self):
        """
        Second step in authorizing with Reader.
        Sends authorized request to Reader token URL and returns a token value.

        Returns token or raises IOError on error.
        """
        headers = {'Authorization':'GoogleLogin auth=%s' % self.auth_token}
        req = requests.get(ReaderUrl.API_URL + 'token', headers=headers)
        if req.status_code != 200:
            raise IOError("Error getting the Reader token.")
        return req.content
