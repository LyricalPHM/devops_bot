FROM python:3.9-slim

WORKDIR /app
COPY bot.py .
RUN pip install psycopg2-binary paramiko python-dotenv requests python-telegram-bot==13.7

CMD ["python", "bot.py"]
