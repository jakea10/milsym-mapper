FROM python:3.11-slim-buster

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
