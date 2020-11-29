FROM python:3.8-slim
RUN pip3 install flask
WORKDIR /workdir
COPY . .
CMD ["python", "main.py"]
