import os
import sys
import requests
from datetime import datetime

# Configurações
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
INPUT_FILE = "automacao_vod/links_brutos.txt"
OUTPUT_FILE = "automacao_vod/lista_final_vod.m3u"

# URL do EPG (Exemplo comum: Github de guias públicos ou sua própria fonte XMLTV)
URL_EPG = "https://meu-guia-epg.com/guia.xml" 

def verificar_link(url):
    [span_0](start_span)"""Verifica se o link está online[span_0](end_span)"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code in [200, 301, 302]
    except:
        try:
            response = requests.get(url, timeout=5, stream=True)
            return response.status_code == 200
        except:
            return False

def buscar_metadados(nome, tipo):
    [span_1](start_span)"""Busca no TMDB para filmes e séries[span_1](end_span)"""
    if not TMDB_API_KEY or tipo == "channel":
        return ""
    endpoint = "search/movie" if tipo == "movie" else "search/tv"
    params = {"api_key": TMDB_API_KEY, "query": nome, "language": "pt-BR"}
    try:
        response = requests.get(f"{TMDB_BASE_URL}/{endpoint}", params=params, timeout=10)
        dados = response.json()
        if dados.get('results'):
            path = dados['results'][0].get('poster_path')
            return f"{TMDB_IMG_BASE}{path}" if path else ""
        return ""
    except:
        return ""

def gerar_m3u():
    os.makedirs("automacao_vod", exist_ok=True)
    if not os.path.exists(INPUT_FILE):
        return False

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        # Configuração do cabeçalho com a URL do EPG
        f_out.write(f'#EXTM3U x-tvg-url="{URL_EPG}"\n\n')
        
        with open(INPUT_FILE, "r", encoding="utf-8") as f_in:
            for linha in f_in:
                linha = linha.strip()
                if not linha or '|' not in linha:
                    continue
                
                # NOVO FORMATO: Nome | URL | Categoria | Tipo | EPG-ID
                # Exemplo: Globo | http://... | TV | channel | Globo.br
                partes = [p.strip() for p in linha.split('|')]
                nome = partes[0]
                url = partes[1]
                cat = partes[2] if len(partes) > 2 else "Geral"
                tipo = partes[3].lower() if len(partes) > 3 else "movie"
                epg_id = partes[4] if len(partes) > 4 else "" # ID do canal no XMLTV

                if verificar_link(url):
                    capa = buscar_metadados(nome, tipo)
                    tag_serie = ' tvg-type="series"' if tipo == "tv" else ""
                    tag_epg = f' tvg-id="{epg_id}"' if epg_id else ""
                    
                    f_out.write(f'#EXTINF:-1{tag_epg} tvg-logo="{capa}" group-title="{cat}"{tag_serie},{nome}\n')
                    f_out.write(f'{url}\n\n')
    return True

if __name__ == "__main__":
    sucesso = gerar_m3u()
    sys.exit(0 if sucesso else 1)
