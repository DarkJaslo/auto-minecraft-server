FROM python:3.9.19

ADD serverhandler.py .

RUN apt-get update && apt-get install -y docker.io
RUN pip install mcstatus docker python-dotenv

CMD [ "python", "./serverhandler.py"]
