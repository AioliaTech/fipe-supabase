import requests
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FipeAPI:
    BASE_URL = "https://parallelum.com.br/fipe/api/v1"
    
    # Delays para evitar rate limit
    DELAY_ENTRE_REQUISICOES = 0.5  # 500ms entre cada chamada
    DELAY_APOS_ERRO = 2.0  # 2 segundos após erro 429
    MAX_RETRIES = 3
    
    TIPO_VEICULO_MAP = {
        'carros': 'carros',
        'motos': 'motos',
        'caminhoes': 'caminhoes'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _fazer_requisicao(self, url: str, retry_count: int = 0) -> Optional[Dict]:
        """Faz requisição com retry e controle de rate limit"""
        try:
            # Delay antes da requisição
            time.sleep(self.DELAY_ENTRE_REQUISICOES)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                if retry_count < self.MAX_RETRIES:
                    logger.warning(f"Rate limit atingido. Aguardando {self.DELAY_APOS_ERRO}s... (tentativa {retry_count + 1}/{self.MAX_RETRIES})")
                    time.sleep(self.DELAY_APOS_ERRO)
                    return self._fazer_requisicao(url, retry_count + 1)
                else:
                    logger.error(f"Erro 429 após {self.MAX_RETRIES} tentativas: {url}")
                    return None
            else:
                logger.error(f"Erro HTTP {e.response.status_code}: {url}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar {url}: {str(e)}")
            return None
    
    def obter_marcas(self, tipo_veiculo: str) -> List[Dict]:
        """Obtém todas as marcas de um tipo de veículo"""
        tipo = self.TIPO_VEICULO_MAP.get(tipo_veiculo)
        if not tipo:
            logger.error(f"Tipo de veículo inválido: {tipo_veiculo}")
            return []
        
        url = f"{self.BASE_URL}/{tipo}/marcas"
        logger.info(f"📥 Buscando marcas de {tipo_veiculo}...")
        
        marcas = self._fazer_requisicao(url)
        if marcas:
            logger.info(f"✅ {len(marcas)} marcas encontradas")
            return marcas
        return []
    
    def obter_modelos(self, tipo_veiculo: str, codigo_marca: str) -> List[Dict]:
        """Obtém todos os modelos de uma marca"""
        tipo = self.TIPO_VEICULO_MAP.get(tipo_veiculo)
        if not tipo:
            return []
        
        url = f"{self.BASE_URL}/{tipo}/marcas/{codigo_marca}/modelos"
        
        data = self._fazer_requisicao(url)
        if data and 'modelos' in data:
            modelos = data['modelos']
            logger.info(f"  ✓ {len(modelos)} modelos encontrados")
            return modelos
        return []
    
    def obter_anos(self, tipo_veiculo: str, codigo_marca: str, codigo_modelo: str) -> List[Dict]:
        """Obtém todos os anos disponíveis de um modelo"""
        tipo = self.TIPO_VEICULO_MAP.get(tipo_veiculo)
        if not tipo:
            return []
        
        url = f"{self.BASE_URL}/{tipo}/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos"
        
        anos = self._fazer_requisicao(url)
        if anos:
            return anos
        return []
    
    def obter_valor(self, tipo_veiculo: str, codigo_marca: str, 
                    codigo_modelo: str, codigo_ano: str) -> Optional[Dict]:
        """Obtém o valor FIPE de uma versão específica"""
        tipo = self.TIPO_VEICULO_MAP.get(tipo_veiculo)
        if not tipo:
            return None
        
        url = f"{self.BASE_URL}/{tipo}/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos/{codigo_ano}"
        
        return self._fazer_requisicao(url)
