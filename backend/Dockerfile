FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p uploads/pdfs
# Generate gRPC code from proto files
RUN python scripts/generate_grpc.py || true
EXPOSE 8000
EXPOSE 50051
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

