FROM python:3.9.19-alpine3.20

ADD serverhandler.py .

RUN pip install mcstatus docker python-dotenv

CMD ["python", "./serverhandler.py"]
