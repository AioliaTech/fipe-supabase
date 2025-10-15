import argparse
import logging
from database import SupabaseDB
from fipe_service import FipeAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Marcas específicas para sincronizar
MARCAS_CARROS = [
    'Fiat', 'Volkswagen', 'Chevrolet', 'Toyota', 'Hyundai', 'Renault', 
    'Jeep', 'Honda', 'BYD', 'Nissan', 'CAOA Chery', 'Ford', 'Citroën', 
    'GWM', 'RAM', 'Mitsubishi', 'Peugeot', 'BMW', 'Mercedes-Benz', 
    'Volvo', 'Land Rover', 'Audi', 'Kia', 'Subaru', 'Mazda', 
    'Jaguar', 'Porsche'
]

MARCAS_MOTOS = [
    'Honda', 'Yamaha', 'Shineray', 'Mottu', 'Avelloz', 'Royal Enfield',
    'Haojue', 'Dafra', 'BMW Motorrad', 'Kawasaki', 'Ducati', 
    'Triumph', 'Suzuki'
]

def normalizar_nome_marca(nome: str) -> str:
    """Normaliza nome da marca para comparação"""
    # Remove acentos e converte para minúsculas
    nome = nome.lower().strip()
    
    # Mapeamentos especiais
    mapeamentos = {
        'caoa chery': 'chery',
        'great wall': 'gwm',
        'great wall motors': 'gwm',
    }
    
    return mapeamentos.get(nome, nome)

def marca_esta_na_lista(marca_api: str, lista_marcas: list) -> bool:
    """Verifica se a marca da API está na lista desejada"""
    marca_normalizada = normalizar_nome_marca(marca_api)
    
    for marca_desejada in lista_marcas:
        if normalizar_nome_marca(marca_desejada) in marca_normalizada:
            return True
        if marca_normalizada in normalizar_nome_marca(marca_desejada):
            return True
    
    return False

def sync_fipe_to_supabase(tipo_veiculo: str, limite_marcas: int = None, marcas_filtradas: list = None):
    """
    Sincroniza dados da FIPE com o Supabase
    
    Args:
        tipo_veiculo: 'carros', 'motos' ou 'caminhoes'
        limite_marcas: Quantidade máxima de marcas (para teste)
        marcas_filtradas: Lista de marcas específicas para buscar
    """
    db = SupabaseDB()
    api = FipeAPI()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Iniciando sincronização de {tipo_veiculo.upper()}")
    logger.info(f"{'='*60}\n")
    
    # Buscar todas as marcas da API
    todas_marcas = api.obter_marcas(tipo_veiculo)
    
    # Filtrar apenas as marcas desejadas
    if marcas_filtradas:
        marcas = [m for m in todas_marcas if marca_esta_na_lista(m['nome'], marcas_filtradas)]
        logger.info(f"🎯 Filtrando {len(marcas)} de {len(todas_marcas)} marcas")
    else:
        marcas = todas_marcas
    
    if limite_marcas:
        marcas = marcas[:limite_marcas]
        logger.info(f"⚠️  MODO TESTE: Processando apenas {limite_marcas} marcas")
    
    total_marcas = len(marcas)
    
    for idx, marca in enumerate(marcas, 1):
        logger.info(f"\n[{idx}/{total_marcas}] Processando marca: {marca['nome']}")
        
        # Inserir marca
        marca_id = db.inserir_marca(
            codigo=marca['codigo'],
            nome=marca['nome'],
            tipo_veiculo=tipo_veiculo
        )
        
        if not marca_id:
            logger.warning(f"❌ Falha ao inserir marca {marca['nome']}")
            continue
        
        # Buscar modelos
        modelos = api.obter_modelos(tipo_veiculo, marca['codigo'])
        
        if not modelos:
            logger.warning(f"  ⚠️  Nenhum modelo encontrado")
            continue
        
        for modelo in modelos:
            # Inserir modelo
            modelo_id = db.inserir_modelo(
                codigo=modelo['codigo'],
                nome=modelo['nome'],
                marca_id=marca_id,
                tipo_veiculo=tipo_veiculo
            )
            
            if not modelo_id:
                continue
            
            # Buscar anos/versões
            anos = api.obter_anos(tipo_veiculo, marca['codigo'], str(modelo['codigo']))
            
            for ano in anos:
                # Buscar valor detalhado
                detalhes = api.obter_valor(
                    tipo_veiculo,
                    marca['codigo'],
                    str(modelo['codigo']),
                    ano['codigo']
                )
                
                if detalhes:
                    db.inserir_versao(
                        codigo=ano['codigo'],
                        nome=ano['nome'],
                        modelo_id=modelo_id,
                        tipo_veiculo=tipo_veiculo,
                        ano_modelo=detalhes.get('AnoModelo'),
                        combustivel=detalhes.get('Combustivel'),
                        codigo_fipe=detalhes.get('CodigoFipe'),
                        mes_referencia=detalhes.get('MesReferencia'),
                        valor=detalhes.get('Valor')
                    )
        
        logger.info(f"✅ Marca {marca['nome']} concluída!")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Sincronização de {tipo_veiculo.upper()} finalizada!")
    logger.info(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description='Sincronizar dados FIPE com Supabase')
    parser.add_argument('--test', action='store_true', help='Modo teste (apenas 2 marcas)')
    parser.add_argument('--tipo', choices=['carros', 'motos', 'caminhoes', 'todos'], 
                       default='todos', help='Tipo de veículo')
    
    args = parser.parse_args()
    
    limite = 2 if args.test else None
    
    try:
        if args.tipo in ['carros', 'todos']:
            sync_fipe_to_supabase('carros', limite, MARCAS_CARROS)
        
        if args.tipo in ['motos', 'todos']:
            sync_fipe_to_supabase('motos', limite, MARCAS_MOTOS)
        
        # Caminhões desabilitado (não tem lista específica)
        # if args.tipo == 'caminhoes':
        #     sync_fipe_to_supabase('caminhoes', limite)
        
        logger.info("\n🎉 Processo completo!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Processo interrompido pelo usuário")
    except Exception as e:
        logger.error(f"\n❌ Erro fatal: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
