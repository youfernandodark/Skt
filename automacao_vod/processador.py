import os
import requests
from datetime import datetime

# Configurações TMDB
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

# Arquivos
INPUT_SERIES = "automacao_vod/links_series.txt"
OUTPUT_FILE = "automacao_vod/lista_final_vod.m3u"

def buscar_dados_tmdb(nome):
    if not TMDB_API_KEY: return "0", ""
    params = {"api_key": TMDB_API_KEY, "query": nome, "language": "pt-BR"}
    try:
        r = requests.get(f"{TMDB_BASE_URL}/search/tv", params=params, timeout=10)
        dados = r.json()
        if dados.get('results'):
            res = dados['results'][0]
            return str(res.get('id')), f"{TMDB_IMG_BASE}{res.get('poster_path')}"
    except: pass
    return "0", ""

def processar_series(f_out):
    if not os.path.exists(INPUT_SERIES): return
    with open(INPUT_SERIES, "r", encoding="utf-8") as f_in:
        for linha in f_in:
            linha = linha.strip()
            if not linha or '|' not in linha: continue
            
            # Formato esperado: Nome | Temporada EP | Link
            partes = [p.strip() for p in linha.split('|')]
            if len(partes) >= 3:
                nome_serie, ep_info, url = partes[0], partes[1], partes[2]
                tmdb_id, capa = buscar_dados_tmdb(nome_serie)
                
                exibicao = f"{nome_serie} {ep_info}"
                
                # Formato idêntico ao solicitado
                f_out.write(f'#EXTINF:-1 tvg-id="{tmdb_id}" tvg-name="{exibicao}" tvg-logo="{capa}" group-title="{nome_serie}",{exibicao}\n')
                f_out.write(f'{url}\n\n')

def main():
    os.makedirs("automacao_vod", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        processar_series(f_out)

if __name__ == "__main__":
    main()
