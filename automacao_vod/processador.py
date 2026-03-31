import os
import requests
import re
import logging
from typing import Optional, Tuple

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/multi"

if not TMDB_API_KEY:
    logger.error("Erro: Variável de ambiente TMDB_API_KEY não encontrada.")
    exit(1)

def buscar_metadados(nome_limpo: str) -> Tuple[str, str, str]:
    """Busca poster, ano e sinopse no TMDB."""
    if not nome_limpo or nome_limpo == "Desconhecido":
        return "", "", ""
        
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": nome_limpo,
            "language": "pt-BR",
            "page": 1
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            res = data['results'][0]
            poster = f"https://image.tmdb.org/t/p/w500{res.get('poster_path')}" if res.get('poster_path') else ""
            
            # Puxa a sinopse (overview)
            sinopse = res.get('overview', 'Sinopse não disponível.').replace('\n', ' ')
            
            # Puxa o ano
            data_lanc = res.get('release_date') or res.get('first_air_date') or ""
            ano = data_lanc.split('-')[0] if '-' in data_lanc else ""
            
            return poster, ano, sinopse
    except Exception as e:
        logger.error(f"Erro ao buscar metadados de '{nome_limpo}': {e}")
    
    return "", "", ""

def limpar_nome(header: str) -> str:
    """Extrai o nome removendo pipes e espaços."""
    nome = header.split(',')[-1]
    return nome.replace('|', '').strip()

def gerar_m3u():
    pasta = "automacao_vod"
    arquivos = {
        "links_tv.txt": {"type": "live", "group": "Canais Ao Vivo"},
        "links_filmes.txt": {"type": "movie", "group": "Filmes"},
        "links_series.txt": {"type": "series", "group": "Séries"}
    }
    
    output_file = "lista_final_vod.m3u"
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        
        for nome_arq, info in arquivos.items():
            caminho = os.path.join(pasta, nome_arq) if os.path.exists(pasta) else nome_arq
            
            if not os.path.exists(caminho):
                continue
                
            logger.info(f"Processando: {nome_arq}")
            
            with open(caminho, "r", encoding="utf-8") as f_in:
                linhas = [l.strip() for l in f_in.readlines() if l.strip()]
                
                for i in range(0, len(linhas), 2):
                    if i + 1 >= len(linhas): break
                    
                    header, url = linhas[i], linhas[i+1]
                    if not header.startswith("#EXTINF"): continue

                    nome_original = limpar_nome(header)
                    logo, ano, sinopse = "", "", ""
                    
                    if info["type"] != "live":
                        logo, ano, sinopse = buscar_metadados(nome_original)
                    
                    nome_exibicao = f"{nome_original} ({ano})" if ano else nome_original
                    
                    # Adiciona as tags de metadados (logo e sinopse/plot)
                    tags = f'tvg-type="{info["type"]}" group-title="{info["group"]}"'
                    if logo:
                        tags += f' tvg-logo="{logo}"'
                    if sinopse:
                        # Alguns players usam a tag 'plot' para exibir a sinopse
                        tags += f' plot="{sinopse}"'
                    
                    f_out.write(f'#EXTINF:-1 {tags},{nome_exibicao}\n{url}\n')
            
    logger.info(f"✅ Lista atualizada com Sinopses em {output_file}")

if __name__ == "__main__":
    gerar_m3u()
   
    
