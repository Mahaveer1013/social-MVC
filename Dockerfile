# Use the official Python image as the base image
FROM python:3.11

# Create a virtual environment within the container
RUN python -m venv /app/venv

# Activate the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies using pip in the virtual environment
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Set the working directory in the container
WORKDIR /app

# Define the entry point for the container
CMD ["flask", "run", "--host=0.0.0.0"]