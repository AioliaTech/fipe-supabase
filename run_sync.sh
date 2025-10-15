#!/bin/bash

echo "=================================================="
echo "FIPE Sync - Iniciado em $(date '+%d/%m/%Y %H:%M:%S')"
echo "=================================================="

cd /app

python main.py

if [ $? -eq 0 ]; then
    echo "✅ Sincronização concluída com sucesso!"
else
    echo "❌ Erro na sincronização!"
fi

echo "Finalizado em $(date '+%d/%m/%Y %H:%M:%S')"
echo ""
