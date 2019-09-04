import requests
import urllib3
import pandas as pd
urllib3.disable_warnings()

class Client:
    _host = 'https://scl.fh-bielefeld.de/SmartMonitoringBackendPVServe'
    _list = '/observedobject/list'
    _data = '/data/getSets?ooid='
    _metadata = '/observedobjectmetadata/list'
    _metatype = '/observedobjectmetadatatype/list'
    _metadataid = '/observedobjectmetadata/listForObservedObject?ooid='

    def __init__(self, host=None):
        if host is not None:
            self._host = host


    def getObjects(self):
        response = requests.get(self._host + self._list, verify=False)
        return response.json()

    def getData(self, id):
        response = requests.get(self._host + self._data + str(id), verify=False)
        return response.json()
    
    def get_meta_data(self):
        response = requests.get(self._host + self._metadata, verify=False)
        return response.json()

    def get_meta_type(self):
        response = requests.get(self._host + self._metatype, verify=False)
        return response.json()

    def get_meta_data_by_id(self, id):
        response = requests.get(self._host + self._metadataid + str(id), verify=False)
        return response.json()
    
    
    def get_observed_objects(self):
        return pd.DataFrame(self.getObjects()['list'], columns=["id", "name", "parent", "type"])

    def get_plant(self, observed_objects):
        return observed_objects.loc[pd.isnull(observed_objects["parent"])]

    def get_plant_modules(self, observed_objects, plant_id):
        return observed_objects.loc[observed_objects["parent"] == "ref://observedobject/get/" + str(plant_id)]

    def get_curves(self, observed_objects, pv_modules, typ):
        curve_id = []
        curves = []
        for id in pv_modules["string_id"]:
            plant_modul_data = observed_objects.loc[observed_objects["parent"] == "ref://observedobject/get/" + str(id)]
            curve_id = plant_modul_data.loc[plant_modul_data["type"] == typ]
            if not curve_id.empty:
                dataframe = pd.DataFrame(self.getData(curve_id["id"].values[0])['list'])
                dataframe.insert(1, 'parent_id', id)
                curves.append(dataframe)
        return pd.concat(curves,ignore_index=True)

    def meta_to_file(self, observed_objects):
        pv_plants = self.get_plant(observed_objects)
        pv_plants = pv_plants.drop(columns=['type', 'parent'])
        pv_plants = pv_plants.rename(columns={"id": "plant_id"})
        pv_plants = pv_plants.rename(columns={"name": "plant_name"})

        module_list = []
        for id in pv_plants['plant_id']:
            module_list.append(self.get_plant_modules(observed_objects, id))
        pv_modules = pd.concat(module_list,ignore_index=True)
        pv_modules = pv_modules.rename(columns={"id": "string_id"})
        pv_modules = pv_modules.rename(columns={"name": "string_name"})
        pv_modules['parent'] = pv_modules['parent'].map(lambda parent: int(parent.split('/')[-1]))

        plant_x_modules = pd.merge(pv_plants, pv_modules, left_on='plant_id', right_on='parent')
        plant_x_modules = plant_x_modules.drop(columns=['parent'])

        meta_data_list = []
        for id in pv_modules['string_id']:
            tmp = pd.DataFrame(self.get_meta_data_by_id(id)['list'])
            if not tmp.empty:
                tmp = tmp.drop(columns=['description', 'id', 'type'])
                tmp = tmp.set_index('name')
                tmp = tmp.transpose()
                tmp.insert(1, 'string_id', id)
                meta_data_list.append(tmp)
                

        meta_data = pd.concat(meta_data_list,ignore_index=True)
        plant_x_modules_x_meta = pd.merge(plant_x_modules, meta_data, how="outer", on='string_id')
        plant_x_modules_x_meta.to_csv("res/meta_data.csv")

        return pv_modules

    def curves_to_file(self, observed_objects, pv_modules):
        dark_curves = self.get_curves(observed_objects, pv_modules, "ref://observedobjecttype/get/3")
        bright_curves = self.get_curves(observed_objects, pv_modules, "ref://observedobjecttype/get/4")

        dark_curves.to_csv("res/dark_curves.csv")
        bright_curves.to_csv("res/bright_curves.csv")

