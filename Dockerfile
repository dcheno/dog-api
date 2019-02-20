# Use Python Docker Image
FROM python:3.7-slim

# Install Tornado via pip
RUN pip install tornado
RUN pip install requests

# Copy source code
COPY . .

WORKDIR .

# Set entry point
ENTRYPOINT ["python"]

# Set command for app
CMD ["dog_api.py"]

# Note: dog_api is currently hardset to run on port 8888,
# so make sure to map that one out when running the container.