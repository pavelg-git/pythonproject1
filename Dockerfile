FROM python:3.9.9-slim
WORKDIR /app
COPY requirements.txt client_resource_final_no_cred.py ./
RUN pip install -r requirements.txt
CMD ["python", "client_resource_final_no_cred.py"]