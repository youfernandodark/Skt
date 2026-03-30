import os
import requests
import re

# [span_1](start_span)Puxa a chave de API dos Secrets do GitHub[span_1](end_span)
TMDB_API_KEY = os.getenv("TMDB_API_KEY") 
BASE_URL = "https://api.themoviedb.org/3/search/multi"

def buscar_metadados(nome_limpo):
    if not TMDB_API_KEY:
        return ""
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": nome_limpo,
            "language": "pt-BR"
        }
        response = requests.get(BASE_URL, params=params).json()
        if response.get('results'):
            data = response['results'][0]
            poster = f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}"
            return poster
    except Exception:
        pass
    return ""

def limpar_nome(header):
    # [span_2](start_span)Extrai o nome após a vírgula do #EXTINF[span_2](end_span)
    match = re.search(r',(.+)$', header)
    return match.group(1).strip() if match else "Desconhecido"

def gerar_m3u():
    # Define as categorias e os arquivos de entrada
    arquivos = {
        "links_tv.txt": {"type": "live", "group": "Canais Ao Vivo"},
        "links_filmes.txt": {"type": "movie", "group": "Filmes de 2026"},
        "links_series.txt": {"type": "series", "group": "Séries"}
    }

    with open("lista_final_vod.m3u", "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        
        for nome_arq, info in arquivos.items():
            if os.path.exists(nome_arq):
                with open(nome_arq, "r", encoding="utf-8") as f_in:
                    linhas = f_in.readlines()
                    for i in range(0, len(linhas), 2):
                        if i + 1 < len(linhas):
                            header = linhas[i].strip()
                            url = linhas[i+1].strip()
                            
                            nome_busca = limpar_nome(header)
                            # Só busca no TMDB se for filme ou série
                            logo = buscar_metadados(nome_busca) if info["type"] != "live" else ""
                            
                            # [span_3](start_span)Adiciona as tags de organização[span_3](end_span)
                            tags = f'tvg-type="{info["type"]}" group-title="{info["group"]}"'
                            if logo:
                                tags += f' tvg-logo="{logo}"'
                            
                            novo_header = header.replace("#EXTINF:-1", f'#EXTINF:-1 {tags}')
                            f_out.write(f"{novo_header}\n{url}\n")
                print(f"✅ Processado: {nome_arq}")
            else:
                print(f"⚠️ Arquivo ignorado (não encontrado): {nome_arq}")

if __name__ == "__main__":
    gerar_m3u()
