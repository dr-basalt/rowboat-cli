FROM python:3.12-slim

# Node 20 pour npx / rowboatx
RUN apt-get update && apt-get install -y curl ca-certificates gnupg \
  && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
     | gpg --dearmor -o /etc/apt/trusted.gpg.d/nodesource.gpg \
  && echo "deb https://deb.nodesource.com/node_20.x nodistro main" \
     > /etc/apt/sources.list.d/nodesource.list \
  && apt-get update && apt-get install -y nodejs \
  && npm install -g npm \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Dossier de travail
WORKDIR /app

# Script rowboatx-multi
COPY scripts/rowboatx-multi /usr/local/bin/rowboatx-multi
RUN chmod +x /usr/local/bin/rowboatx-multi

# FastAPI app
COPY app/ app/
RUN pip install fastapi uvicorn

# Dossier de data persistant
RUN mkdir -p /data/rowboat
VOLUME ["/data/rowboat"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
