FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application files
COPY . /app/

# Expose port 8000 for Django
EXPOSE 8000

# Run migrations and start the server
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]