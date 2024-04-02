# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster
# FROM --platform=linux/amd64 python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install necessary packages
RUN apt-get update && apt-get install -y \
    g++ \
    unixodbc-dev \
    curl \
    gnupg

# Install Microsoft ODBC 18
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18



RUN apt-get update && apt-get install -y unixodbc

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r amqp.reqs.txt

# Run refund.py when the container launches
CMD ["python", "Bidding_Records.py"]

# Expose the port the app runs in
EXPOSE 5008