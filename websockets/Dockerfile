FROM python

#ENV PYTHONUNBUFFERED=1
ENV INITRD No
ENV LANG en_US.UTF-8
ENV WEBSKD_VERSION 0.4.1

RUN wget https://github.com/joewalnes/websocketd/releases/download/v$WEBSKD_VERSION/websocketd-$WEBSKD_VERSION\_amd64.deb && \
    dpkg -i websocketd-$WEBSKD_VERSION\_amd64.deb && \
    rm websocketd-$WEBSKD_VERSION\_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install redis

COPY subscribe.py /
EXPOSE 8181
ENTRYPOINT /usr/bin/websocketd --port=8181 /subscribe.py
