import os
import sys
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class Config:
    BASE_DIR = Path(__file__).parent
    OUTPUT_FILE = BASE_DIR / "lista_final_vod.m3u"
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
    
    # URLs de EPG corrigidas (separadas por vírgula no padrão M3U)
    EPG_URL = "https://epgshare01.online,https://iptv-epg.org/"

    # Mapeamento rigoroso para o TMDB e Categorias
    FONTES: List[Dict[str, str]] = [
        { "input": "links_tv.txt", "tipo": "tv", "categoria": "CANAIS AO VIVO", "m3u_type": "live" },
        { "input": "links_filmes.txt", "tipo": "movie", "categoria": "FILMES", "m3u_type": "movie" },
        { "input": "links_series.txt", "tipo": "tv", "categoria": "SÉRIES", "m3u_type": "series" }
    ]

class TMDBHandler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def buscar_dados(self, nome: str, tipo: str) -> Tuple[str, str, str]:
        if not self.api_key or self.api_key == "SUA_CHAVE_AQUI":
            return "0", "", "Sinopse indisponível."

        params = {
            "api_key": self.api_key,
            "query": nome,
            "language": "pt-BR",
            "page": 1
        }

        try:
            # O TMDB usa 'movie' ou 'tv' para busca
            url = f"{Config.TMDB_BASE_URL}/search/{tipo}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            dados = response.json()

            if dados.get('results'):
                res = dados['results'][0]
                tmdb_id = str(res.get('id'))
                poster_path = res.get('poster_path')
                
                logo = f"{Config.TMDB_IMG_BASE}{poster_path}" if poster_path else ""
                # Limpa quebras de linha na sinopse para não quebrar o M3U
                sinopse = res.get('overview' if tipo == 'movie' else 'overview', 'Sinopse não encontrada.').replace('\n', ' ').replace('\r', '').strip()
                
                return tmdb_id, logo, sinopse
            
            return "0", "", "Informação não encontrada."
        except Exception as e:
            logger.error(f"Erro TMDB: {e}")
            return "0", "", ""

def processar_linha(linha: str, fonte: Dict[str, str], tmdb_handler: TMDBHandler) -> Optional[str]:
    partes = [p.strip() for p in linha.split('|')]
    if len(partes) < 2: return None

    nome_obra = partes[0]
    # Se não houver info_extra (partes[1]), a URL será a partes[1]
    info_extra = partes[1] if len(partes) > 2 else ""
    url = partes[2] if len(partes) > 2 else partes[1]

    tmdb_id, capa, sinopse = tmdb_handler.buscar_dados(nome_obra, fonte["tipo"])
    
    tvg_id = tmdb_id if tmdb_id != "0" else nome_obra.lower().replace(" ", "_")
    nome_exibicao = f"{nome_obra} {info_extra}".strip()

    # Inclusão da tag m3u_type e correção de metadados para players VOD
    extinf = (
        f'#EXTINF:-1 tvg-id="{tvg_id}" '
        f'tvg-name="{nome_obra}" '
        f'tvg-logo="{capa}" '
        f'group-title="{fonte["categoria"]}" '
        f'tvg-type="{fonte["m3u_type"]}" '
        f'description="{sinopse}",{nome_exibicao}'
    )
    
    return f"{extinf}\n{url}"

def main():
    api_key = os.environ.get('TMDB_API_KEY')
    tmdb_handler = TMDBHandler(api_key)
    Config.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f_out:
            f_out.write(f'#EXTM3U x-tvg-url="{Config.EPG_URL}"\n\n')

            for fonte in Config.FONTES:
                caminho_arquivo = Config.BASE_DIR / fonte["input"]
                if not caminho_arquivo.exists(): continue
                
                logger.info(f"Processando: {fonte['input']}")
                with open(caminho_arquivo, "r", encoding="utf-8") as f_in:
                    for linha in f_in:
                        res = processar_linha(linha.strip(), fonte, tmdb_handler)
                        if res:
                            f_out.write(res + "\n")

        logger.info("✅ Lista atualizada com sucesso!")
    except Exception as e:
        logger.error(f"Erro: {e}")

if __name__ == "__main__":
    main()
                 
                
