#!/usr/bin/env python3
"""
Script para iniciar o bot localmente na porta 8001
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Iniciando WhatsApp Bot na porta 8001...")
    print("📁 Diretório atual:", os.getcwd())
    
    # Verificar se estamos no diretório correto
    if not Path("src/main.py").exists():
        print("❌ Erro: arquivo src/main.py não encontrado")
        print("💡 Execute este script na raiz do projeto")
        return
    
    # Verificar se o arquivo .env existe
    if not Path(".env").exists():
        print("⚠️  Aviso: arquivo .env não encontrado")
        print("💡 Certifique-se de ter todas as variáveis de ambiente configuradas")
    
    try:
        # Definir a porta 8001 como variável de ambiente
        env = os.environ.copy()
        env["PORT"] = "8001"
        
        print("🔧 Configurações:")
        print(f"   Porta: 8001")
        print(f"   Host: 0.0.0.0")
        print(f"   Ambiente: development")
        print()
        
        # Executar o uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ]
        
        print("▶️  Executando:", " ".join(cmd))
        print("📡 URL local: http://localhost:8001")
        print("🔗 Health check: http://localhost:8001/health")
        print("📚 Docs: http://localhost:8001/docs")
        print()
        print("⏹️  Para parar o servidor, pressione Ctrl+C")
        print("=" * 60)
        
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()