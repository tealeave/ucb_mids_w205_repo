FROM continuumio/anaconda3:2021.11

RUN ["/bin/bash", "-c", "rm /etc/localtime"]

RUN ["/bin/bash", "-c", "ln -s /usr/share/zoneinfo/US/Pacific /etc/localtime"]

RUN ["/bin/bash", "-c", "conda update -n base -c defaults conda"]

RUN ["/bin/bash", "-c", "pip install psycopg2-binary"]

RUN ["/bin/bash", "-c", "conda install -c conda-forge geographiclib"]

RUN ["/bin/bash", "-c", "conda install -c conda-forge gmaps"]

RUN ["/bin/bash", "-c", "conda install -c conda-forge fuzzywuzzy"]

RUN ["/bin/bash", "-c", "pip install jellyfish"]

RUN ["/bin/bash", "-c", "conda install -c anaconda pymongo"]

RUN ["/bin/bash", "-c", "pip install redis"]

RUN ["/bin/bash", "-c", "conda install -c conda-forge kafka-python"]

RUN ["/bin/bash", "-c", "conda install -c binstar gunicorn"]

RUN ["/bin/bash", "-c", "conda install -c anaconda beautifulsoup4"]

RUN ["/bin/bash", "-c", "pip install neo4j"]

RUN ["/bin/bash", "-c", "jupyter notebook --generate-config"]

COPY jupyter_notebook_config.py /root/.jupyter

COPY w205_cert.pem /root/.jupyter

COPY w205.key /root/.jupyter




