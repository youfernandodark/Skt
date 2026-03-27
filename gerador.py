def gerar_m3u_com_infos(lista_conteudo):
    arquivo_m3u = "#EXTM3U\n\n"
    
    for item in lista_conteudo:
        # Determina se é série ou filme para ajudar o player
        # [span_0](start_span)Verifica se existe "S01" no título ou se o grupo é de séries[span_0](end_span)
        tipo = "series" if "S01" in item["titulo"] or "Séries" in item["grupo"] else "movie"
        
        # Construção da linha de metadados sem espaços extras antes da vírgula
        linha = (
            f'#EXTINF:-1 tvg-id="{item["id"]}" '
            f'tvg-logo="{item["logo"]}" '
            f'group-title="{item["grupo"]}" '
            f'tvg-type="{tipo}" '
            f'year="{item.get("ano", "")}" '
            f'description="{item.get("sinopse", "")}",{item["titulo"]}\n'
            f'{item["url"]}\n\n'
        )
        arquivo_m3u += linha
    
    return arquivo_m3u
