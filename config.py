import json
import os

try:
    f = open("config.json")
    data = json.load(f)
    f.close()
except:
    data = {
        "TOKEN": os.environ["TOKEN"],
        "APPLICATION_ID": os.environ["APPLICATION_ID"],
        "MONGO_USER": os.environ["MONGO_USER"],
        "MONGO_PASSWORD": os.environ["MONGO_PASSWORD"]
    }