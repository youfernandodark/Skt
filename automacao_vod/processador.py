 import os
import sys
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class Config:
    """Gerenciamento de Configurações e Caminhos"""
    BASE_DIR = Path(__file__).parent
    OUTPUT_FILE = BASE_DIR / "lista_final_vod.m3u"
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
    
    # URL Externa de EPG (XMLTV) - Configure no Player ou deixe vazio
    EPG_URL = os.environ.get('EPG_URL', '') 

    FONTES: List[Dict[str, str]] = [
        { "input": "links_tv.txt", "tipo": "tv", "categoria": "CANAIS AO VIVO" },
        { "input": "links_filmes.txt", "tipo": "movie", "categoria": "FILMES" },
        { "input": "links_series.txt", "tipo": "tv", "categoria": "SÉRIES" }
    ]

class TMDBHandler:
    """Classe responsável por interagir com a API do TMDB"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def buscar_dados(self, nome: str, tipo: str) -> Tuple[str, str, str]:
        """
        Busca metadados no TMDB.
        Retorna: (tmdb_id, logo_url, sinopse)
        """
        if not self.api_key:
            logger.warning("TMDB_API_KEY não configurada. Metadados ignorados.")
            return "0", "", "Sinopse indisponível."

        params = {
            "api_key": self.api_key,
            "query": nome,
            "language": "pt-BR",
            "page": 1
        }

        try:
            url = f"{Config.TMDB_BASE_URL}/search/{tipo}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            dados = response.json()

            if dados.get('results'):
                res = dados['results'][0]
                tmdb_id = str(res.get('id'))
                poster_path = res.get('poster_path')
                
                logo = f"{Config.TMDB_IMG_BASE}{poster_path}" if poster_path else ""
                sinopse = res.get('overview', 'Sinopse não encontrada.').replace('\n', ' ').strip()
                
                logger.info(f"✓ TMDB ID {tmdb_id} encontrado para '{nome}'")
                return tmdb_id, logo, sinopse
            
            logger.debug(f"⚠ Nenhum resultado TMDB para '{nome}'")
            return "0", "", "Informação não encontrada."

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Erro na requisição TMDB: {e}")
        except Exception as e:
            logger.error(f"✗ Erro inesperado: {e}")
            
        return "0", "", "Erro na busca."

def processar_linha(linha: str, fonte: Dict[str, str], tmdb_handler: TMDBHandler) -> Optional[str]:
    """Processa uma linha do arquivo de entrada e retorna a string formatada para M3U"""
    partes = [p.strip() for p in linha.split('|')]
    
    if len(partes) < 3:
        return None

    nome_obra = partes[0].strip()
    info_extra = partes[1].strip()
    url = partes[2].strip()

    # Busca metadados
    tmdb_id, capa, sinopse = tmdb_handler.buscar_dados(nome_obra, fonte["tipo"])

    # Padronização do ID para EPG (minúsculas, sem espaços especiais)
    tvg_id = tmdb_id if tmdb_id != "0" else nome_obra.lower().replace(" ", "_")
    nome_exibicao = f"{nome_obra} {info_extra}".strip()

    # Construção da entrada M3U
    extinf = (
        f'#EXTINF:-1 tvg-id="{tvg_id}" '
        f'tvg-name="{nome_obra}" '
        f'tvg-logo="{capa}" '
        f'group-title="{fonte["categoria"]}" '
        f'description="{sinopse}",{nome_exibicao}'
    )
    
    return f"{extinf}\n{url}\n"

def main():
    logger.info("🚀 Iniciando processador de listas VOD/TV")
    
    api_key = os.environ.get('TMDB_API_KEY')
    tmdb_handler = TMDBHandler(api_key)
    
    # Garantir que o diretório existe
    Config.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f_out:
            # Cabeçalho M3U com suporte a EPG externo
            f_out.write("#EXTM3U\n")
            if Config.EPG_URL:
                f_out.write(f'#EXTM3U url-tvg="{Config.EPG_URL}"\n')
            f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

            total_linhas = 0
            
            for fonte in Config.FONTES:
                caminho_arquivo = Config.BASE_DIR / fonte["input"]
                
                if not caminho_arquivo.exists():
                    logger.warning(f"Arquivo não encontrado: {caminho_arquivo}")
                    continue
                
                logger.info(f"📁 Processando: {fonte['input']}")
                
                with open(caminho_arquivo, "r", encoding="utf-8") as f_in:
                    for linha in f_in:
                        linha = linha.strip()
                        if not linha or '|' not in linha:
                            continue
                        
                        resultado = processar_linha(linha, fonte, tmdb_handler)
                        if resultado:
                            f_out.write(resultado)
                            f_out.write("\n") # Espaçamento entre entradas
                            total_linhas += 1

        logger.info(f"✅ Sucesso! {total_linhas} entradas geradas em {Config.OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"❌ Falha crítica na geração do arquivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()                       
