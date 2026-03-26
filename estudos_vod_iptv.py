#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

# =============================================================================
# 🎬 CONFIGURAÇÕES E BANCO DE DATOS
# =============================================================================

# DICA: Use links diretos .mp4 ou .m3u8 para funcionar em Smart TVs
DATA = {
    "movies": [
        {
            "id": "mov_001",
            "title": "Tokyo Ghoul - Live Action",
            "group": "Animes",
            "logo": "https://image.tmdb.org/t/p/w500/6vS9L7Q2m8oXzJ9xV8w5n4P.jpg",
            "url": "https://exemplo.com/filmes/tokyo-ghoul.m3u8",
            "year": "2017"
        },
        {
            "id": "mov_002",
            "title": "Manobras Radicais",
            "group": "Skate / Esportes",
            "logo": "https://exemplo.com/logos/skate.jpg",
            "url": "https://exemplo.com/videos/skate_tutorial.mp4",
            "year": "2024"
        }
    ],
    "series": [
        {
            "title": "Naruto Shippuden",
            "group": "Animes / Séries",
            "logo": "https://image.tmdb.org/t/p/w500/398O1OO9u7uPTvYp9mYv5n4P.jpg",
            "episodes": [
                {"s": 1, "e": 1, "name": "O Retorno", "url": "https://cdn.com/naruto/s01e01.m3u8"},
                {"s": 1, "e": 2, "name": "Os Akatsuki", "url": "https://cdn.com/naruto/s01e02.m3u8"}
            ]
        }
    ]
}

# =============================================================================
# 🛠️ GERADOR DE LISTA M3U (OTIMIZADO PARA APPS)
# =============================================================================

def generate_iptv_list():
    output_file = "vod_playlist.m3u"
    
    with open(output_file, "w", encoding="utf-8") as f:
        # Cabeçalho padrão IPTV
        f.write("#EXTM3U\n\n")
        
        # --- SEÇÃO DE FILMES ---
        f.write("### ---------- FILMES ---------- ###\n")
        for mov in DATA["movies"]:
            # Tags que os APPs usam para montar a biblioteca (Capa, Grupo, Título)
            line = (f'#EXTINF:-1 tvg-id="{mov["id"]}" tvg-name="{mov["title"]}" '
                    f'tvg-logo="{mov["logo"]}" group-title="{mov["group"]}", '
                    f'{mov["title"]} ({mov["year"]})\n')
            f.write(line)
            f.write(f'{mov["url"]}\n\n')

        # --- SEÇÃO DE SÉRIES ---
        f.write("### ---------- SÉRIES ---------- ###\n")
        for ser in DATA["series"]:
            for ep in ser["episodes"]:
                # Formato S01 E01 para o App organizar as temporadas
                ep_title = f"{ser['title']} S{ep['s']:02d}E{ep['e']:02d} - {ep['name']}"
                
                line = (f'#EXTINF:-1 tvg-id="{ser["title"]}_{ep["s"]}_{ep["e"]}" '
                        f'tvg-logo="{ser["logo"]}" group-title="{ser["group"]}", '
                        f'{ep_title}\n')
                f.write(line)
                f.write(f'{ep["url"]}\n\n')

    print(f"✅ Sucesso! Lista '{output_file}' gerada com {len(DATA['movies'])} filmes e episódios.")

if __name__ == "__main__":
    generate_iptv_list()
