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


MEMORIA = {
    "importante": {},
    "lixo": {},
}

def nota_da_pista(pista):
    vezes_importante = MEMORIA["importante"].get(pista, 0)
    vezes_lixo = MEMORIA["lixo"].get(pista, 0)
    return (vezes_importante + 1) / (vezes_importante + vezes_lixo + 2)

def aprender(email, categoria):
    contagem = MEMORIA[categoria]
    for pista in pegar_pistas(email):
        contagem[pista] = contagem.get(pista, 0) + 1

def calcular_nota(email):
    notas = []

    for pista in pegar_pistas(email):
        conhece = pista in MEMORIA["importante"] or pista in MEMORIA["lixo"]
        if conhece:
            notas.append(nota_da_pista(pista))
    if len(notas) == 0:
        return None
    else:
        return sum(notas) / len(notas)
        
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

    nota = calcular_nota(email)

    if nota is None:
        return "não sei"
    elif nota >= 0.65:
        return "importante"
    elif nota <= 0.35:
        return "lixo"
    else:
        return "não sei"
    
# ---------------------------------------------------------------
# Testes antigos (já cumpriram o papel, ficam comentados)
# ---------------------------------------------------------------
# adicionar_regra()
#
# for email in caixa_de_entrada:
#     print(classificar(email), "->", email["assunto"])
#
# print(MEMORIA)
# print(nota_da_pista("fatura"))
# print(nota_da_pista("oferta"))
# print(nota_da_pista("pizza"))
#
# email_teste1 = {"remetente": "fatura@vivo.com.br", "assunto": "Nova fatura disponível"}
# email_teste2 = {"remetente": "promo@steampowered.com", "assunto": "Nova oferta na sua lista"}
# email_teste3 = {"remetente": "oi@pizzaria.com", "assunto": "Promoção de pizza"}
# print(calcular_nota(email_teste1))
# print(calcular_nota(email_teste2))
# print(calcular_nota(email_teste3))

# ---------------------------------------------------------------
# 1. Aprender
# ---------------------------------------------------------------
aprender(caixa_de_entrada[6], "importante")   # Vivo
aprender(caixa_de_entrada[5], "importante")   # TikTok
aprender(caixa_de_entrada[0], "lixo")         # Steam

# ---------------------------------------------------------------
# 2. Testar com e-mails novos (nenhuma regra fixa cobre esses dois)
# ---------------------------------------------------------------
email_teste4 = {"remetente": "loja@shop.tiktok.com", "assunto": "Seus achados chegaram"}
email_teste5 = {"remetente": "ofertas@lojanova.com", "assunto": "Grounded e outros desejos"}

print(classificar(email_teste4))
print(classificar(email_teste5))