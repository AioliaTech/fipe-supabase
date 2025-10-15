from supabase import create_client, Client
from config import Config
from typing import List, Dict, Any

class SupabaseDB:
    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    
    def insert_marca(self, marca: Dict[str, Any]) -> Dict[str, Any]:
        """Insere uma marca no banco"""
        try:
            response = self.client.table('marcas').upsert({
                'codigo': marca['codigo'],
                'nome': marca['nome'],
                'tipo_veiculo': marca['tipo_veiculo']
            }, on_conflict='codigo,tipo_veiculo').execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao inserir marca: {e}")
            return None
    
    def insert_modelo(self, modelo: Dict[str, Any], marca_id: int) -> Dict[str, Any]:
        """Insere um modelo no banco"""
        try:
            response = self.client.table('modelos').upsert({
                'codigo': modelo['codigo'],
                'nome': modelo['nome'],
                'marca_id': marca_id,
                'tipo_veiculo': modelo['tipo_veiculo']
            }, on_conflict='codigo,marca_id,tipo_veiculo').execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao inserir modelo: {e}")
            return None
    
    def insert_versao(self, versao: Dict[str, Any], modelo_id: int) -> Dict[str, Any]:
        """Insere uma versão no banco"""
        try:
            response = self.client.table('versoes').upsert({
                'codigo': versao['codigo'],
                'nome': versao['nome'],
                'modelo_id': modelo_id,
                'tipo_veiculo': versao['tipo_veiculo']
            }, on_conflict='codigo,modelo_id,tipo_veiculo').execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao inserir versão: {e}")
            return None
    
    def get_marca_by_codigo(self, codigo: str, tipo_veiculo: str) -> Dict[str, Any]:
        """Busca uma marca pelo código"""
        try:
            response = self.client.table('marcas')\
                .select('*')\
                .eq('codigo', codigo)\
                .eq('tipo_veiculo', tipo_veiculo)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao buscar marca: {e}")
            return None
    
    def get_modelo_by_codigo(self, codigo: str, marca_id: int, tipo_veiculo: str) -> Dict[str, Any]:
        """Busca um modelo pelo código"""
        try:
            response = self.client.table('modelos')\
                .select('*')\
                .eq('codigo', codigo)\
                .eq('marca_id', marca_id)\
                .eq('tipo_veiculo', tipo_veiculo)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao buscar modelo: {e}")
            return None
