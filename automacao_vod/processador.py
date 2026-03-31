import os
import requests
import re
import logging
from typing import Optional

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações - Busca exatamente o que o YAML envia
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/multi"

if not TMDB_API_KEY:
    logger.error("Erro: Variável de ambiente TMDB_API_KEY não encontrada no GitHub Secrets.")
    exit(1)

def buscar_metadados(nome_limpo: str) -> Optional[str]:
    """Busca o poster no TMDB baseado no nome limpo."""
    if not nome_limpo or nome_limpo == "Desconhecido":
        return ""
        
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
            primeiro_resultado = data['results'][0]
            poster_path = primeiro_resultado.get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception as e:
        logger.error(f"Erro ao buscar '{nome_limpo}': {e}")
    
    return ""

def limpar_nome(header: str) -> str:
    """Remove caracteres especiais e extrai o nome real do filme."""
    # Remove o prefixo #EXTINF e tags extras
    nome = header.split(',')[-1]
    # Remove pipes '|' ou outros caracteres que atrapalham a busca
    nome_limpo = nome.replace('|', '').strip()
    return nome_limpo if nome_limpo else "Desconhecido"

def gerar_m3u():
    arquivos = {
        "links_tv.txt": {"type": "live", "group": "Canais Ao Vivo"},
        "links_filmes.txt": {"type": "movie", "group": "Filmes"},
        "links_series.txt": {"type": "series", "group": "Séries"}
    }
    
    output_file = "lista_final_vod.m3u"
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        
        for nome_arq, info in arquivos.items():
            if not os.path.exists(nome_arq):
                continue
                
            logger.info(f"Processando: {nome_arq}")
            
            with open(nome_arq, "r", encoding="utf-8") as f_in:
                linhas = [l.strip() for l in f_in.readlines() if l.strip()]
                
                for i in range(0, len(linhas), 2):
                    if i + 1 >= len(linhas): break
                        
                    header = linhas[i]
                    url = linhas[i+1]
                    
                    if not header.startswith("#EXTINF"): continue

                    nome_busca = limpar_nome(header)
                    logo = buscar_metadados(nome_busca) if info["type"] != "live" else ""
                    
                    tags = f'tvg-type="{info["type"]}" group-title="{info["group"]}"'
                    if logo:
                        tags += f' tvg-logo="{logo}"'
                    
                    # Injeta as tags logo após o #EXTINF:-1
                    novo_header = re.sub(r'^#EXTINF:-1', f'#EXTINF:-1 {tags}', header)
                    f_out.write(f"{novo_header}\n{url}\n")
            
    logger.info(f"🎉 Sucesso! Lista gerada: {output_file}")

if __name__ == "__main__":
    gerar_m3u()
                
