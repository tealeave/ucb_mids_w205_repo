FROM postgres:14

RUN ["/bin/bash", "-c", "rm /etc/localtime"]

RUN ["/bin/bash", "-c", "ln -s /usr/share/zoneinfo/US/Pacific /etc/localtime"]

RUN ["/bin/bash", "-c", "groupadd -g 1001 mids"]

RUN ["/bin/bash", "-c", "usermod -a -G mids postgres"]



