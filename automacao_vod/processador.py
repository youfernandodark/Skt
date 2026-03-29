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
    """Busca o ID e a Capa da série no TMDB para enriquecer o VOD."""
    if not TMDB_API_KEY: 
        return "0", ""
    params = {"api_key": TMDB_API_KEY, "query": nome, "language": "pt-BR"}
    try:
        r = requests.get(f"{TMDB_BASE_URL}/search/tv", params=params, timeout=10)
        dados = r.json()
        if dados.get('results'):
            res = dados['results'][0]
            poster = res.get('poster_path')
            capa_url = f"{TMDB_IMG_BASE}{poster}" if poster else ""
            return str(res.get('id')), capa_url
    except Exception:
        pass
    return "0", ""

def processar_series(f_out):
    """Lê os links brutos e gera a estrutura compatível com a aba de Séries."""
    if not os.path.exists(INPUT_SERIES): 
        print(f"Erro: Arquivo {INPUT_SERIES} não encontrado.")
        return
        
    with open(INPUT_SERIES, "r", encoding="utf-8") as f_in:
        for linha in f_in:
            linha = linha.strip()
            if not linha or '|' not in linha: 
                continue
            
            # Formato esperado no TXT: Nome da Série | Temporada e EP | Link
            partes = [p.strip() for p in linha.split('|')]
            if len(partes) >= 3:
                nome_serie, ep_info, url = partes[0], partes[1], partes[2]
                tmdb_id, capa = buscar_dados_tmdb(nome_serie)
                
                # Título que aparece no player (Ex: Chainsaw Man - S01 E01)
                exibicao = f"{nome_serie} - {ep_info}"
                
                # --- AJUSTE PARA ABA DE SÉRIES ---
                # type="series": Move o conteúdo de 'Canais' para 'Séries'
                # series-name: Agrupa todos os episódios sob a mesma capa
                # group-title: Define a categoria principal no menu
                metadata = (
                    f'#EXTINF:-1 tvg-id="{tmdb_id}" '
                    f'tvg-name="{exibicao}" '
                    f'tvg-logo="{capa}" '
                    f'group-title="SÉRIES ANIME" '
                    f'type="series" '
                    f'series-name="{nome_serie}",{exibicao}'
                )
                
                f_out.write(f'{metadata}\n')
                f_out.write(f'{url}\n\n')

def main():
    # [span_1](start_span)Garante que a pasta de saída existe[span_1](end_span)
    os.makedirs("automacao_vod", exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        # Cabeçalho padrão M3U
        f_out.write("#EXTM3U\n")
        f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        
        processar_series(f_out)
    
    print(f"Sucesso: {OUTPUT_FILE} gerado com sucesso!")

if __name__ == "__main__":
    main()
