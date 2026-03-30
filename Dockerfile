# 1. Start with a lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory
WORKDIR /app

# 3. Install the compiler tools (The missing "hammer and nails")
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your code and the 2GB AI model
COPY main.py .
COPY Llama-3.2-3B-Instruct-Q4_K_M.gguf .

# 6. Open the port
EXPOSE 8000

# 7. Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]