FROM python:3.12-slim

WORKDIR /app

# Installazione dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia del codice sorgente mantenendo la struttura delle cartelle
COPY . .

# Variabile d'ambiente per evitare il buffering dei log
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]