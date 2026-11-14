FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --uid 10001 --create-home lab \
    && mkdir /data && chown lab:lab /data
COPY app app
COPY app_b app_b
COPY --chmod=755 scripts/start_django.sh /usr/local/bin/start-django
USER lab
ENTRYPOINT ["/usr/local/bin/start-django"]
