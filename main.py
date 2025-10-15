from fipe_service import FipeService
from database import SupabaseDB
import time

def sync_fipe_to_supabase():
    """Sincroniza dados da FIPE para o Supabase"""
    
    fipe = FipeService()
    db = SupabaseDB()
    
    print("🚀 Iniciando sincronização FIPE -> Supabase\n")
    
    for tipo_veiculo in fipe.tipos_veiculo:
        print(f"\n{'='*60}")
        print(f"📋 Processando: {tipo_veiculo.upper()}")
        print(f"{'='*60}\n")
        
        # 1. Buscar e inserir marcas
        marcas = fipe.get_marcas(tipo_veiculo)
        print(f"✓ Encontradas {len(marcas)} marcas de {tipo_veiculo}")
        
        for idx, marca in enumerate(marcas, 1):
            print(f"\n[{idx}/{len(marcas)}] Processando marca: {marca['nome']}")
            
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
                time.sleep(0.5)
            
            print(f"  ✅ Marca {marca['nome']} concluída!")
    
    print("\n" + "="*60)
    print("🎉 Sincronização concluída!")
    print("="*60)

if __name__ == "__main__":
    sync_fipe_to_supabase()
