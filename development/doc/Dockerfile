FROM python:3.8

RUN apt-get update \
 && apt-get install --yes --no-install-recommends \
      graphviz \
 && rm -r /var/lib/apt/lists/*

# @todo Upgrade Sphinx version
RUN pip install \
      sphinx==1.8.2 \
      matplotlib \
      graphviz

ENTRYPOINT ["/entrypoint.sh"]

COPY development/doc/entrypoint.sh /
RUN chmod +x /entrypoint.sh
