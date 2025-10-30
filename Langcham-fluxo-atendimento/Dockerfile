# ========================================
# Dockerfile - WhatsApp Bot LangChain
# ========================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Vinicius Soutenio"
LABEL description="WhatsApp Bot com LangChain, LangGraph e Evolution API"
LABEL version="1.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/logs

# Expor portas (8000 e 8001 para dev)
EXPOSE 8000 8001

# Health check (usa variável PORT se disponível, senão 8000)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Comando de inicialização (usa variável PORT se disponível, senão 8000)
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
