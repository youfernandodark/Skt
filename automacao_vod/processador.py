import os
import requests

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

def buscar_poster_tmdb(nome_filme):
    if not TMDB_API_KEY:
        return ""
    params = {"api_key": TMDB_API_KEY, "query": nome_filme, "language": "pt-BR"}
    try:
        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
        dados = response.json()
        if dados.get('results'):
            path = dados['results'][0].get('poster_path')
            return f"{TMDB_IMG_BASE}{path}" if path else ""
    except:
        pass
    return ""

def gerar_m3u():
    input_file = "automacao_vod/links_brutos.txt"
    output_file = "lista_final_vod.m3u"
    
    if not os.path.exists(input_file):
        return

    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        with open(input_file, "r", encoding="utf-8") as f_in:
            for linha in f_in:
                if "|" in linha:
                    partes = [p.strip() for p in linha.split("|")]
                    nome = partes[0]
                    url = partes[1]
                    categoria = partes[2] if len(partes) > 2 else "VOD"
                    
                    capa = buscar_poster_tmdb(nome)
                    f_out.write(f'#EXTINF:-1 tvg-logo="{capa}" group-title="{categoria}",{nome}\n{url}\n')

if __name__ == "__main__":
    gerar_m3u()
