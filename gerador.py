def gerar_m3u_com_infos(lista_conteudo):
    arquivo_m3u = "#EXTM3U\n\n"
    for item in lista_conteudo:
        # Normalização das chaves (removendo espaços se possível na origem)
        # Assumindo aqui que corrigiremos as chaves para sem espaços
        titulo = item.get("titulo", "Desconhecido")
        grupo = item.get("grupo", "Geral")
        item_id = item.get("id", "")
        logo = item.get("logo", "")
        ano = item.get("ano", "")
        sinopse = item.get("sinopse", "").replace('"', '\\"').replace('\n', ' ')
        url = item.get("url", "")

        # Detecção de tipo mais limpa
        tipo = "movie"
        if "S01" in titulo or "E01" in titulo or "Série" in grupo:
            tipo = "series"
        
        # Construção da linha (sem espaços extras dentro das aspas)
        linha = (
            f'#EXTINF:-1 tvg-id="{item_id}" '
            f'tvg-logo="{logo}" '
            f'group-title="{grupo}" '
            f'tvg-type="{tipo}" '
            f'year="{ano}" '
            f'description="{sinopse}",{titulo}\n'
            f'{url}\n\n'
        )
        arquivo_m3u += linha

    return arquivo_m3u

if __name__ == "__main__":
    # Importando os dados
    from organizador import meu_vod
    
    # Gerando o arquivo M3U
    conteudo_m3u = gerar_m3u_com_infos(meu_vod)

    # Salvando em arquivo
    with open("playlist.m3u", "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo_m3u)

    print("Arquivo playlist.m3u gerado com sucesso!")