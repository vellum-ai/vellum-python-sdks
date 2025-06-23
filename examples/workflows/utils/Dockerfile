FROM vellumai/python-workflow-runtime:latest

RUN pip install --upgrade pip \
    && pip install boto3 \
    && pip install mcp

# Install Docker (daemon and CLI)
RUN apt-get update && apt-get install -y docker.io

COPY ./utils /custom/utils
ENV PYTHONPATH="${PYTHONPATH}:/custom"

CMD dockerd & vellum_start_server
