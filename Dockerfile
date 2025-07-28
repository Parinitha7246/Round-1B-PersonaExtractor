# Use official slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies required by PyMuPDF and fonts
RUN apt-get update && \
    apt-get install -y \
    build-essential gcc g++ \
    libgl1-mesa-glx libglib2.0-0 libxrender1 libxext6 libsm6 \
    && rm -rf /var/lib/apt/lists/*

# Copy your project into the container
COPY . /app

# Upgrade pip first
RUN pip install --upgrade pip

# Install core packages that sometimes fail inside slim
RUN pip install --no-cache-dir \
    PyMuPDF==1.23.19 \
    sentence-transformers==2.2.2 \
    torch>=1.10 \
    scikit-learn \
    transformers>=4.39.3

# Install your project requirements (remainder)
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "main.py"]
