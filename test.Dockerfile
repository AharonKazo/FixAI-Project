FROM python:3.12-slim
WORKDIR /tests
COPY requirements.txt .
COPY testserver.py .
RUN pip install -r requirements.txt pytest
CMD ["pytest", "testserver.py"]