import os
import requests
import json

# Configurações do TMDb - Puxa a chave de forma segura das variáveis do GitHub
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
# URL base para imagens do TMDb (w500 é uma largura boa para mobile/TV)
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

def buscar_poster_tmdb(nome_filme):
    """Consulta o TMDb para encontrar a capa do filme."""
    if not TMDB_API_KEY:
        print("Aviso: TMDB_API_KEY não configurada. Pulando busca de imagem.")
        return ""

    params = {
        "api_key": TMDB_API_KEY,
        "query": nome_filme,
        "language": "pt-BR" # Busca título e info em português
    }
    
    try:
        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
        response.raise_for_status() # Levanta erro se a requisição falhar
        dados = response.json()
        
        if dados['results']:
            # Pega o primeiro resultado (mais provável)
            poster_path = dados['results'][0].get('poster_path')
            if poster_path:
                return f"{TMDB_IMG_BASE}{poster_path}"
    except Exception as e:
        print(f"Erro ao buscar poster para '{nome_filme}': {e}")
        
    return "" # Retorna vazio se não encontrar nada

def gerar_m3u():
    arquivo_input = "automacao_vod/links_brutos.txt"
    arquivo_output = "lista_final_vod.m3u"
    
    if not os.path.exists(arquivo_input):
        print("Arquivo de entrada não encontrado!")
        return

    print(f"Iniciando processamento com integração TMDb...")

    with open(arquivo_output, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        
        with open(arquivo_input, "r", encoding="utf-8") as f_in:
            for linha in f_in:
                linha = linha.strip()
                if not linha or "|" not in linha:
                    continue
                
                # Formato no TXT: Nome do Filme | URL | Categoria
                partes = linha.split("|")
                nome = partes[0].strip()
                url = partes[1].strip()
                categoria = partes[2].strip() if len(partes) > 2 else "Geral"

                # --- NOVA FUNÇÃO DE INTEGRAÇÃO ---
                print(f"Buscando capa para: {nome}...")
                url_poster = buscar_poster_tmdb(nome)
                
                # Adiciona a tag tvg-logo se tivermos uma imagem
                tag_logo = f' tvg-logo="{url_poster}"' if url_poster else ""

                # Criando a entrada VOD formatada com a logo
                f_out.write(f'#EXTINF:-1{tag_logo} group-title="{categoria}",{nome}\n')
                f_out.write(f'{url}\n')

    print(f"Lista '{arquivo_output}' gerada com sucesso com metadados!")

if __name__ == "__main__":
    gerar_m3u()
