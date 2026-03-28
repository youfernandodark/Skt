import os

def gerar_m3u():
    arquivo_input = "automacao_vod/links_brutos.txt"
    arquivo_output = "lista_final_vod.m3u"
    
    if not os.path.exists(arquivo_input):
        print("Arquivo de entrada não encontrado!")
        return

    with open(arquivo_output, "w", encoding="utf-8") as f_out:
        f_out.write("#EXTM3U\n")
        
        with open(arquivo_input, "r", encoding="utf-8") as f_in:
            for linha in f_in:
                linha = linha.strip()
                if not linha or "|" not in linha:
                    continue
                
                # Formato esperado no TXT: Nome do Filme | URL | Categoria
                partes = linha.split("|")
                nome = partes[0].strip()
                url = partes[1].strip()
                categoria = partes[2].strip() if len(partes) > 2 else "Geral"

                # Criando a entrada VOD formatada
                f_out.write(f'#EXTINF:-1 group-title="{categoria}",{nome}\n')
                f_out.write(f'{url}\n')

    print("Lista M3U gerada com sucesso!")

if __name__ == "__main__":
    gerar_m3u()
