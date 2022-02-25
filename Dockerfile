FROM python:3.10

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.1.12 \
#    CPLUS_INCLUDE_PATH=/usr/include/gdal \
#    C_INCLUDE_PATH=/usr/include/gdal \
    TZ='Asia/Kathmandu'

WORKDIR /usr/src/app

RUN echo $TZ > /etc/timezone && \
    apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

RUN apt-get update && apt-get install -y netcat #libgdal-dev locales

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
  && poetry lock \
  && poetry install --no-interaction --no-ansi

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project #
COPY . /usr/src/app

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
