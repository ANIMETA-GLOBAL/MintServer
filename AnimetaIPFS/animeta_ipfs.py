import ipfshttpclient
import json
import config

dictionary = {
    "name": "sathiyajith",
    "rollno": 56,
    "cgpa": 8.6,
    "phonenumber": "9976770500"
}


#
# json_object = json.dumps(dictionary, indent=4)
#
# with open("./metadata_temp/sample.json", "w") as outfile:
#     json.dump(dictionary, outfile)
# client = ipfshttpclient.connect()  # Connects to: /dns/localhost/tcp/5001/http
# res = client.add('./metadata_temp/sample.json')
# print(res)


class AnimetaIPFS(object):

    def __init__(self):
        self.client = ipfshttpclient.connect()

    def upload(self, metadata):
        with open(config.metadata_temp_dir + f"/{metadata['name']}.json", "w") as outfile:
            json.dump(metadata, outfile)

        res = self.client.add(config.metadata_temp_dir + f"/{metadata['name']}")

        return res


if __name__ == '__main__':
    metadata = {
        "name": "test",
        "description": "test"
    }

    metadata_json = json.dumps(metadata)

    print(AnimetaIPFS().upload(metadata))
