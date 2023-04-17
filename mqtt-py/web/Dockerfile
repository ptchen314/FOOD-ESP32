FROM python:3.12-rc-slim

COPY . /app
WORKDIR /app
RUN mkdir /app/log
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python","-u","web.py"]