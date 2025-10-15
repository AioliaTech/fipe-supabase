from fipe_service import FipeService
from database import SupabaseDB
import time
import sys
import argparse

def sync_fipe_to_supabase(tipo_veiculo_especifico=None, limite_marcas=None):
    """
    Sincroniza dados da FIPE para o Supabase
    
    Args:
        tipo_veiculo_especifico: 'carros', 'motos', ou 'caminhoes' (None para todos)
        limite_marcas: Limitar número de marcas processadas (útil para testes)
    """
    
    fipe = FipeService()
    db = SupabaseDB()
    
    print("🚀 Iniciando sincronização FIPE -> Supabase\n")
    
    tipos = [tipo_veiculo_especifico] if tipo_veiculo_especifico else fipe.tipos_veiculo
    
    for tipo_veiculo in tipos:
        print(f"\n{'='*60}")
        print(f"📋 Processando: {tipo_veiculo.upper()}")
        print(f"{'='*60}\n")
        
        # 1. Buscar e inserir marcas
        marcas = fipe.get_marcas(tipo_veiculo)
        
        # Limitar marcas se especificado (útil para testes)
        if limite_marcas:
            marcas = marcas[:limite_marcas]
        
        print(f"✓ Encontradas {len(marcas)} marcas de {tipo_veiculo}")
        
        for idx, marca in enumerate(marcas, 1):
            print(f"\n[{idx}/{len(marcas)}] Processando marca: {marca['nome']}")
            
            try:
                # Inserir marca
                marca_inserida = db.insert_marca(marca)
                if not marca_inserida:
                    marca_inserida = db.get_marca_by_codigo(marca['codigo'], tipo_veiculo)
                
                if not marca_inserida:
                    print(f"  ⚠️  Erro ao processar marca {marca['nome']}")
                    continue
                
                marca_id = marca_inserida['id']
                
                # 2. Buscar e inserir modelos
                modelos = fipe.get_modelos(tipo_veiculo, marca['codigo'])
                print(f"  ✓ {len(modelos)} modelos encontrados")
                
                for modelo in modelos:
                    modelo_inserido = db.insert_modelo(modelo, marca_id)
                    if not modelo_inserido:
                        modelo_inserido = db.get_modelo_by_codigo(
                            modelo['codigo'], marca_id, tipo_veiculo
                        )
                    
                    if not modelo_inserido:
                        continue
                    
                    modelo_id = modelo_inserido['id']
                    
                    # 3. Buscar e inserir versões (anos)
                    anos = fipe.get_anos(tipo_veiculo, marca['codigo'], modelo['codigo'])
                    
                    for ano in anos:
                        versao = fipe.get_versao(
                            tipo_veiculo, marca['codigo'], modelo['codigo'], ano
                        )
                        if versao:
                            db.insert_versao(versao, modelo_id)
                    
                    # Delay para não sobrecarregar a API
                    time.sleep(0.3)
                
                print(f"  ✅ Marca {marca['nome']} concluída!")
                
            except Exception as e:
                print(f"  ❌ Erro ao processar marca {marca['nome']}: {e}")
                continue
    
    print("\n" + "="*60)
    print("🎉 Sincronização concluída!")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Sincroniza dados da FIPE para Supabase')
    parser.add_argument('--tipo', choices=['carros', 'motos', 'caminhoes'], 
                        help='Tipo de veículo específico')
    parser.add_argument('--limite', type=int, 
                        help='Limitar número de marcas (útil para testes)')
    parser.add_argument('--test', action='store_true',
                        help='Modo teste: processa apenas 2 marcas de carros')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Modo TESTE ativado - processando apenas 2 marcas de carros\n")
        sync_fipe_to_supabase(tipo_veiculo_especifico='carros', limite_marcas=2)
    else:
        sync_fipe_to_supabase(
            tipo_veiculo_especifico=args.tipo,
            limite_marcas=args.limite
        )

if __name__ == "__main__":
    main()
