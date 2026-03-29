import os
import sys
import requests
from datetime import datetime

# Configurações TMDB
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

# Arquivos
INPUT_SERIES = "automacao_vod/links_series.txt"
OUTPUT_FILE = "automacao_vod/lista_final_vod.m3u"

def buscar_dados_tmdb(nome, tipo="tv"):
    if not TMDB_API_KEY: return "", ""
    endpoint = "search/tv" if tipo == "tv" else "search/movie"
    params = {"api_key": TMDB_API_KEY, "query": nome, "language": "pt-BR"}
    try:
        r = requests.get(f"{TMDB_BASE_URL}/{endpoint}", params=params, timeout=10)
        dados = r.json()
        if dados.get('results'):
            result = dados['results'][0]
            id_tmdb = str(result.get('id'))
            path = result.get('poster_path')
            capa = f"{TMDB_IMG_BASE}{path}" if path else ""
            return id_tmdb, capa
    except: pass
    return "", ""

def processar_arquivo(caminho, f_out, tipo="tv"):
    if not os.path.exists(caminho): return 0
    contador = 0
    with open(caminho, "r", encoding="utf-8") as f_in:
        for linha in f_in:
            linha = linha.strip()
            if not linha or '|' not in linha: continue
            
            partes = [p.strip() for p in linha.split('|')]
            if len(partes) >= 3:
                nome_serie, temporada_ep, url = partes[0], partes[1], partes[2]
                
                # Busca ID e Capa reais no TMDB
                id_tmdb, capa = buscar_dados_tmdb(nome_serie, "tv")
                
                # Monta a exibição: Nome S01 E01
                exibicao = f"{nome_serie} {temporada_ep}"
                
                # FORMATO EXATO: #EXTINF:-1 tvg-id="ID" tvg-name="NOME EP" tvg-logo="CAPA" group-title="NOME SERIE",NOME EP
                f_out.write(f'#EXTINF:-1 tvg-id="{id_tmdb}" tvg-name="{exibicao}" tvg-logo="{capa}" group-title="{nome_serie}",{exibicao}\n')
                f_out.write(f'{url}\n\n')
                contador += 1
    return contador

def main():
    os.makedirs("automacao_vod", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        total = processar_arquivo(INPUT_SERIES, f_out, "tv")
    print(f"✅ Sucesso! {total} episódios gerados no novo formato.")

if __name__ == "__main__":
    main()
        
