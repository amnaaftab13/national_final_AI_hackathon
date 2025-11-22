# 1. Base Image: Python 3.13 
FROM python:3.13

# 2. Working Directory 
WORKDIR /app

# 3. Dependencies 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. container at /app
COPY main.py . 

# 5. Environment variable 
ENV PORT 8002

# 6. uvicorn.run()
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]