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
    """Configurações de caminhos e URLs"""
    BASE_DIR = Path(__file__).parent
    OUTPUT_FILE = BASE_DIR / "lista_final_vod.m3u"
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
    EPG_URL = os.environ.get('EPG_URL', 'https://iptv-epg.org/')

    FONTES: List[Dict[str, str]] = [
        {"input": "links_tv.txt", "tipo": "tv", "categoria": "CANAIS AO VIVO"},
        {"input": "links_filmes.txt", "tipo": "movie", "categoria": "FILMES"},
        {"input": "links_series.txt", "tipo": "tv", "categoria": "SÉRIES"}
    ]

class TMDBHandler:
    """Busca capas e sinopses no TMDB"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def buscar_dados(self, nome: str, tipo: str) -> Tuple[str, str, str]:
        if not self.api_key:
            return "0", "", "Sinopse indisponível."

        params = {"api_key": self.api_key, "query": nome, "language": "pt-BR"}

        try:
            url = f"{Config.TMDB_BASE_URL}/search/{tipo}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            dados = response.json()

            if dados.get('results'):
                res = dados['results'][0]
                tmdb_id = str(res.get('id'))
                poster = f"{Config.TMDB_IMG_BASE}{res.get('poster_path')}" if res.get('poster_path') else ""
                sinopse = res.get('overview', '').replace('\n', ' ').strip()
                return tmdb_id, poster, sinopse

            return "0", "", "Informação não encontrada."
        except Exception as e:
            logger.error(f"Erro ao buscar {nome}: {e}")
            return "0", "", "Erro na busca."

def processar_linha(linha: str, fonte: Dict[str, str], tmdb_handler: TMDBHandler) -> Optional[str]:
    """Formata a linha para o padrão M3U Plus"""
    partes = [p.strip() for p in linha.split('|')]
    if len(partes) < 3:
        return None

    nome_obra, info_extra, url = partes[0], partes[1], partes[2]
    tmdb_id, capa, sinopse = tmdb_handler.buscar_dados(nome_obra, fonte["tipo"])

    tvg_id = tmdb_id if tmdb_id != "0" else nome_obra.lower().replace(" ", "_")

    extinf = (
        f'#EXTINF:-1 tvg-id="{tvg_id}" '
        f'tvg-name="{nome_obra}" '
        f'tvg-logo="{capa}" '
        f'group-title="{fonte["categoria"]}" '
        f'description="{sinopse}",{nome_obra} {info_extra}'
    )
    return f"{extinf}\n{url}"

def main():
    api_key = os.environ.get('TMDB_API_KEY')
    tmdb_handler = TMDBHandler(api_key)
    Config.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f_out:
            f_out.write(f'#EXTM3U url-tvg="{Config.EPG_URL}"\n')
            f_out.write(f"#GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

            for fonte in Config.FONTES:
                caminho = Config.BASE_DIR / fonte["input"]
                if not caminho.exists():
                    continue

                logger.info(f"Processando: {fonte['input']}")
                with open(caminho, "r", encoding="utf-8") as f_in:
                    for linha in f_in:
                        resultado = processar_linha(linha, fonte, tmdb_handler)
                        if resultado:
                            f_out.write(resultado + "\n\n")

        logger.info(f"✅ Arquivo gerado: {Config.OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
