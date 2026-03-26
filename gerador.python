def gerar_m3u_com_infos(lista_conteudo):
    arquivo_m3u = "#EXTM3U\n\n"
    
    for item in lista_conteudo:
        # Montando a tag EXTINF com informações extras
        linha = (
            f'#EXTINF:-1 tvg-id="{item["id"]}" '
            f'tvg-logo="{item["logo"]}" '
            f'group-title="{item["grupo"]}" '
            f'year="{item.get("ano", "")}" '
            f'description="{item.get("sinopse", "")}", '
            f'{item["titulo"]}\n'
            f'{item["url"]}\n\n'
        )
        arquivo_m3u += linha
    
    return arquivo_m3u

# Executa e salva o arquivo
playlist_final = gerar_m3u_com_infos(meu_vod)

with open("lista_com_infos.m3u", "w", encoding="utf-8") as f:
    f.write(playlist_final)

print("Playlist gerada com sucesso: lista_com_infos.m3u")
