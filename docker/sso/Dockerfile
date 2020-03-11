FROM python:latest AS py-runtime

ENV APP /app
RUN mkdir $APP
WORKDIR $APP

EXPOSE 3000

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT [ "python" ]
CMD ["sso.py"]

