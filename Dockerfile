FROM python:3.11-slim

# Prevent python cache files and enable immediate container logs

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# build-essential supports packages that require compilation
# libgomp1 is commonly required by faiss-cpu

RUN apt-get update && apt-get install -y --no-install-recommends \	
	build-essential\
	libgomp1 \
	&& rm -rf /var/lib/apt/lists/*

#copy requirements first for docker build caching

COPY requirements.txt .

# Install python dependencies

RUN python -m pip install --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt


# Copy the complete project
COPY . .

# exposing the app to the port number 8501
EXPOSE 8501

CMD ["streamlit", "run", "app.py",\
    "--server.port = 8501", \
	"--server.address=0.0.0.0", \
	"--server.headless=true", \
	"--browser.gatherUsageStats=false"]