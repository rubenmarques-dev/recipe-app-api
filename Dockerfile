FROM python:3.9-alpine3.13
LABEL maintainer="rubenmarques86@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

COPY ./app /app
WORKDIR /app
EXPOSE 8000

# will be update on docker compose
ARG DEV=false

 ## python environment is created to avoid conflicts on dependencies with the docker image, install pip, copy and install requirements, remove /tmp to be lightweighted, new user on image (not use root user)
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
          --disabled-password \
          --no-create-home \
          django-user

## overwrite environment path on the image
ENV PATH="/py/bin:$PATH"

USER django-user