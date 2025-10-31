FROM confluentinc/cp-kafka:7.9.0

USER root

RUN ["/bin/bash", "-c", "rm /etc/localtime"]

RUN ["/bin/bash", "-c", "ln -s /usr/share/zoneinfo/US/Pacific /etc/localtime"]

USER appuser

