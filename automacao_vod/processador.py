import os
import sys
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# Logging
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

    EPG_URL = os.environ.get('EPG_URL', 'https://iptv-epg.org/')

    FONTES: List[Dict[str, str]] = [
        {"input": "links_tv.txt", "tipo": "tv", "categoria": "CANAIS AO VIVO"},
        {"input": "links_filmes.txt", "tipo": "movie", "categoria": "FILMES"},
        {"input": "links_series.txt", "tipo": "tv", "categoria": "SÉRIES"}
    ]

class TMDBHandler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def buscar_dados(self, nome: str, tipo: str) -> Tuple[str, str, str]:
        if not self.api_key:
            return "0", "", "Sem API TMDB."

        try:
            url = f"{Config.TMDB_BASE_URL}/search/{tipo}"
            params = {
                "api_key": self.api_key,
                "query": nome,
                "language": "pt-BR"
            }

            r = self.session.get(url, params=params, timeout=10)
            r.raise_for_status()

            data = r.json()

            if data.get("results"):
                res = data["results"][0]
                tmdb_id = str(res.get("id", "0"))

                poster = ""
                if res.get("poster_path"):
                    poster = f"{Config.TMDB_IMG_BASE}{res['poster_path']}"

                sinopse = res.get("overview", "").replace("\n", " ").strip()

                return tmdb_id, poster, sinopse or "Sem descrição."

            return "0", "", "Não encontrado."

        except Exception as e:
            logger.error(f"Erro TMDB ({nome}): {e}")
            return "0", "", "Erro na busca."

def processar_linha(linha: str, fonte: Dict[str, str], tmdb: TMDBHandler) -> Optional[str]:
    linha = linha.strip()

    # Ignorar lixo
    if not linha or linha.startswith("#"):
        return None

    partes = linha.split("|")

    if len(partes) < 3:
        return None

    nome = partes[0].strip()
    info = partes[1].strip()
    url = partes[2].strip()

    if not url.startswith("http"):
        return None

    tmdb_id, capa, sinopse = tmdb.buscar_dados(nome, fonte["tipo"])

    tvg_id = tmdb_id if tmdb_id != "0" else nome.lower().replace(" ", "_")

    extinf = (
        f'#EXTINF:-1 tvg-id="{tvg_id}" '
        f'tvg-name="{nome}" '
        f'tvg-logo="{capa}" '
        f'group-title="{fonte["categoria"]}" '
        f'description="{sinopse}",{nome} {info}'
    )

    return f"{extinf}\n{url}"

def main():
    api_key = os.environ.get("TMDB_API_KEY")
    tmdb = TMDBHandler(api_key)

    Config.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as out:
            out.write(f'#EXTM3U url-tvg="{Config.EPG_URL}"\n')
            out.write(f"# GERADO EM: {datetime.now()}\n\n")

            for fonte in Config.FONTES:
                path = Config.BASE_DIR / fonte["input"]

                if not path.exists():
                    logger.warning(f"Arquivo não encontrado: {path}")
                    continue

                logger.info(f"Processando: {path}")

                with open(path, "r", encoding="utf-8") as f:
                    for linha in f:
                        item = processar_linha(linha, fonte, tmdb)
                        if item:
                            out.write(item + "\n\n")

        logger.info(f"✅ Lista gerada: {Config.OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
