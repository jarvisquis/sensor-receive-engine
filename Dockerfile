FROM python:3.7-alpine as baseStage
WORKDIR /app
COPY rf_data_parse rf_data_parse
COPY rf_receive rf_receive
COPY requirements.txt .
RUN apk add gcc musl-dev
RUN pip --no-cache-dir install -r requirements.txt

FROM baseStage
COPY test test
RUN python -m unittest discover -t ./test -s ./test

FROM baseStage
COPY main.py .
CMD python main.py