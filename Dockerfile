FROM python:3.11-slim
LABEL authors="belvisk"

ENTRYPOINT ["top", "-b"]


# Set working directory
WORKDIR /mimi_ecom

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files and run migrations (optional)
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# Run the app
CMD ["gunicorn", "mimi_ecom.wsgi:application", "--bind", "0.0.0.0:8000"]
