# TOUCHE-21:  Argument Retrieval for Controversial Questions
**Submission of Team Heimdall**


Submission to the Touche-21 Shared Task on argument retrieval for controversial questions. For detailed information, refer to the associated paper published at CLEF 2021.

## Usage

1. Start the container with `docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.1`
2. Run the notebooks in their enumerated order

Note: for automated usage, `run.sh` can be invoked with a given data file as produced by `04-Consolidate.ipynb`.
