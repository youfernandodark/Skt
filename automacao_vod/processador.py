import os
import requests
from datetime import datetime

# Configurações TMDB
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

# Mapeamento de Fontes
FONTES = [
    {"in": "automacao_vod/links_tv.txt", "tipo": "tv", "categoria": "CANAIS AO VIVO"},
    {"in": "automacao_vod/links_filmes.txt", "tipo": "movie", "categoria": "FILMES"},
    {"in": "automacao_vod/links_series.txt", "tipo": "tv", "categoria": "SÉRIES"}
]

OUTPUT_FILE = "automacao_vod/lista_final_vod.m3u"

def buscar_dados_tmdb(nome, tipo):
    if not TMDB_API_KEY: return "0", "", "Sem sinopse disponível."
    params = {"api_key": TMDB_API_KEY, "query": nome, "language": "pt-BR"}
    try:
        r = requests.get(f"{TMDB_BASE_URL}/search/{tipo}", params=params, timeout=10)
        dados = r.json()
        if dados.get('results'):
            res = dados['results'][0]
            id_tmdb = str(res.get('id'))
            capa = f"{TMDB_IMG_BASE}{res.get('poster_path')}" if res.get('poster_path') else ""
            sinopse = res.get('overview', 'Sinopse não encontrada.').replace('\n', ' ')
            return id_tmdb, capa, sinopse
    except: pass
    return "0", "", "Erro ao carregar informações."

def main():
    os.makedirs("automacao_vod", exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        
        for fonte in FONTES:
            if not os.path.exists(fonte["in"]): continue
            
            with open(fonte["in"], "r", encoding="utf-8") as f_in:
                for linha in f_in:
                    linha = linha.strip()
                    if not linha or '|' not in linha: continue
                    
                    partes = [p.strip() for p in linha.split('|')]
                    if len(partes) >= 3:
                        nome, extra, url = partes[0], partes[1], partes[2]
                        tmdb_id, capa, sinopse = buscar_dados_tmdb(nome, fonte["tipo"])
                        
                        exibicao = f"{nome} {extra}".strip()
                        
                        # Formatação com metadados avançados
                        # tvg-id é essencial para o EPG funcionar em canais
                        info_linha = (
                            f'#EXTINF:-1 tvg-id="{tmdb_id}" tvg-name="{nome}" '
                            f'tvg-logo="{capa}" group-title="{fonte["categoria"]}" '
                            f'description="{sinopse}",{exibicao}\n'
                        )
                        
                        f_out.write(info_linha)
                        f_out.write(f'{url}\n\n')

if __name__ == "__main__":
    main()
