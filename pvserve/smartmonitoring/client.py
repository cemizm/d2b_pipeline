import requests
import urllib3
import pandas as pd
from .consts import *

urllib3.disable_warnings()

class Client:
    _host = 'https://scl.fh-bielefeld.de/SmartMonitoringBackendPVServe'
    _list = '/observedobject/list'
    _data = '/data/getSets?ooid='
    _metadata = '/observedobjectmetadata/list'
    _metatype = '/observedobjectmetadatatype/list'

    def __init__(self, host=None):
        if host is not None:
            self._host = host

    def get_objects(self):
        response = requests.get(self._host + self._list, verify=False)
        if not response.status_code == 200:
            return None
        
        response = response.json()
        if "list" not in response:
            return None

        df = pd.DataFrame(response['list'], columns=["id", "name", "parent", "type"])
        df = df.set_index(["id"])

        df.type = df.type.str.split("/", expand=True).iloc[:,-1]
        df.parent = df.parent.str.split("/", expand=True).iloc[:,-1]

        df.type = pd.to_numeric(df.type)
        df.parent = pd.to_numeric(df.parent).astype("Int64")

        return df

    def get_data(self, id):
        response = requests.get(self._host + self._data + str(id), verify=False)
        if not response.status_code == 200:
            return None
        
        response = response.json()
        if "list" not in response:
            return None
        
        df = pd.DataFrame(response["list"])

        df[SM_CURVE_I + SM_CURVE_U] = df[SM_CURVE_I + SM_CURVE_U].apply(pd.to_numeric)

        return df

    def get_meta_type(self):
        response = requests.get(self._host + self._metatype, verify=False)
        if not response.status_code == 200:
            return None
        
        response = response.json()
        if "list" not in response:
            return None
    
        df = pd.DataFrame(response['list'], columns=["id", "name"])
        df = df.set_index(["id"])

        return df
    
    def get_meta_data(self):
        response = requests.get(self._host + self._metadata, verify=False)
        if not response.status_code == 200:
            return None
        
        response = response.json()
        if "list" not in response:
            return None
    
        df = pd.DataFrame(response['list'], columns=["val", "observedobject", "type"])

        df.observedobject = df.observedobject.str.split("/", expand=True).iloc[:,-1]
        df.type = df.type.str.split("/", expand=True).iloc[:,-1]

        df.observedobject = pd.to_numeric(df.observedobject)
        df.type = pd.to_numeric(df.type)
        
        df = df.set_index(["type"])

        return df

    def get_meta_dataframe(self):
        metatypes = self.get_meta_type()
        metadata = self.get_meta_data()

        for id, group in metadata.groupby(["observedobject"]):
            val = group[['val']]
            val = val.rename(columns={"val": id})
            metatypes = metatypes.join(val)

        metadata = metatypes.T
        metadata = metadata.rename(columns=metadata.iloc[0])
        metadata = metadata.drop(metadata.index[0])
        metadata = metadata.reset_index().rename(columns={"index": "string_id"}).set_index(["string_id"])

        return metadata

    def get_meta_dataframe_workaround(self):
        return pd.read_csv("pvserve/smartmonitoring/meta.csv", sep=";", index_col=[0])

        
