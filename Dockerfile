# ==========================================
# STAGE 1: Build the Next.js Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy source and build static export
COPY frontend/ ./
RUN npm run build

# ==========================================
# STAGE 2: Build the FastAPI Python Server
# ==========================================
FROM python:3.11-slim AS runner
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend

# Copy built Next.js static assets into FastAPI static directory
COPY --from=frontend-builder /app/frontend/out ./backend/static

# Expose dynamic Render port (defaults to 10000)
ENV PORT=10000
EXPOSE 10000

# Run the FastAPI server using shell to evaluate the environment port
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
