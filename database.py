from supabase import create_client, Client
from config import Config
from typing import List, Dict, Any, Optional

class SupabaseDB:
    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    
    def inserir_marca(self, codigo: str, nome: str, tipo_veiculo: str) -> Optional[int]:
        """Insere uma marca no banco e retorna o ID"""
        try:
            response = self.client.table('marcas').upsert({
                'codigo': codigo,
                'nome': nome,
                'tipo_veiculo': tipo_veiculo
            }, on_conflict='codigo,tipo_veiculo').execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get('id')
            return None
        except Exception as e:
            print(f"Erro ao inserir marca {nome}: {e}")
            return None
    
    def inserir_modelo(self, codigo: str, nome: str, marca_id: int, tipo_veiculo: str) -> Optional[int]:
        """Insere um modelo no banco e retorna o ID"""
        try:
            response = self.client.table('modelos').upsert({
                'codigo': codigo,
                'nome': nome,
                'marca_id': marca_id,
                'tipo_veiculo': tipo_veiculo
            }, on_conflict='codigo,marca_id,tipo_veiculo').execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get('id')
            return None
        except Exception as e:
            print(f"Erro ao inserir modelo {nome}: {e}")
            return None
    
    def inserir_versao(self, codigo: str, nome: str, modelo_id: int, 
                       tipo_veiculo: str, ano_modelo: Optional[int] = None,
                       combustivel: Optional[str] = None, codigo_fipe: Optional[str] = None,
                       mes_referencia: Optional[str] = None, valor: Optional[str] = None) -> Optional[int]:
        """Insere uma versão no banco e retorna o ID"""
        try:
            dados = {
                'codigo': codigo,
                'nome': nome,
                'modelo_id': modelo_id,
                'tipo_veiculo': tipo_veiculo
            }
            
            # Adiciona campos opcionais se fornecidos
            if ano_modelo:
                dados['ano_modelo'] = ano_modelo
            if combustivel:
                dados['combustivel'] = combustivel
            if codigo_fipe:
                dados['codigo_fipe'] = codigo_fipe
            if mes_referencia:
                dados['mes_referencia'] = mes_referencia
            if valor:
                dados['valor'] = valor
            
            response = self.client.table('versoes').upsert(
                dados,
                on_conflict='codigo,modelo_id,tipo_veiculo'
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get('id')
            return None
        except Exception as e:
            print(f"Erro ao inserir versão {nome}: {e}")
            return None
    
    def get_marca_by_codigo(self, codigo: str, tipo_veiculo: str) -> Optional[Dict[str, Any]]:
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
    
    def get_modelo_by_codigo(self, codigo: str, marca_id: int, tipo_veiculo: str) -> Optional[Dict[str, Any]]:
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
