# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy the project folder into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run migrations
RUN python mealgenie/manage.py migrate

# Expose the port
EXPOSE 8000

# Run the Django app
CMD ["python", "mealgenie/manage.py", "runserver", "0.0.0.0:8000"]