def gerar_m3u_com_infos(lista_conteudo):
    arquivo_m3u = "#EXTM3U\n\n"
    
    for item in lista_conteudo:
        # Melhor detecção de séries
        tipo = "series" if ("S01" in item["titulo"] or 
                           "Série" in item["grupo"] or 
                           "E01" in item["titulo"]) else "movie"
        
        # Garantindo que campos opcionais tenham valores padrão
        ano = item.get("ano", "")
        sinopse = item.get("sinopse", "").replace('"', '\\"')  # Escapa aspas na sinopse
        
        # Construção da linha de metadados
        linha = (
            f'#EXTINF:-1 tvg-id="{item["id"]}" '
            f'tvg-logo="{item["logo"]}" '
            f'group-title="{item["grupo"]}" '
            f'tvg-type="{tipo}" '
            f'year="{ano}" '
            f'description="{sinopse}",{item["titulo"]}\n'
            f'{item["url"]}\n\n'
        )
        arquivo_m3u += linha
    
    return arquivo_m3u

# Exemplo de uso
if __name__ == "__main__":
    # Importando os dados
    from organizador import meu_vod
    
    # Gerando o arquivo M3U
    conteudo_m3u = gerar_m3u_com_infos(meu_vod)
    
    # Salvando em arquivo
    with open("playlist.m3u", "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo_m3u)
    
    print("Arquivo playlist.m3u gerado com sucesso!")