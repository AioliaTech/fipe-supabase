import requests
from typing import List, Dict, Any
from config import Config

class FipeService:
    def __init__(self):
        self.base_url = Config.FIPE_API_BASE_URL
        self.tipos_veiculo = ['carros', 'motos', 'caminhoes']
    
    def get_marcas(self, tipo_veiculo: str) -> List[Dict[str, Any]]:
        """Busca todas as marcas de um tipo de veículo"""
        try:
            url = f"{self.base_url}/{tipo_veiculo}/marcas"
            response = requests.get(url)
            response.raise_for_status()
            return [{'codigo': m['codigo'], 'nome': m['nome'], 'tipo_veiculo': tipo_veiculo} 
                    for m in response.json()]
        except Exception as e:
            print(f"Erro ao buscar marcas de {tipo_veiculo}: {e}")
            return []
    
    def get_modelos(self, tipo_veiculo: str, codigo_marca: str) -> List[Dict[str, Any]]:
        """Busca todos os modelos de uma marca"""
        try:
            url = f"{self.base_url}/{tipo_veiculo}/marcas/{codigo_marca}/modelos"
            response = requests.get(url)
            response.raise_for_status()
            modelos = response.json()['modelos']
            return [{'codigo': str(m['codigo']), 'nome': m['nome'], 'tipo_veiculo': tipo_veiculo} 
                    for m in modelos]
        except Exception as e:
            print(f"Erro ao buscar modelos da marca {codigo_marca}: {e}")
            return []
    
    def get_anos(self, tipo_veiculo: str, codigo_marca: str, codigo_modelo: str) -> List[str]:
        """Busca todos os anos disponíveis de um modelo"""
        try:
            url = f"{self.base_url}/{tipo_veiculo}/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos"
            response = requests.get(url)
            response.raise_for_status()
            return [ano['codigo'] for ano in response.json()]
        except Exception as e:
            print(f"Erro ao buscar anos do modelo {codigo_modelo}: {e}")
            return []
    
    def get_versao(self, tipo_veiculo: str, codigo_marca: str, 
                   codigo_modelo: str, codigo_ano: str) -> Dict[str, Any]:
        """Busca informações completas de uma versão específica"""
        try:
            url = f"{self.base_url}/{tipo_veiculo}/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos/{codigo_ano}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                'codigo': f"{codigo_modelo}_{codigo_ano}",
                'nome': f"{data.get('Modelo', '')} - {data.get('AnoModelo', '')}",
                'tipo_veiculo': tipo_veiculo,
                'ano_modelo': data.get('AnoModelo'),
                'combustivel': data.get('Combustivel'),
                'codigo_fipe': data.get('CodigoFipe'),
                'mes_referencia': data.get('MesReferencia'),
                'valor': data.get('Valor')
            }
        except Exception as e:
            print(f"Erro ao buscar versão: {e}")
            return None
