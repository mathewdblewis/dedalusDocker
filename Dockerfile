FROM python:3.7-slim
COPY test.py ./
RUN pip install numpy
CMD [ "python", "./test.py"]
