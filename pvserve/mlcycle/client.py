import os
import mlcycle
import pandas as pd

from tensorflow.keras.models import load_model

class Client:
    client=None

    def __init__(self):
        is_local = "MLCYCLE_HOST" not in os.environ
        if not is_local:
            self.client = mlcycle.from_env()
        else:
            if not os.path.exists('workdir'):
                os.mkdir('workdir')

    def upload(self, fragment, fd):
        if self.client is None:
            path = os.path.join("workdir", fragment['filename'])

            with open(path, 'wb') as f:
                while True:
                    data = fd.read(1024 * 1024)
                    if not data:
                        break
                    f.write(data)
        else:
            self.client.Fragments.upload(fragment, fd)

    def upload_frag(self, name, filename, type):

        fragment = {
            'name': name,
            'filename': filename,
            'type': type
        }

        with open(filename, 'rb') as f:
            self.upload(fragment, f)

        os.remove(filename)


    def upload_dataframe(self, df, name, filename, type=1):
        df.to_csv(filename)

        self.upload_frag(name, filename, type)

    def upload_plot(self, fig, name, filename, type=0):
        fig.savefig(filename)

        self.upload_frag(name, filename, type)

    def upload_model(self, model, name, filename, type=2):
        model.save(filename)

        self.upload_frag(name, filename, type)

    def download(self, name, fd):
        if self.client is None:
            path = os.path.join("workdir", name)

            with open(path, 'rb') as src:
                while True:
                    data = src.read(1024 * 1024)
                    if not data:
                        break
                    fd.write(data)
        else:
            self.client.Fragments.getLatestByJob(name, fd)

    def download_dataframe(self, name, **kwargs):
        with open(name, "wb") as f:
            self.download(name, f)
        
        df = pd.read_csv(name, **kwargs)

        os.remove(name)

        return df

    def download_model(self, name):
        with open(name, "wb") as f:
            self.download(name, f)

        model = load_model(name)

        os.remove(name)

        return model


    
    def add_metrics(self, metrics):
        if self.client is not None:
            self.client.Jobs.addMetrics(metrics)
        