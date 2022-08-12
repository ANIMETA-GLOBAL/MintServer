import ipfshttpclient
import json
import config
import uuid

class AnimetaIPFS(object):

    def __init__(self):
        self.client = ipfshttpclient.connect()

    def upload(self, metadata):
        file_id = uuid.uuid1()
        with open(config.metadata_temp_dir + f"/{file_id}.json", "w") as outfile:
            json.dump(metadata, outfile)

        res = self.client.add(config.metadata_temp_dir + f"/{file_id}.json")

        return res


if __name__ == '__main__':
    metadata = {
        "name": "test",
        "description": "test"
    }

    metadata_json = json.dumps(metadata)

    print(AnimetaIPFS().upload(metadata))
