FROM vellumai/python-workflow-runtime:latest

COPY ./utils /custom/utils

ENV PYTHONPATH="${PYTHONPATH}:/custom"
CMD ["vellum_start_server"]
