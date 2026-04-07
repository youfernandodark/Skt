import os
import requests
import logging
import re
from typing import Optional, Tuple, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/multi"
URL_EPG = "https://github.com/limaalef/BrazilTVEPG/blob/main/epg.xml" 

if not TMDB_API_KEY:
    logger.error("Variável de ambiente TMDB_API_KEY não encontrada.")
    exit(1)

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

def buscar_metadados(nome_limpo: str) -> Tuple[str, str, str, str]:
    if not nome_limpo or nome_limpo == "Desconhecido":
        return "", "", "", ""
    try:
        params = {"api_key": TMDB_API_KEY, "query": nome_limpo, "language": "pt-BR", "page": 1, "include_adult": "false"}
        response = session.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            res = data['results'][0]
            tmdb_id = str(res.get('id', ''))
            path = res.get('poster_path')
            poster = f"https://image.tmdb.org/t/p/w500{path}" if path else ""
            sinopse = res.get('overview', '').replace('\n', ' ').replace('"', "'").strip()
            data_lanc = res.get('release_date') or res.get('first_air_date') or ""
            ano = data_lanc.split('-')[0] if '-' in data_lanc else ""
            return poster, ano, sinopse, tmdb_id
    except Exception as e:
        logger.warning(f"Erro ao buscar metadados para '{nome_limpo}': {e}")
    return "", "", "", ""

def extrair_tag(header: str, tag: str) -> str:
    """Extrai o valor de qualquer tag (tvg-id, group-title, etc) do cabeçalho."""
    match = re.search(f'{tag}="([^"]+)"', header)
    return match.group(1) if match else ""

def limpar_nome(header: str) -> str:
    if "," in header:
        nome = header.rsplit(',', 1)[-1]
        nome = nome.replace('|', '').strip()
        return os.path.splitext(nome)[0]
    return "Desconhecido"

def gerar_m3u():
    pasta = "automacao_vod"
    # Removido o grupo fixo dos links_tv.txt
    arquivos_config = {
        "links_tv.txt": {"type": "live", "default_group": "Canais Ao Vivo"},
        "links_filmes.txt": {"type": "movie", "default_group": "Filmes"},
        "links_series.txt": {"type": "series", "default_group": "Séries"}
    }
    
    output_file = "lista_final_vod.m3u"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write(f'#EXTM3U url-tvg="{URL_EPG}"\n')
            
            for nome_arq, info in arquivos_config.items():
                caminho = os.path.join(pasta, nome_arq) if os.path.isdir(pasta) else nome_arq
                
                if not os.path.exists(caminho):
                    continue
                    
                logger.info(f"Lendo arquivo: {nome_arq}")
                
                with open(caminho, "r", encoding="utf-8") as f_in:
                    linhas = [l.strip() for l in f_in if l.strip()]
                    
                    for i in range(0, len(linhas), 2):
                        if i + 1 >= len(linhas): break
                        
                        header, url = linhas[i], linhas[i+1]
                        if not header.startswith("#EXTINF"): continue

                        nome_original = limpar_nome(header)
                        
                        # CAPTURA O GRUPO DO ARQUIVO ORIGINAL OU USA O PADRÃO
                        grupo_original = extrair_tag(header, "group-title")
                        grupo_final = grupo_original if grupo_original else info["default_group"]
                        
                        tvg_id_existente = extrair_tag(header, "tvg-id")
                        logo, ano, sinopse, tmdb_id = "", "", "", ""
                        
                        if info["type"] in ["movie", "series"]:
                            logo, ano, sinopse, tmdb_id = buscar_metadados(nome_original)
                        
                        nome_exibicao = f"{nome_original} ({ano})" if ano else nome_original
                        
                        # Montagem das tags
                        tags = [f'tvg-type="{info["type"]}"', f'group-title="{grupo_final}"']
                        
                        final_tvg_id = tmdb_id if tmdb_id else tvg_id_existente
                        if final_tvg_id: 
                            tags.append(f'tvg-id="{final_tvg_id}"')
                        
                        if tmdb_id: tags.append(f'tmdb-id="{tmdb_id}"')
                        if logo:    tags.append(f'tvg-logo="{logo}"')
                        if sinopse: tags.append(f'plot="{sinopse}"')
                        
                        f_out.write(f'#EXTINF:-1 {" ".join(tags)},{nome_exibicao}\n{url}\n')
                        
        logger.info(f"✨ Lista atualizada com sucesso: {output_file}")
        
    except IOError as e:
        logger.error(f"Erro ao gravar arquivo: {e}")

if __name__ == "__main__":
    gerar_m3u()
  
