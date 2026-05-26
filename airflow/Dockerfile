FROM apache/airflow:latest-python3.12

# Salin file requirements ke dalam kontainer
COPY ./requirements.txt /requirements.txt

# Upgrade pip dan instal modul ke user-space airflow
RUN pip install --no-cache-dir --user -r /requirements.txt