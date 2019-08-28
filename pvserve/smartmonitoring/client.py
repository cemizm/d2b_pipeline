import requests
import urllib3
urllib3.disable_warnings()

class Client:
    _host = 'https://scl.fh-bielefeld.de/SmartMonitoringBackendPVServe'
    _list = '/observedobject/list'
    _data = '/data/getSets?ooid='

    def __init__(self, host=None):
        if host is not None:
            self._host = host


    def getObjects(self):
        response = requests.get(self._host + self._list, verify=False)
        return response.json()

    def getData(self, id):
        response = requests.get(self._host + self._data + str(id), verify=False)
        return response.json()