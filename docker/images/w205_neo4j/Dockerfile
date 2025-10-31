FROM neo4j:5.10

RUN ["/bin/bash", "-c", "rm /etc/localtime"]

RUN ["/bin/bash", "-c", "ln -s /usr/share/zoneinfo/US/Pacific /etc/localtime"]

RUN ["/bin/bash", "-c", "mkdir /var/lib/neo4j/certificates/https"]

RUN ["/bin/bash", "-c", "mkdir /var/lib/neo4j/certificates/bolt"]

COPY neo4j.conf /var/lib/neo4j/conf/neo4j.conf

COPY w205.key /var/lib/neo4j/certificates/https/private.key

COPY w205.key /var/lib/neo4j/certificates/bolt/private.key

COPY w205_cert.pem /var/lib/neo4j/certificates/https/public.crt

COPY w205_cert.pem /var/lib/neo4j/certificates/bolt/public.crt


