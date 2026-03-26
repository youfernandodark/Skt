# gerador.py corrigido
def gerar_m3u_com_infos(lista_conteudo):
    arquivo_m3u = "#EXTM3U\n\n"
    
    for item in lista_conteudo:
        # Determina se é série ou filme para ajudar o player
        tipo = "series" if "S01" in item["titulo"] or "Séries" in item["grupo"] else "movie"
        
        linha = (
            f'#EXTINF:-1 tvg-id="{item["id"]}" '
            f'tvg-logo="{item["logo"]}" '
            f'group-title="{item["grupo"]}" '
            f'tvg-type="{tipo}" ' # Tag extra para reconhecimento
            f'year="{item.get("ano", "")}" '
            f'description="{item.get("sinopse", "")}", '
            f'{item["titulo"]}\n'
            f'{item["url"]}\n\n'
        )
        arquivo_m3u += linha
    
    return arquivo_m3u

# ... resto do código de salvamento permanece igual
