import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, required=True)
args = parser.parse_args()


df = pd.read_parquet(args.data)

index = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "similarity": {
            "dirichlet": {
                "type": "LMDirichlet"
            }
        }
    },
    "mappings": {
        "dynamic": "true",
        "_source": {
            "enabled": "true"
        },
        "properties": {
            "text": {"type": "text", "similarity":"dirichlet"},
            "cluster": {"type": "integer"},
            "centroid": {"type": "dense_vector", "dims": 512},
            "quality": {"type": "float"}
        }
    }
}

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


CLIENT = Elasticsearch()
INDEX_NAME = "argrank"
BATCH_SIZE = 1000

def index_batch(docs):
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME
        requests.append(request)
    bulk(CLIENT, requests)
    
CLIENT.indices.delete(index=INDEX_NAME, ignore=[404])
CLIENT.indices.create(index=INDEX_NAME, body=index)

docs = []
count = 0

for doc in df.iterrows():
    # Normalize doc to dict
    doc = doc[1].to_dict()
    doc["centroid"] = doc["centroid"].tolist()
    doc["text"] = doc["premise"] + " " + doc["conclusion"]
    del(doc["premise"])
    del(doc["conclusion"])
    docs.append(doc)
    count += 1
    
    # Index in batches
    if count % BATCH_SIZE == 0:
        index_batch(docs)
        docs = []
        print("Indexed {} documents.".format(count), end="\r")

if docs:
    index_batch(docs)
    print("Indexed {} documents.".format(count), end="\r")

CLIENT.indices.refresh(index=INDEX_NAME)
print("Done indexing.")