import os
import mlcycle

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
    
    def add_metrics(self, metrics):
        if self.client is not None:
            self.client.Jobs.addMetrics(metrics)
        