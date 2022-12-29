FROM python:3.7-slim
COPY app.py ./
RUN pip install numpy
CMD [ "python", "./app.py"]
