#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Lista VOD
Gera arquivo M3U8 com metadados do TMDB para serviços de streaming.
"""

import os
import sys
import logging
import requests
from datetime import datetime
from typing import Optional, List, Dict

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automacao_vod/processamento.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurações TMDB
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

# Configurações de Arquivos
INPUT_FILE = "automacao_vod/links_brutos.txt"
OUTPUT_FILE = "automacao_vod/lista_final_vod.m3u"
BACKUP_FILE = "automacao_vod/backup_lista_vod.m3u"


def buscar_poster_tmdb(nome_filme: str) -> str:
    """
    Busca o poster do filme na API do TMDB.
    
    Args:
        nome_filme: Nome do filme para busca
        
    Returns:
        URL do poster ou string vazia se não encontrado
    """
    if not TMDB_API_KEY:
        logger.warning("TMDB_API_KEY não configurada")
        return ""
    
    params = {
        "api_key": TMDB_API_KEY,
        "query": nome_filme,
        "language": "pt-BR",
        "page": "1"
    }
    
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/search/movie",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        dados = response.json()
        
        if dados.get('results'):
            path = dados['results'][0].get('poster_path')
            if path:
                poster_url = f"{TMDB_IMG_BASE}{path}"
                logger.info(f"Poster encontrado para '{nome_filme}'")
                return poster_url
        
        logger.warning(f"Poster não encontrado para '{nome_filme}'")
        return ""
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição TMDB: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return ""


def validar_linha(linha: str) -> Optional[Dict[str, str]]:
    """
    Valida e parseia uma linha do arquivo de entrada.
    
    Args:
        linha: Linha do arquivo no formato "Nome | URL | Categoria"
        
    Returns:
        Dicionário com dados ou None se inválido
    """
    linha = linha.strip()
    
    if not linha or linha.startswith('#'):
        return None
    
    if '|' not in linha:
        logger.warning(f"Linha inválida (sem separador |): {linha}")
        return None
    
    partes = [p.strip() for p in linha.split('|')]
    
    if len(partes) < 2:
        logger.warning(f"Linha incompleta: {linha}")
        return None
    
    nome = partes[0]
    url = partes[1]
    categoria = partes[2].strip() if len(partes) > 2 else "VOD"
    
    if not nome or not url:
        logger.warning(f"Linha com dados vazios: {linha}")
        return None
    
    if not url.startswith('http'):
        logger.warning(f"URL inválida: {url}")
        return None
    
    return {
        'nome': nome,
        'url': url,
        'categoria': categoria
    }


def criar_backup() -> None:
    """Cria backup da lista anterior se existir."""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f_in:
                with open(BACKUP_FILE, 'w', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
            logger.info(f"Backup criado: {BACKUP_FILE}")
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")


def gerar_m3u() -> bool:
    """
    Gera o arquivo M3U com metadados completos.
    
    Returns:
        True se sucesso, False se falha
    """
    logger.info("=" * 50)
    logger.info("Iniciando geração da lista VOD")
    logger.info("=" * 50)
    
    if not os.path.exists(INPUT_FILE):
        logger.error(f"Arquivo de entrada não encontrado: {INPUT_FILE}")
        return False
    
    criar_backup()
    
    contador_sucesso = 0
    contador_falha = 0
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
            f_out.write("#EXTM3U\n")
            f_out.write(f"#GENERATED: {datetime.now().isoformat()}\n")
            f_out.write(f"#SOURCE: {INPUT_FILE}\n")
            f_out.write("\n")
            
            with open(INPUT_FILE, 'r', encoding='utf-8') as f_in:
                for num_linha, linha in enumerate(f_in, 1):
                    dados = validar_linha(linha)
                    
                    if not dados:
                        continue
                    
                    nome = dados['nome']
                    url = dados['url']
                    categoria = dados['categoria']
                    
                    logger.info(f"Processando [{num_linha}]: {nome}")
                    
                    capa = buscar_poster_tmdb(nome)
                    
                    f_out.write(f'#EXTINF:-1 ')
                    f_out.write(f'tvg-id="" ')
                    f_out.write(f'tvg-name="{nome}" ')
                    f_out.write(f'tvg-logo="{capa}" ')
                    f_out.write(f'group-title="{categoria}",')
                    f_out.write(f'{nome}\n')
                    f_out.write(f'{url}\n\n')
                    
                    contador_sucesso += 1
                    
        logger.info("=" * 50)
        logger.info(f"Processamento concluído!")
        logger.info(f"Sucesso: {contador_sucesso} | Falhas: {contador_falha}")
        logger.info(f"Arquivo gerado: {OUTPUT_FILE}")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"Erro crítico: {str(e)}")
        return False


if __name__ == "__main__":
    sucesso = gerar_m3u()
    sys.exit(0 if sucesso else 1)
