FROM python:3.10

WORKDIR /app
# Установка LibreOffice должна быть здесь (до копирования кода)
RUN apt-get update && apt-get install -y \
    libreoffice \
    xvfb \
    fonts-dejavu \
    fontconfig \
    cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# RUN mkdir -p /etc/www/storage
RUN mkdir -p /var/sbz
# Копируем приложение
COPY src /app
COPY requirements.txt /app/requirements.txt
RUN find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf

# Устанавливаем зависимости
RUN ls -l /app
RUN pip install uvicorn
RUN pip install -r /app/requirements.txt
# RUN pip install -r /app/utils/sbz/requirements.txt
RUN pip install -r /app/utils/service/requirements.txt

# Копируем сертификаты
# RUN mkdir -p /etc/ssl/certs
# RUN mkdir -p /etc/ssl/private
# COPY resources/cert/pub/*.pem /etc/ssl/certs
# COPY resources/cert/prv/*.pem /etc/ssl/private

# Копируем настройки
COPY resources/setting/docker.setting.json /etc/setting.json

# --- НАСТРОЙКА CRON ---
# RUN echo "0 3 1 * * root /usr/bin/find /var/sbz -type f -mtime +1 -delete" > /etc/cron.d/cache-cleaner
RUN echo "*/5 * * * * root /usr/bin/find /var/sbz/pdf_output/ -type f -mmin +5 -delete > /proc/1/fd/1 2>&1" > /etc/cron.d/cache-cleaner

EXPOSE 80
# WORKDIR /app

# CMD ["uvicorn", "main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "80"]
CMD cron && uvicorn main:app --workers 4 --host 0.0.0.0 --port 80