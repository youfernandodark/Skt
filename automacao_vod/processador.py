import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import importlib.util
import sys
import argparse

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ConteudoM3U:
    """Classe para representar um item da playlist"""
    titulo: str
    url: str
    grupo: str = "Geral"
    id: str = ""
    logo: str = ""
    ano: str = ""
    sinopse: str = ""
    tipo: str = "movie"
    temporada: str = ""
    episodio: str = ""
    avaliacao: float = 0.0
    generos: List[str] = None

    def __post_init__(self):
        if self.generos is None:
            self.generos = []


class TMDbClient:
    """Cliente para integração com a API do TMDb"""
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY", "")
        if not self.api_key:
            logger.warning("TMDB API Key não configurada. Funcionalidades limitadas.")

    def buscar_por_titulo(self, titulo: str, ano: Optional[str] = None) -> Optional[Dict]:
        """Busca conteúdo no TMDb pelo título"""
        if not self.api_key:
            return None
        
        try:
            params = {
                "api_key": self.api_key,
                "query": titulo,
                "language": "pt-BR"
            }
            if ano:
                params["year"] = ano
            
            response = requests.get(
                f"{self.BASE_URL}/search/multi",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            resultados = response.json().get("results", [])
            if resultados:
                return resultados[0]
                
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar '{titulo}' no TMDb: {e}")
        
        return None

    def obter_detalhes(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Obtém detalhes completos de um item do TMDb"""
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{media_type}/{tmdb_id}",
                params={
                    "api_key": self.api_key,
                    "language": "pt-BR",
                    "append_to_response": "credits,similar"
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter detalhes do ID {tmdb_id}: {e}")
        
        return None

    def enriquecer_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece um item com dados do TMDb"""
        titulo = item.get("titulo", "")
        ano = item.get("ano", "")
        
        resultado = self.buscar_por_titulo(titulo, ano)
        
        if resultado:
            media_type = resultado.get("media_type", "movie")
            tmdb_id = resultado.get("id")
            
            detalhes = self.obter_detalhes(tmdb_id, media_type)
            
            if detalhes:
                # Atualiza com dados do TMDb
                item["logo"] = detalhes.get("poster_path") or item.get("logo", "")
                if item["logo"]:
                    item["logo"] = f"{self.IMAGE_BASE_URL}{item['logo']}"
                
                item["sinopse"] = detalhes.get("overview") or item.get("sinopse", "")
                item["ano"] = str(detalhes.get("release_date", "").split("-")[0]) or item.get("ano", "")
                item["avaliacao"] = detalhes.get("vote_average", 0)
                item["generos"] = [g.get("name") for g in detalhes.get("genres", [])]
                
                logger.info(f"Enriquecido: {titulo}")
        
        return item


class GeradorM3U:
    """Classe principal para geração de playlists M3U"""
    
    def __init__(self, tmdb_api_key: Optional[str] = None):
        self.tmdb_client = TMDbClient(tmdb_api_key)

    def detectar_tipo(self, item: Dict[str, Any]) -> str:
        """Detecta se é filme ou série baseado em várias heurísticas"""
        titulo = item.get("titulo", "")
        grupo = item.get("grupo", "")
        temporada = item.get("temporada", "")
        episodio = item.get("episodio", "")
        
        # Verifica padrões de série
        padroes_serie = [
            "S01" in titulo, "E01" in titulo,
            "Série" in grupo, "Series" in grupo,
            temporada, episodio,
            "episódio" in titulo.lower(),
            "temporada" in titulo.lower()
        ]
        
        return "series" if any(padroes_serie) else "movie"

    def formatar_descricao(self, item: Dict[str, Any]) -> str:
        """Formata a descrição com informações adicionais"""
        partes = []
        
        if item.get("sinopse"):
            partes.append(item.get("sinopse", ""))
        
        if item.get("avaliacao", 0) > 0:
            partes.append(f"⭐ Avaliação: {item['avaliacao']}/10")
        
        if item.get("generos"):
            generos_str = ", ".join(item["generos"][:3])
            partes.append(f"🎭 Gêneros: {generos_str}")
        
        if item.get("temporada") and item.get("episodio"):
            partes.append(f"📺 T{item['temporada']}E{item['episodio']}")
        
        descricao = " | ".join(partes) if partes else item.get("sinopse", "")
        
        # Escapa caracteres especiais
        return descricao.replace('"', '\\"').replace('\n', ' ').strip()

    def gerar_linha(self, item: Dict[str, Any]) -> str:
        """Gera uma linha EXTINF para o arquivo M3U"""
        
        # Enriquecimento opcional (descomente se quiser usar TMDb)
        # item = self.tmdb_client.enriquecer_item(item)
        
        tipo = self.detectar_tipo(item)
        titulo = item.get("titulo", "Desconhecido")
        grupo = item.get("grupo", "Geral")
        item_id = item.get("id", "")
        logo = item.get("logo", "")
        ano = item.get("ano", "")
        descricao = self.formatar_descricao(item)
        url = item.get("url", "")
        
        # Tags opcionais
        tags_adicionais = []
        
        if item.get("temporada"):
            tags_adicionais.append(f'tvg-season="{item["temporada"]}"')
        
        if item.get("episodio"):
            tags_adicionais.append(f'tvg-episode="{item["episodio"]}"')
        
        tags_str = " ".join(tags_adicionais)
        
        # Construção da linha EXTINF
        extinf = (
            f'#EXTINF:-1 tvg-id="{item_id}" '
            f'tvg-logo="{logo}" '
            f'group-title="{grupo}" '
            f'tvg-type="{tipo}" '
            f'year="{ano}" '
            f'{tags_str} '
            f'description="{descricao}",{titulo}\n'
        )
        
        return f"{extinf}{url}\n"

    def gerar_playlist(self, lista_conteudo: List[Dict[str, Any]]) -> str:
        """Gera o conteúdo completo do arquivo M3U"""
        
        logger.info(f"Iniciando geração de playlist com {len(lista_conteudo)} itens")
        
        # Cabeçalho M3U com metadados
        cabecalho = "#EXTM3U\n"
        cabecalho += f"# Playlist gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        cabecalho += f"# Total de itens: {len(lista_conteudo)}\n\n"
        
        conteudo = cabecalho
        
        # Estatísticas
        stats = {"movie": 0, "series": 0, "erros": 0}
        
        for idx, item in enumerate(lista_conteudo, 1):
            try:
                linha = self.gerar_linha(item)
                conteudo += linha
                
                tipo = self.detectar_tipo(item)
                stats[tipo] += 1
                
                if idx % 50 == 0:
                    logger.info(f"Processados {idx}/{len(lista_conteudo)} itens")
                    
            except Exception as e:
                stats["erros"] += 1
                logger.error(f"Erro ao processar item {idx}: {e}")
                logger.debug(f"Item problemático: {item}")
        
        # Adiciona estatísticas ao final do arquivo (como comentário)
        conteudo += f"\n# Estatísticas:\n"
        conteudo += f"# Filmes: {stats['movie']}\n"
        conteudo += f"# Séries: {stats['series']}\n"
        conteudo += f"# Erros: {stats['erros']}\n"
        
        logger.info(f"Playlist gerada com sucesso! Filmes: {stats['movie']}, Séries: {stats['series']}")
        
        return conteudo

    def salvar_playlist(self, lista_conteudo: List[Dict[str, Any]], nome_arquivo: str = "playlist.m3u"):
        """Gera e salva a playlist em arquivo"""
        conteudo = self.gerar_playlist(lista_conteudo)
        
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
        
        logger.info(f"Arquivo {nome_arquivo} salvo com sucesso!")
        return nome_arquivo


def carregar_dados(arquivo: str = "organizador.py") -> List[Dict[str, Any]]:
    """Carrega os dados do arquivo organizador"""
    try:
        # Se for arquivo Python, importa dinamicamente
        spec = importlib.util.spec_from_file_location("organizador", arquivo)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["organizador"] = module
            spec.loader.exec_module(module)
            
            if hasattr(module, "meu_vod"):
                return module.meu_vod
            else:
                logger.error("Arquivo não contém a variável 'meu_vod'")
                return []
        else:
            logger.error(f"Não foi possível carregar o arquivo {arquivo}")
            return []
            
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return []


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Gerador de playlist M3U")
    parser.add_argument("--arquivo", default="organizador.py", help="Arquivo com os dados")
    parser.add_argument("--output", default="playlist.m3u", help="Nome do arquivo de saída")
    parser.add_argument("--tmdb-key", help="Chave da API do TMDb (opcional)")
    args = parser.parse_args()

    # Carrega dados
    dados = carregar_dados(args.arquivo)

    if not dados:
        logger.error("Nenhum dado encontrado para processar")
        return

    logger.info(f"Carregados {len(dados)} itens de {args.arquivo}")

    # Gera playlist
    gerador = GeradorM3U(tmdb_api_key=args.tmdb_key)
    gerador.salvar_playlist(dados, args.output)


if __name__ == "__main__":
    main()            
                    
        
