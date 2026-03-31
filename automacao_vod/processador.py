import os
import requests
import re
import logging
from typing import Optional

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/multi"

if not TMDB_API_KEY:
    logger.error("Erro: Variável de ambiente TMDB_API_KEY não encontrada.")
    exit(1)

def buscar_metadados(nome_limpo: str) -> Optional[str]:
    """Busca o poster no TMDB baseado no nome limpo."""
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": nome_limpo,
            "language": "pt-BR",
            "page": 1
        }
        # Adicionado timeout para evitar travamentos
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            primeiro_resultado = data['results'][0]
            poster_path = primeiro_resultado.get('poster_path')
            
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                logger.warning(f"Sem poster para: {nome_limpo}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição TMDB para '{nome_limpo}': {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar metadados: {e}")
    
    return ""

def limpar_nome(header: str) -> str:
    """Extrai o nome do conteúdo após a última vírgula do #EXTINF."""
    # Padrão M3U: #EXTINF:-1 info...,NOME DO CANAL/FILME
    if "," in header:
        return header.rsplit(',', 1)[-1].strip()
    return "Desconhecido"

def gerar_m3u():
    # Correção: Removidos espaços extras nas chaves e valores
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
                logger.warning(f"Arquivo {nome_arq} não encontrado. Pulando...")
                continue
                
            logger.info(f"Processando {nome_arq}...")
            
            with open(nome_arq, "r", encoding="utf-8") as f_in:
                linhas = f_in.readlines()
                
                # Itera de 2 em 2 (Header + URL)
                for i in range(0, len(linhas), 2):
                    if i + 1 >= len(linhas):
                        break
                        
                    header = linhas[i].strip()
                    url = linhas[i+1].strip()
                    
                    if not header.startswith("#EXTINF"):
                        continue

                    nome_busca = limpar_nome(header)
                    
                    # Só busca poster se não for TV Ao Vivo
                    logo = ""
                    if info["type"] != "live":
                        logo = buscar_metadados(nome_busca)
                    
                    # Construção das tags M3U corretamente formatadas
                    # Ex: tvg-type="movie" group-title="Filmes" tvg-logo="url"
                    tags = f'tvg-type="{info["type"]}" group-title="{info["group"]}"'
                    if logo:
                        tags += f' tvg-logo="{logo}"'
                    
                    # Injeta as tags logo após #EXTINF:-1
                    # Substitui #EXTINF:-1 por #EXTINF:-1 [TAGS]
                    # Usa regex para garantir que pega o início da linha
                    novo_header = re.sub(
                        r'^#EXTINF:-1', 
                        f'#EXTINF:-1 {tags}', 
                        header
                    )
                    
                    f_out.write(f"{novo_header}\n{url}\n")
            
            logger.info(f"✅ Concluído: {nome_arq}")

    logger.info(f"🎉 Lista final gerada em {output_file}")

if __name__ == "__main__":
    gerar_m3u()
