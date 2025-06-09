FROM vellumai/python-workflow-runtime:latest

RUN pip install --upgrade pip \
    && pip install boto3 \
    && pip install mcp

COPY ./utils /custom/utils

ENV PYTHONPATH="${PYTHONPATH}:/custom"
CMD ["vellum_start_server"]
