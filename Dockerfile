# =========================
# Streamlit App Dockerfile
# =========================

# Use an official Python base image
FROM python:3.12-slim

# Set environment variables to prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a working directory inside the container
WORKDIR /app

# Copy Fortinet certificate into container
COPY Fortinet_CA_SSL(15).cer /usr/local/share/ca-certificates/Fortinet_CA_SSL.crt

# Install system dependencies for psycopg2, numpy, pandas, etc.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set certificate environment variables globally (so pip, requests, etc. trust Fortinet)
ENV SSL_CERT_FILE=/usr/local/share/ca-certificates/Fortinet_CA_SSL.crt
ENV REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/Fortinet_CA_SSL.crt    

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .

# Use psycopg2-binary instead of psycopg2 for easier installation
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org


# Copy all project files into the container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Streamlit configuration (disable telemetry, allow external access)
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRSFPROTECTION=false
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]


# # =========================
# # Streamlit App Dockerfile
# # =========================

# # Use an official Python base image
# FROM python:3.12-slim

# # Set environment variables to prevent Python from buffering stdout/stderr
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Create a working directory inside the container
# WORKDIR /app

# # Install system dependencies for psycopg2, numpy, pandas, etc.
# RUN apt-get update && apt-get install -y \
#     libpq-dev \
#     gcc \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements.txt and install Python dependencies
# COPY requirements.txt .

# # Use psycopg2-binary instead of psycopg2 for easier installation
# # RUN pip install --no-cache-dir -r requirements.txt
# # RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org


# # Copy all project files into the container
# COPY . .

# # Expose Streamlit's default port
# EXPOSE 8501

# # Streamlit configuration (disable telemetry, allow external access)
# ENV STREAMLIT_SERVER_ENABLECORS=false
# ENV STREAMLIT_SERVER_ENABLEXSRSFPROTECTION=false
# ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# # Run the Streamlit app
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
