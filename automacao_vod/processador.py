import os
import requests
import re
import logging
from typing import Optional, Tuple

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações - Pega a chave enviada pelo GitHub Actions
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/multi"

if not TMDB_API_KEY:
    logger.error("Erro: Variável de ambiente TMDB_API_KEY não encontrada.")
    exit(1)

def buscar_metadados(nome_limpo: str) -> Tuple[str, str]:
    """Busca o poster e o ano no TMDB."""
    if not nome_limpo or nome_limpo == "Desconhecido":
        return "", ""
        
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
            
            # Tenta pegar a data de lançamento (filme ou série)
            data_lancamento = res.get('release_date') or res.get('first_air_date') or ""
            ano = data_lancamento.split('-')[0] if '-' in data_lancamento else ""
            
            return poster, ano
    except Exception as e:
        logger.error(f"Erro ao buscar '{nome_limpo}': {e}")
    
    return "", ""

def limpar_nome(header: str) -> str:
    """Extrai o nome do filme removendo pipes e espaços extras."""
    nome = header.split(',')[-1]
    nome_limpo = nome.replace('|', '').strip()
    return nome_limpo if nome_limpo else "Desconhecido"

def gerar_m3u():
    # Caminho ajustado para a pasta onde os arquivos estão no seu repositório
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
            # Tenta ler da pasta ou da raiz para evitar erros de localização
            caminho_completo = os.path.join(pasta, nome_arq) if os.path.exists(pasta) else nome_arq
            
            if not os.path.exists(caminho_completo):
                continue
                
            logger.info(f"Processando: {nome_arq}")
            
            with open(caminho_completo, "r", encoding="utf-8") as f_in:
                linhas = [l.strip() for l in f_in.readlines() if l.strip()]
                
                for i in range(0, len(linhas), 2):
                    if i + 1 >= len(linhas): break
                        
                    header = linhas[i]
                    url = linhas[i+1]
                    
                    if not header.startswith("#EXTINF"): continue

                    nome_original = limpar_nome(header)
                    logo, ano = "", ""
                    
                    if info["type"] != "live":
                        logo, ano = buscar_metadados(nome_original)
                    
                    # Se achou o ano, atualiza o nome que aparece na lista
                    nome_exibicao = f"{nome_original} ({ano})" if ano else nome_original
                    
                    tags = f'tvg-type="{info["type"]}" group-title="{info["group"]}"'
                    if logo:
                        tags += f' tvg-logo="{logo}"'
                    
                    # Monta o novo header com as tags e o nome atualizado com ano
                    novo_header = f'#EXTINF:-1 {tags},{nome_exibicao}'
                    f_out.write(f"{novo_header}\n{url}\n")
            
    logger.info(f"🎉 Lista final atualizada com anos em {output_file}")

if __name__ == "__main__":
    gerar_m3u()
        
