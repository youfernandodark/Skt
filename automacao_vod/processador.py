import os
import sys
import requests
from datetime import datetime

# Configurações TMDB
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

# Arquivos de Entrada e Saída
INPUT_FILMES = "automacao_vod/links_brutos.txt"
INPUT_SERIES = "automacao_vod/links_series.txt"
OUTPUT_FILE = "automacao_vod/lista_final_vod.m3u"

def buscar_poster(nome, tipo="movie"):
    if not TMDB_API_KEY: return ""
    # Define o endpoint baseado no tipo (movie ou tv)
    endpoint = "search/movie" if tipo == "movie" else "search/tv"
    params = {"api_key": TMDB_API_KEY, "query": nome, "language": "pt-BR"}
    
    try:
        r = requests.get(f"{TMDB_BASE_URL}/{endpoint}", params=params, timeout=10)
        dados = r.json()
        if dados.get('results'):
            path = dados['results'][0].get('poster_path')
            return f"{TMDB_IMG_BASE}{path}" if path else ""
    except:
        pass
    return ""

def processar_arquivo(caminho, f_out, tipo="movie"):
    if not os.path.exists(caminho):
        print(f"⚠️ Arquivo não encontrado: {caminho}")
        return 0
    
    contador = 0
    with open(caminho, "r", encoding="utf-8") as f_in:
        for linha in f_in:
            linha = linha.strip()
            if not linha or linha.startswith('#') or '|' not in linha:
                continue
            
            partes = [p.strip() for p in linha.split('|')]
            nome, url = partes[0], partes[1]
            categoria = partes[2] if len(partes) > 2 else ("Filmes" if tipo == "movie" else "Séries")
            
            capa = buscar_poster(nome, tipo)
            
            # Adicionamos 'tvg-type="series"' se for série para o app identificar melhor
            info_extra = ' tvg-type="series"' if tipo == "tv" else ""
            f_out.write(f'#EXTINF:-1 tvg-logo="{capa}" group-title="{categoria}"{info_extra},{nome}\n')
            f_out.write(f'{url}\n\n')
            contador += 1
            print(f"✅ Adicionado ({tipo}): {nome}")
    return contador

def main():
    os.makedirs("automacao_vod", exist_ok=True)
    total = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        
        total += processar_arquivo(INPUT_FILMES, f_out, "movie")
        total += processar_arquivo(INPUT_SERIES, f_out, "tv")
    
    print(f"\n🎉 Sucesso! {total} itens totais na lista única.")

if __name__ == "__main__":
    main()
