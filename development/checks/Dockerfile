FROM python:3.8

ENTRYPOINT ["/entrypoint.sh"]

RUN pip install docutils pycodestyle

COPY development/checks/entrypoint.sh /
RUN chmod +x /entrypoint.sh
