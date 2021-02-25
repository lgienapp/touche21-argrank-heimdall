import tensorflow_hub as hub
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--topic_path', type=str, required=True)
parser.add_argument('--output_path', type=str, required=True)
args = parser.parse_args()




def perform_query(query_text, w_r=1, w_c=1, w_q=1, k=1000, index="argrank"):
    query_vector = embed([query_text]).numpy()[0].tolist()
    script_query = {
        "script_score": {
            "query": {
                "match" : {
                    "text" : {
                        "query" : query_text
                    }
                }
            },
            "script": {
                "source": "_score * (1 + params.w_c * (cosineSimilarity(params.query_vector, 'centroid') + 1)) * (1 + params.w_q * doc['quality'].value)",
                "params": {
                    "query_vector": query_vector,
                    "w_c": w_c,
                    "w_q": w_q
                }
            }
        }
    }
    
    res = CLIENT.search(
        index=index,
        body={
            "size": k,
            "query": script_query,
             "_source": {"includes": ["id"]}
        },
    )
    return res["hits"]["hits"]

def parse_query(res):
    return {"id": res["_source"]["id"], "score": res["_score"]}


CLIENT = Elasticsearch()


tree = ET.parse(args.topic_path)
root = tree.getroot()
topics = []
for child in root:
    d = {'topic_number':int(child[0].text), 'topic_query':child[1].text}
    topics.append(d)
topics = pd.DataFrame(topics)


w_c = 1
w_q = 1
print("Retrieving for weights:", w_c, w_q)

for _, row in topics.iterrows():
    number = row['topic_number']
    query = row['topic_query']

    print(f'Now working on query {number}: {query}')
    res = list(map(parse_query, perform_query(query, w_c=w_c, w_q=w_q)))


    final_ranks = pd.DataFrame(res)
    final_ranks = final_ranks.sort_values(by='score', ascending=False)
    final_ranks['rank'] = np.arange(len(final_ranks)) + 1
    final_ranks['method'] = 'argrank_'+str(w_c)+'-'+str(w_q)
    final_ranks['Q0'] = "Q0"
    final_ranks['topic_number'] = number


    with open(args.output_path, 'a+') as f:
        final_ranks[['topic_number', 'Q0', 'id', 'rank', 'score', 'method']].to_csv(f, sep=' ', header=False, index=False)

