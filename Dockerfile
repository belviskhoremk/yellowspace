FROM python:3.11-slim
LABEL authors="belvisk"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /mimi_ecom

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Create directories for static and media files
RUN mkdir -p /mimi_ecom/staticfiles
RUN mkdir -p /mimi_ecom/media

# Make sure the port is available
EXPOSE 8000

# Use a startup script instead of running migrations in build
COPY start.sh .
RUN chmod +x start.sh

# Run the startup script
CMD ["./start.sh"]