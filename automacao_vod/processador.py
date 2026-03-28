import os
import requests
import time
import re

# Configurações
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

def sanitizar_nome(nome):
    """Remove ano e caracteres especiais para melhorar a busca na API"""
    # Remove ano entre parênteses ex: (2009)
    nome = re.sub(r'\(\d{4}\)', '', nome)
    # Remove caracteres especiais
    nome = re.sub(r'[^\w\sÀ-ÿ]', '', nome)
    return nome.strip()

def buscar_info_tmdb(nome_filme):
    """Busca Poster, Ano, Nota e Sinopse no TMDB"""
    if not TMDB_API_KEY:
        print("⚠️ API Key não configurada")
        return {}
    
    nome_busca = sanitizar_nome(nome_filme)
    params = {
        "api_key": TMDB_API_KEY,
        "query": nome_busca,
        "language": "pt-BR",
        "page": 1
    }
    
    try:
        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params, timeout=10)
        response.raise_for_status()
        dados = response.json()
        
        if dados.get('results'):
            filme = dados['results'][0]
            path = filme.get('poster_path')
            return {
                'logo': f"{TMDB_IMG_BASE}{path}" if path else "",
                'year': filme.get('release_date', '')[:4] if filme.get('release_date') else "",
                'rating': filme.get('vote_average', 0),
                'overview': filme.get('overview', '')[:160] # Limita tamanho da sinopse
            }
    except Exception as e:
        print(f"❌ Erro na API para '{nome_filme}': {e}")
    
    return {}

def gerar_m3u():
    input_file = "automacao_vod/links_brutos.txt"
    output_file = "lista_final_vod.m3u"
    
    if not os.path.exists(input_file):
        print(f"❌ Arquivo '{input_file}' não encontrado.")
        return

    print("🚀 Iniciando geração da lista VOD...")
    processados = 0
    erros = 0
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        
        with open(input_file, "r", encoding="utf-8") as f_in:
            linhas = f_in.readlines()
            total = len(linhas)
            
            for i, linha in enumerate(linhas, 1):
                if "|" not in linha:
                    continue
                
                partes = [p.strip() for p in linha.split("|")]
                
                if len(partes) < 2:
                    print(f"⚠️ Linha {i} ignorada (formato inválido)")
                    continue
                
                nome = partes[0]
                url = partes[1].strip()
                categoria = partes[2].strip() if len(partes) > 2 else "Geral"
                
                print(f"[{i}/{total}] Processando: {nome}...")
                
                info = buscar_info_tmdb(nome)
                
                # Formatação M3U Completa com tags padrão
                # tvg-id: identificador único (usamos o nome sanitizado)
                # tvg-name: nome para EPG
                # tvg-logo: capa do filme
                # group-title: categoria
                
                tvg_id = sanitizar_nome(nome).replace(" ", "_").lower()
                tvg_name = nome.replace('"', "'") # Evita aspas duplas
                
                f_out.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{info.get("logo", "")}" group-title="{categoria}",{tvg_name}\n')
                
                # Se tiver sinopse, pode adicionar como metadado extra dependendo do player
                # Alguns players suportam: tvg-opsis="sinopse"
                
                f_out.write(f'{url}\n')
                
                processados += 1
                
                # Rate Limiting: Respeitar limite da API (40 req/10s para free)
                time.sleep(0.3) 
    
    print(f"✅ Concluído! {processados} itens processados.")
    print(f"📄 Lista salva em: {output_file}")

if __name__ == "__main__":
    gerar_m3u()                    
    print(f"Lista '{output_file}' gerada com sucesso!")

if __name__ == "__main__":
    gerar_m3u()
