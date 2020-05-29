FROM python:3.8

RUN apt-get update \
 && apt-get install --yes --no-install-recommends \
      graphviz \
 && rm -r /var/lib/apt/lists/*

RUN pip install \
      sphinx \
      matplotlib \
      graphviz

ENTRYPOINT ["/entrypoint.sh"]

COPY development/doc/entrypoint.sh /
RUN chmod +x /entrypoint.sh
