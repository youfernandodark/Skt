import os
import requests
import logging
from typing import Optional, Tuple, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuração de Logging mais detalhada
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/multi"

if not TMDB_API_KEY:
    logger.error("Variável de ambiente TMDB_API_KEY não encontrada.")
    exit(1)

# Configuração de Sessão com Retentativas (Resiliência)
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

def buscar_metadados(nome_limpo: str) -> Tuple[str, str, str, str]:
    """Busca poster, ano, sinopse e ID no TMDB de forma eficiente."""
    if not nome_limpo or nome_limpo == "Desconhecido":
        return "", "", "", ""
        
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": nome_limpo,
            "language": "pt-BR",
            "page": 1,
            "include_adult": "false"
        }
        response = session.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            # Priorizamos o primeiro resultado
            res = data['results'][0]
            tmdb_id = str(res.get('id', ''))
            path = res.get('poster_path')
            poster = f"https://image.tmdb.org/t/p/w500{path}" if path else ""
            
            # Limpeza de texto para evitar quebra do M3U
            sinopse = res.get('overview', '').replace('\n', ' ').replace('"', "'").strip()
            
            # Tenta pegar data de lançamento de filme ou série
            data_lanc = res.get('release_date') or res.get('first_air_date') or ""
            ano = data_lanc.split('-')[0] if '-' in data_lanc else ""
            
            return poster, ano, sinopse, tmdb_id
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Falha na rede ao buscar '{nome_limpo}': {e}")
    except Exception as e:
        logger.error(f"Erro inesperado para '{nome_limpo}': {e}")
    
    return "", "", "", ""

def limpar_nome(header: str) -> str:
    """Extrai o nome removendo metadados comuns de IPTV/M3U."""
    if "," in header:
        # Pega tudo após a última vírgula
        nome = header.rsplit(',', 1)[-1]
        # Remove caracteres de formatação e espaços extras
        nome = nome.replace('|', '').strip()
        # Opcional: Remover extensões se existirem no nome
        nome = os.path.splitext(nome)[0]
        return nome
    return "Desconhecido"

def gerar_m3u():
    pasta = "automacao_vod"
    arquivos_config = {
        "links_tv.txt": {"type": "live", "group": "Canais Ao Vivo"},
        "links_filmes.txt": {"type": "movie", "group": "Filmes"},
        "links_series.txt": {"type": "series", "group": "Séries"}
    }
    
    output_file = "lista_final_vod.m3u"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write("#EXTM3U\n")
            
            for nome_arq, info in arquivos_config.items():
                caminho = os.path.join(pasta, nome_arq) if os.path.isdir(pasta) else nome_arq
                
                if not os.path.exists(caminho):
                    logger.warning(f"Arquivo não encontrado: {caminho}")
                    continue
                    
                logger.info(f"Processando categoria: {info['group']}")
                
                with open(caminho, "r", encoding="utf-8") as f_in:
                    linhas = [l.strip() for l in f_in if l.strip()]
                    
                    for i in range(0, len(linhas), 2):
                        if i + 1 >= len(linhas): break
                        
                        header, url = linhas[i], linhas[i+1]
                        if not header.startswith("#EXTINF"): continue

                        nome_original = limpar_nome(header)
                        logo, ano, sinopse, tmdb_id = "", "", "", ""
                        
                        # Só gasta cota de API para filmes e séries
                        if info["type"] in ["movie", "series"]:
                            logo, ano, sinopse, tmdb_id = buscar_metadados(nome_original)
                        
                        nome_exibicao = f"{nome_original} ({ano})" if ano else nome_original
                        
                        # Construção organizada das tags
                        metadata_tags = [
                            f'tvg-type="{info["type"]}"',
                            f'group-title="{info["group"]}"'
                        ]
                        
                        if tmdb_id: metadata_tags.append(f'tmdb-id="{tmdb_id}" tvg-id="{tmdb_id}"')
                        if logo:    metadata_tags.append(f'tvg-logo="{logo}"')
                        if sinopse: metadata_tags.append(f'plot="{sinopse}"')
                        
                        tags_str = " ".join(metadata_tags)
                        f_out.write(f'#EXTINF:-1 {tags_str},{nome_exibicao}\n{url}\n')
                        
        logger.info(f"✨ Sucesso! Lista gerada: {output_file}")
        
    except IOError as e:
        logger.error(f"Erro ao gravar arquivo de saída: {e}")

if __name__ == "__main__":
    gerar_m3u()
        
