import os
import requests
from datetime import datetime

# Configurações TMDB
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

# Mapeamento de Fontes e Categorias
FONTES = [
    {"in": "automacao_vod/links_tv.txt", "tipo": "tv", "categoria": "CANAIS AO VIVO"},
    {"in": "automacao_vod/links_filmes.txt", "tipo": "movie", "categoria": "FILMES"},
    {"in": "automacao_vod/links_series.txt", "tipo": "tv", "categoria": "SÉRIES"}
]

OUTPUT_FILE = "automacao_vod/lista_final_vod.m3u"

def buscar_dados_tmdb(nome, tipo):
    if not TMDB_API_KEY:
        return "0", "", "Sinopse indisponível."
    
    params = {"api_key": TMDB_API_KEY, "query": nome, "language": "pt-BR"}
    
    try:
        r = requests.get(f"{TMDB_BASE_URL}/search/{tipo}", params=params, timeout=10)
        dados = r.json()
        
        if dados.get('results'):
            res = dados['results'][0]
            tmdb_id = str(res.get('id'))
            capa = f"{TMDB_IMG_BASE}{res.get('poster_path')}" if res.get('poster_path') else ""
            sinopse = res.get('overview', 'Sinopse não encontrada.').replace('\n', ' ')
            return tmdb_id, capa, sinopse
    except Exception as e:
        print(f"Erro na busca TMDB: {e}")
        pass
    
    return "0", "", "Informação não encontrada."

def main():
    os.makedirs("automacao_vod", exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        
        for fonte in FONTES:
            if not os.path.exists(fonte["in"]):
                print(f"Arquivo não encontrado: {fonte['in']}")
                continue
            
            with open(fonte["in"], "r", encoding="utf-8") as f_in:
                for linha in f_in:
                    linha = linha.strip()
                    if not linha or '|' not in linha:
                        continue
                    
                    # Formato esperado no TXT: Nome | Info Extra | Link
                    partes = [p.strip() for p in linha.split('|')]
                    if len(partes) >= 3:
                        nome_obra, info_extra, url = partes[0], partes[1], partes[2]
                        
                        # Puxa ID, Capa e Sinopse do TMDB
                        tmdb_id, capa, sinopse = buscar_dados_tmdb(nome_obra, fonte["tipo"])
                        
                        # Nome que aparece na lista (Ex: Matrix 1999)
                        exibicao = f"{nome_obra} {info_extra}".strip()
                        
                        # Preenchimento exato conforme solicitado
                        f_out.write(
                            f'#EXTINF:-1 tvg-id="{tmdb_id}" '
                            f'tvg-name="{nome_obra}" '
                            f'tvg-logo="{capa}" '
                            f'group-title="{fonte["categoria"]}" '
                            f'description="{sinopse}",{exibicao}\n'
                        )
                        f_out.write(f'{url}\n\n')
    
    print(f"Arquivo gerado com sucesso: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()                        

