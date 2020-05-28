ARG python_version
FROM python:$python_version

COPY requirements-gantt.txt requirements-dependency_graphs.txt /
RUN pip install -r /requirements-gantt.txt -r /requirements-dependency_graphs.txt

ENTRYPOINT ["/entrypoint.sh"]

COPY development/tests/entrypoint.sh /
RUN chmod +x /entrypoint.sh
