import ipfshttpclient
import json

dictionary = {
    "name": "sathiyajith",
    "rollno": 56,
    "cgpa": 8.6,
    "phonenumber": "9976770500"
}

json_object = json.dumps(dictionary, indent=4)

with open("./metadata_temp/sample.json", "w") as outfile:
    json.dump(dictionary, outfile)
client = ipfshttpclient.connect()  # Connects to: /dns/localhost/tcp/5001/http
res = client.add('./metadata_temp/sample.json')
print(res)