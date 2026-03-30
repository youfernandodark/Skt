import os
import requests
import re

# COLOQUE SUA CHAVE AQUI OU USE VARIÁVEIS DE AMBIENTE
TMDB_API_KEY = "TMDB_API_KEY"
BASE_URL = "https://api.themoviedb.org/3/search/multi"

def buscar_metadados(nome_limpo):
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": nome_limpo,
            "language": "pt-BR"
        }
        response = requests.get(BASE_URL, params=params).json()
        if response['results']:
            data = response['results'][0]
            poster = f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}"
            return poster
    except Exception:
        pass
    return ""

def limpar_nome(header):
    # Tenta extrair o nome após a vírgula do #EXTINF
    match = re.search(r',(.+)$', header)
    return match.group(1).strip() if match else "Desconhecido"

def gerar_m3u():
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
                            logo = buscar_metadados(nome_busca) if info["type"] != "live" else ""
                            
                            # Construção das tags
                            tags = f'tvg-type="{info["type"]}" group-title="{info["group"]}"'
                            if logo:
                                tags += f' tvg-logo="{logo}"'
                            
                            novo_header = header.replace("#EXTINF:-1", f'#EXTINF:-1 {tags}')
                            f_out.write(f"{novo_header}\n{url}\n")
                print(f"✅ Concluído: {nome_arq}")

if __name__ == "__main__":
    gerar_m3u()
    
