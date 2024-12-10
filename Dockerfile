# Python base image
FROM python:3.12-slim

# Set the working directory (in container)
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Make the test script executable
RUN chmod +x run_ArtLang.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command: Run all tests using run_ArtLang.sh
ENTRYPOINT ["./run_ArtLang.sh"]