# Use Python as the base for the backend
FROM python:3.9-slim

# Install C++ compiler tools
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the project file
COPY . .

# Install python dependecies
RUN pip install --no-cache-dir fastapi uvicorn requests

# Copile the ECU Monitor for Linux
# We replace the .exe with a Linux binary named "ecu_monitor.bin"
RUN gcc -c firmware/src/sensor_logic.c -I firmware/include -o sensor_logic.o && \
    g++ firmware/src/main.cpp sensor_logic.o -I firmware/include -o firmware/ecu_monitor.bin

# Expose the API port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "backend.main_api:app", "--host", "0.0.0.0", "--port", "8000"]