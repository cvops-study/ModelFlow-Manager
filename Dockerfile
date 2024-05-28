# Stage 1: Install dependencies
FROM python:3.8-slim-buster as dependencies

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt



# Stage 3: Create the final image
FROM python:3.8-slim-buster

LABEL authors="nada"

WORKDIR /app

COPY --from=dependencies /app /app

# Expose the port number the Flask app runs on
EXPOSE 5001

# Define environment variable
ENV AZURE_STORAGE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=kestra1cvops;AccountKey=Yrz/3SUhQUxToFl2x68UZvHnIh0hVXsj6BZvoEyCjdgbtGSFwdSrZJlgR9tJPIIo1c39t0iiSW8j+AStAW2TPA==;EndpointSuffix=core.windows.net'

# Run the application
CMD ["python", "/src/app.py"]
