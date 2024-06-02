# Stage 1: Install dependencies
FROM python:3.9 as dependencies

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx
WORKDIR /app

COPY . .

RUN python -m venv venv
RUN . venv/bin/activate

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port number the Flask app runs on
EXPOSE 5001

# Define environment variable
ENV AZURE_STORAGE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=kestra1cvops;AccountKey=Yrz/3SUhQUxToFl2x68UZvHnIh0hVXsj6BZvoEyCjdgbtGSFwdSrZJlgR9tJPIIo1c39t0iiSW8j+AStAW2TPA==;EndpointSuffix=core.windows.net'

# Run the application
CMD ["python", "src/app.py"]
