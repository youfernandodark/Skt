#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
                    IPTV VOD GENERATOR - SOLUÇÃO COMPLETA
===============================================================================
Gera listas M3U para IPTV com filmes e séries a partir de dados embutidos.

Uso: python iptv_vod_generator.py
===============================================================================
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any

# =============================================================================
# 📚 BANCO DE DADOS EMBUTIDO (JSON)
# =============================================================================

MOVIES_DATA = {
    "movies": [
        {
            "id": "mov001",
            "title": "O Grande Aventura",
            "year": 2024,
            "genre": ["Ação", "Aventura"],
            "director": "João Silva",
            "cast": ["Maria Santos", "Pedro Oliveira"],
            "synopsis": "Uma jornada épica através de terras desconhecidas em busca de um tesouro lendário.",
            "duration": "120 min",
            "rating": "8.5",
            "poster": "https://via.placeholder.com/300x450/0000FF/FFFFFF?text=O+Grande+Aventura",
            "stream_url": "https://example-cdn.com/movies/grande-aventura-2024.m3u8",
            "trailer": "https://example.com/trailers/grande-aventura.mp4"
        },
        {
            "id": "mov002",
            "title": "Amor em Paris",
            "year": 2023,
            "genre": ["Romance", "Drama"],
            "director": "Sophie Martin",
            "cast": ["Jean Dupont", "Claire Beaumont"],
            "synopsis": "Dois estranhos se encontram nas ruas de Paris e descobrem que o amor pode surgir nos lugares mais inesperados.",
            "duration": "95 min",
            "rating": "7.8",
            "poster": "https://via.placeholder.com/300x450/FF69B4/FFFFFF?text=Amor+em+Paris",
            "stream_url": "https://example-cdn.com/movies/amor-paris-2023.m3u8",
            "trailer": "https://example.com/trailers/amor-paris.mp4"
        },
        {
            "id": "mov003",
            "title": "Cyber Future 2099",
            "year": 2025,
            "genre": ["Ficção Científica", "Ação"],
            "director": "Alex Chen",
            "cast": ["Ryan Cooper", "Lisa Wang"],
            "synopsis": "No ano de 2099, a humanidade luta contra uma IA que ameaça extinguir a raça humana.",
            "duration": "145 min",
            "rating": "9.1",
            "poster": "https://via.placeholder.com/300x450/00CED1/FFFFFF?text=Cyber+Future+2099",
            "stream_url": "https://example-cdn.com/movies/cyber-future-2099.m3u8",
            "trailer": "https://example.com/trailers/cyber-future.mp4"
        },
        {
            "id": "mov004",
            "title": "Risadas Garantidas",
            "year": 2024,
            "genre": ["Comédia"],
            "director": "Carlos Mendes",
            "cast": ["Ana Paula", "Bruno Ferreira"],
            "synopsis": "Uma comédia hilária sobre um grupo de amigos que tenta organizar um casamento desastroso.",
            "duration": "100 min",
            "rating": "7.2",
            "poster": "https://via.placeholder.com/300x450/FFD700/000000?text=Risadas+Garantidas",
            "stream_url": "https://example-cdn.com/movies/risadas-garantidas-2024.m3u8",
            "trailer": "https://example.com/trailers/risadas.mp4"
        },
        {
            "id": "mov005",
            "title": "O Mistério da Mansão",
            "year": 2023,
            "genre": ["Terror", "Suspense"],
            "director": "Helen Carter",
            "cast": ["Michael Scott", "Emma Watson"],
            "synopsis": "Uma família se muda para uma mansão antiga e descobre segredos sombrios escondidos nas paredes.",
            "duration": "110 min",
            "rating": "8.0",
            "poster": "https://via.placeholder.com/300x450/8B0000/FFFFFF?text=O+Misterio+da+Mansao",
            "stream_url": "https://example-cdn.com/movies/misterio-mansao-2023.m3u8",
            "trailer": "https://example.com/trailers/misterio-mansao.mp4"
        }
    ]
}

SERIES_DATA = {
    "series": [
        {
            "id": "ser001",
            "title": "Detetives da Cidade",
            "year": 2024,
            "genre": ["Crime", "Drama"],
            "creator": "Robert Stone",
            "cast": ["Tom Hardy", "Jessica Alba"],
            "synopsis": "Dois detetives investigam os casos mais complexos da cidade grande.",
            "seasons": 2,
            "rating": "8.7",
            "poster": "https://via.placeholder.com/300x450/4B0082/FFFFFF?text=Detectives+da+Cidade",
            "episodes": [
                {
                    "season": 1, "episode": 1, "title": "O Primeiro Caso",
                    "duration": "45 min", "synopsis": "Os detetives se conhecem e recebem seu primeiro caso juntos.",
                    "stream_url": "https://example-cdn.com/series/detetives/s01e01.m3u8"
                },
                {
                    "season": 1, "episode": 2, "title": "Pistas Escondidas",
                    "duration": "44 min", "synopsis": "Uma pista inesperada muda completamente a direção da investigação.",
                    "stream_url": "https://example-cdn.com/series/detetives/s01e02.m3u8"
                },
                {
                    "season": 2, "episode": 1, "title": "Novos Desafios",
                    "duration": "46 min", "synopsis": "Na segunda temporada, os detetives enfrentam um inimigo mais perigoso.",
                    "stream_url": "https://example-cdn.com/series/detetives/s02e01.m3u8"
                }
            ]
        },
        {
            "id": "ser002",
            "title": "Médicos em Ação",
            "year": 2023,
            "genre": ["Drama", "Medical"],
            "creator": "Sarah Johnson",
            "cast": ["Patrick Dempsey", "Ellen Pompeo"],
            "synopsis": "A vida intensa de médicos em um hospital de emergência.",
            "seasons": 3,
            "rating": "9.0",
            "poster": "https://via.placeholder.com/300x450/DC143C/FFFFFF?text=Medicos+em+Acao",
            "episodes": [
                {
                    "season": 1, "episode": 1, "title": "Plantão Inicial",
                    "duration": "42 min", "synopsis": "Primeiro dia de um novo residente no hospital.",
                    "stream_url": "https://example-cdn.com/series/medicos/s01e01.m3u8"
                },
                {
                    "season": 1, "episode": 2, "title": "Decisões Difíceis",
                    "duration": "43 min", "synopsis": "Um caso complexo testa as habilidades da equipe.",
                    "stream_url": "https://example-cdn.com/series/medicos/s01e02.m3u8"
                }
            ]
        },
        {
            "id": "ser003",
            "title": "Espaço Profundo",
            "year": 2025,
            "genre": ["Ficção Científica", "Aventura"],
            "creator": "Neil Armstrong Jr",
            "cast": ["Chris Pratt", "Zoe Saldana"],
            "synopsis": "Uma tripulação explora os confins do universo em busca de novos mundos.",
            "seasons": 1,
            "rating": "8.9",
            "poster": "https://via.placeholder.com/300x450/000080/FFFFFF?text=Espaco+Profundo",
            "episodes": [
                {
                    "season": 1, "episode": 1, "title": "A Decolagem",
                    "duration": "50 min", "synopsis": "A missão espacial começa com uma descoberta surpreendente.",
                    "stream_url": "https://example-cdn.com/series/espaco/s01e01.m3u8"
                },
                {
                    "season": 1, "episode": 2, "title": "Planeta Desconhecido",
                    "duration": "48 min", "synopsis": "A tripulação aterrissa em um planeta nunca antes explorado.",
                    "stream_url": "https://example-cdn.com/series/espaco/s01e02.m3u8"
                },
                {
                    "season": 1, "episode": 3, "title": "Encontro Alienígena",
                    "duration": "49 min", "synopsis": "Primeiro contato com uma civilização extraterrestre.",
                    "stream_url": "https://example-cdn.com/series/espaco/s01e03.m3u8"
                }
            ]
        }
    ]
}

# =============================================================================
# 🛠️ FUNÇÕES DE GERAÇÃO M3U
# =============================================================================

def generate_movies_m3u(movies_data: Dict, output_path: str) -> int:
    """Gera lista M3U apenas para filmes"""
    count = 0
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        f.write(f'# Atualizado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'# Total de filmes: {len(movies_data["movies"])}\n')
        f.write(f'# Generator: IPTV VOD Single File\n\n')
        
        for movie in movies_data['movies']:
            genre = movie['genre'][0] if movie['genre'] else 'Geral'
            f.write(f'#EXTINF:-1 tvg-id="{movie["id"]}" tvg-name="{movie["title"]}" '
                   f'tvg-logo="{movie["poster"]}" group-title="Filmes/{genre}", '
                   f'{movie["title"]} ({movie["year"]})\n')
            f.write(f'{movie["stream_url"]}\n\n')
            count += 1
    
    return count

def generate_series_m3u(series_data: Dict, output_path: str) -> int:
    """Gera lista M3U apenas para séries"""
    count = 0
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        f.write(f'# Atualizado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'# Total de séries: {len(series_data["series"])}\n')
        f.write(f'# Generator: IPTV VOD Single File\n\n')
        
        for series in series_data['series']:
            genre = series['genre'][0] if series['genre'] else 'Geral'
            for episode in series['episodes']:
                episode_name = f"S{episode['season']:02d}E{episode['episode']:02d} - {episode['title']}"
                full_title = f"{series['title']} - {episode_name}"
                
                f.write(f'#EXTINF:-1 tvg-id="{series["id"]}" tvg-name="{series["title"]}" '
                       f'tvg-logo="{series["poster"]}" group-title="Séries/{genre}", '
                       f'{full_title}\n')
                f.write(f'{episode["stream_url"]}\n\n')
                count += 1
    
    return count

def generate_full_m3u(movies_data: Dict, series_data: Dict, output_path: str) -> tuple:
    """Gera lista M3U completa (filmes + séries)"""
    movies_count = 0
    series_count = 0
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        f.write(f'# Atualizado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'# Lista Completa - Filmes e Séries\n')
        f.write(f'# Generator: IPTV VOD Single File\n\n')
        
        # Seção Filmes
        f.write('# ============================================\n')
        f.write('# FILMES\n')
        f.write('# ============================================\n\n')
        
        for movie in movies_data['movies']:
            genre = movie['genre'][0] if movie['genre'] else 'Geral'
            f.write(f'#EXTINF:-1 tvg-id="{movie["id"]}" tvg-name="{movie["title"]}" '
                   f'tvg-logo="{movie["poster"]}" group-title="Filmes", '
                   f'{movie["title"]} ({movie["year"]})\n')
            f.write(f'{movie["stream_url"]}\n')
            movies_count += 1
        
        f.write('\n')
        
        # Seção Séries
        f.write('# ============================================\n')
        f.write('# SÉRIES\n')
        f.write('# ============================================\n\n')
        
        for series in series_data['series']:
            for episode in series['episodes']:
                episode_name = f"S{episode['season']:02d}E{episode['episode']:02d}"
                full_title = f"{series['title']} - {episode_name} - {episode['title']}"
                
                f.write(f'#EXTINF:-1 tvg-id="{series["id"]}" tvg-name="{series["title"]}" '
                       f'tvg-logo="{series["poster"]}" group-title="Séries", '
                       f'{full_title}\n')
                f.write(f'{episode["stream_url"]}\n')
                series_count += 1
    
    return movies_count, series_count

# =============================================================================
# 🔍 FUNÇÕES DE VALIDAÇÃO
# =============================================================================

def validate_url(url: str, timeout: int = 5) -> bool:
    """Valida se uma URL está acessível"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def validate_all_links(movies_data: Dict, series_data: Dict) -> Dict:
    """Valida todos os links e retorna estatísticas"""
    results = {
        'movies_total': 0,
        'movies_valid': 0,
        'episodes_total': 0,
        'episodes_valid': 0,
        'movies_failed': [],
        'episodes_failed': []
    }
    
    print("\n🔍 Validando links de filmes...")
    for movie in movies_data['movies']:
        results['movies_total'] += 1
        is_valid = validate_url(movie['stream_url'])
        if is_valid:
            results['movies_valid'] += 1
            print(f"  ✓ {movie['title']}")
        else:
            results['movies_failed'].append(movie['title'])
            print(f"  ✗ {movie['title']}")
    
    print("\n🔍 Validando links de séries...")
    for series_item in series_data['series']:
        for episode in series_item['episodes']:
            results['episodes_total'] += 1
            is_valid = validate_url(episode['stream_url'])
            ep_title = f"{series_item['title']} - S{episode['season']}E{episode['episode']}"
            if is_valid:
                results['episodes_valid'] += 1
                print(f"  ✓ {ep_title}")
            else:
                results['episodes_failed'].append(ep_title)
                print(f"  ✗ {ep_title}")
    
    return results

# =============================================================================
# 📊 FUNÇÕES DE RELATÓRIO
# =============================================================================

def print_summary(movies_count: int, series_count: int, total_count: int, output_dir: str):
    """Imprime resumo da geração"""
    print("\n" + "=" * 70)
    print("                    📊 RESUMO DA GERAÇÃO")
    print("=" * 70)
    print(f"  🎬 Filmes gerados:        {movies_count}")
    print(f"  📺 Episódios gerados:     {series_count}")
    print(f"  📦 Total de entradas:     {total_count}")
    print(f"  📁 Diretório de saída:    {output_dir}")
    print(f"  ⏰ Data de geração:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def print_validation_summary(results: Dict):
    """Imprime resumo da validação"""
    print("\n" + "=" * 70)
    print("                    🔍 RESUMO DA VALIDAÇÃO")
    print("=" * 70)
    print(f"  🎬 Filmes válidos:        {results['movies_valid']}/{results['movies_total']}")
    print(f"  📺 Episódios válidos:     {results['episodes_valid']}/{results['episodes_total']}")
    
    if results['movies_failed']:
        print(f"\n  ⚠️  Filmes com links quebrados:")
        for title in results['movies_failed']:
            print(f"      - {title}")
    
    if results['episodes_failed']:
        print(f"\n  ⚠️  Episódios com links quebrados:")
        for title in results['episodes_failed']:
            print(f"      - {title}")
    
    print("=" * 70)

# =============================================================================
# 💾 FUNÇÕES DE EXPORTAÇÃO JSON (OPCIONAL)
# =============================================================================

def export_json(data: Dict, output_path: str):
    """Exporta dados para arquivo JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ JSON exportado: {output_path}")

# =============================================================================
# 🚀 FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal do gerador IPTV VOD"""
    
    print("\n" + "=" * 70)
    print("          🎬 IPTV VOD GENERATOR - SOLUÇÃO COMPLETA")
    print("=" * 70)
    print("  Gerando listas M3U para filmes e séries...")
    print("=" * 70 + "\n")
    
    # Criar diretórios
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'lists')
    db_dir = os.path.join(base_dir, 'database')
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(db_dir, exist_ok=True)
    
    # Exportar JSONs (opcional - para backup)
    print("💾 Exportando bancos de dados JSON...")
    export_json(MOVIES_DATA, os.path.join(db_dir, 'movies.json'))
    export_json(SERIES_DATA, os.path.join(db_dir, 'series.json'))
    
    # Gerar listas M3U
    print("\n📝 Gerando listas M3U...")
    
    movies_count = generate_movies_m3u(
        MOVIES_DATA, 
        os.path.join(output_dir, 'vod_movies.m3u')
    )
    print(f"  ✓ vod_movies.m3u ({movies_count} filmes)")
    
    series_count = generate_series_m3u(
        SERIES_DATA, 
        os.path.join(output_dir, 'vod_series.m3u')
    )
    print(f"  ✓ vod_series.m3u ({series_count} episódios)")
    
    full_movies, full_series = generate_full_m3u(
        MOVIES_DATA, 
        SERIES_DATA, 
        os.path.join(output_dir, 'full_vod.m3u')
    )
    print(f"  ✓ full_vod.m3u ({full_movies + full_series} entradas)")
    
    # Imprimir resumo
    print_summary(movies_count, series_count, full_movies + full_series, output_dir)
    
    # Validação opcional (comentar se não quiser validar)
    validate = input("\n🔍 Deseja validar os links? (s/n): ").strip().lower()
    if validate == 's':
        try:
            results = validate_all_links(MOVIES_DATA, SERIES_DATA)
            print_validation_summary(results)
        except Exception as e:
            print(f"\n⚠️  Erro na validação: {e}")
    
    # URLs para uso
    print("\n" + "=" * 70)
    print("                    🔗 URLS PARA IMPORTAÇÃO")
    print("=" * 70)
    print("  Copie estas URLs para seu player IPTV:")
    print("\n  📦 Lista Completa:")
    print(f"     file://{os.path.join(output_dir, 'full_vod.m3u')}")
    print("\n  🎬 Apenas Filmes:")
    print(f"     file://{os.path.join(output_dir, 'vod_movies.m3u')}")
    print("\n  📺 Apenas Séries:")
    print(f"     file://{os.path.join(output_dir, 'vod_series.m3u')}")
    print("=" * 70)
    
    print("\n✅ Processo concluído com sucesso!\n")
    
    return 0

# =============================================================================
# 🎯 EXECUÇÃO
# =============================================================================

if __name__ == '__main__':
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        exit(1)