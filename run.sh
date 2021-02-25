#!/bin/sh
while getopts ":i:o:" opt; do
  case $opt in
    i)
      in_dir=$OPTARG
      ;;
    o)
      out_dir=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

set -e
set -x

docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.1

python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt

python3 05-index.py --data data/index.parquet
python3 06-query.py --topic_path $in_dir/topics.xml --output_path $out_dir/run.txt