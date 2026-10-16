# Start with a lightweight image that already has Python installed.
FROM python:3.14-slim

# Set the working directory inside the container.
WORKDIR /app

# Prevent Python from creating unnecessary .pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Make Python logs appear immediately in the container logs.
ENV PYTHONUNBUFFERED=1

# Copy the dependency list first so Docker can reuse this layer
# when the application code changes but the dependencies stay the same.
COPY requirements.txt .

# Install the packages required by the application.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining project files into the container.
COPY . .

# Document the port used by the API.
EXPOSE 8000

# Start the FastAPI application using Uvicorn.
# Use the hosting platform's PORT variable when available, otherwise use 8000.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]