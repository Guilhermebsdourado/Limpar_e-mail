import os
caixa_de_entrada = [
    {"remetente": "noreply@steampowered.com", "assunto": "Grounded, da sua lista de desejos, está em oferta!"},
    {"remetente": "no-reply@pandape.com.br", "assunto": "Envio de Questionário"},
    {"remetente": "linkedin@em.linkedin.com", "assunto": "Guilherme, agradecemos sua participação no LinkedIn"},
    {"remetente": "messages-noreply@linkedin.com", "assunto": "6 pessoas viram seu perfil"},
    {"remetente": "messages-noreply@linkedin.com", "assunto": "Uma pessoa da empresa Bear System que você talvez conheça"},
    {"remetente": "no-reply@shop.tiktok.com", "assunto": "【180 Hz】Achados para... acabou de ser enviado"},
    {"remetente": "contadigitalvivo@vivo.com.br", "assunto": "Sua Fatura Digital Vivo Chegou"},
]

def adicionar_regra():
    while True:
        print("Quer adicionar alguma coisa?")
        print("1 - palavra importante")
        print("2 - palavra lixo")
        print("3 - frase importante")
        print("4 - frase lixo")
        print("5 - Pode rodar o sistema, já está como eu quero")
        opcao = input("Escolha: ")
        try: 
            numero = int(opcao)
        except ValueError:
            os.system("cls")
            print("Isso não é um número inteiro válido. Tente novamente!")
            print("-----------------------------------------------------")
            continue
        
        if numero == 5:
            os.system("cls")
            break
        elif 0 < numero <= 4:
            while True:
                texto = input("Digite a palavra ou frase: ").lower()

                if numero == 1 and len(texto.split()) == 1:
                    PISTAS_IMPORTANTES.append(texto)
                    print("Foi adicionada no sistema")
                    break

                elif numero == 1 and len(texto.split()) != 1:
                    print("-----------------------------------------------------")
                    print("❌ Coloque apenas uma palavra nessa opção ❌")

                elif numero == 2 and len(texto.split()) == 1:
                    PISTAS_LIXO.append(texto)
                    print("Foi adicionada no sistema")
                    break

                elif numero == 2 and len(texto.split()) != 1:
                    print("-----------------------------------------------------")
                    print("❌ Coloque apenas uma palavra nessa opção ❌")

                elif numero == 3 and len(texto.split()) > 1:
                    FRASES_IMPORTANTES.append(texto)
                    print("Foi adicionada no sistema")
                    break

                elif numero == 3 and len(texto.split()) <= 1:
                    print("-----------------------------------------------------")
                    print("❌ Nessa opção coloque uma frase (2 palavras ou mais) ❌")
                    
                elif numero == 4 and len(texto.split()) > 1:
                    FRASES_LIXO.append(texto)
                    print("Foi adicionada no sistema")
                    break

                elif numero == 4 and len(texto.split()) <= 1:
                    print("-----------------------------------------------------")
                    print("❌ Nessa opção coloque uma frase (2 palavras ou mais) ❌")

                else:
                    os.system("cls")
                    
                print("-----------------------------------------------------")
                persistir = input("Quer tentar em outra opção? [s] [n] ")

                if persistir.lower() == "s":
                    os.system("cls")
                    break
                elif persistir.lower() == "n":
                    os.system("cls")
                    print(f"Okk, vamos tentar novamente na opção {numero}")
                else:
                    os.system("cls")
                    print("Como nenhuma das duas opções foram selecionadas.\nO sistema vai voltar para o começo")
                    break

        else:
            print("Opção inválida")
            continue

def pegar_dominio(email):
    remetente = email["remetente"]
    partes = remetente.split("@")
    return partes[1]

def pegar_palavras(email):
    palavras_boas = []          # lista vazia para ir guardando

    assunto = email['assunto'].lower()
    
    acentos = ",.!?:;()【】-|"

    for acento in acentos:
        assunto = assunto.replace(acento, " ")
    
    assunto = assunto.split()

    for i in assunto:
        numletras = len(i)
        if numletras >= 4:
            palavras_boas.append(i)

    return palavras_boas

def pegar_pistas(email):
    dominio = [pegar_dominio(email)]
    palavras = pegar_palavras(email) 
    return dominio + palavras

FRASES_IMPORTANTES = ["acabou de ser enviado"]
FRASES_LIXO = ["lista de desejos", "black friday", "viram seu perfil", "talvez conheça", "agradecemos sua participação no LinkedIn"]
PISTAS_IMPORTANTES = ["vivo.com.br", "fatura", "enviado"]
PISTAS_LIXO = ["steampowered.com", "linkedin.com", "oferta"]

def classificar(email):
    assunto = email["assunto"].lower()

    for frase in FRASES_IMPORTANTES:
        if frase in assunto:
            return "importante"

    for frase_lixo in FRASES_LIXO:
        if frase_lixo.lower() in assunto:
            return "lixo"
        
    for palavras in pegar_pistas(email):
        if palavras in PISTAS_IMPORTANTES:
            return "importante"
        elif palavras in PISTAS_LIXO:
            return "lixo"
    return "não sei"
    
adicionar_regra()

for email in caixa_de_entrada:
    print(classificar(email), "->", email["assunto"])