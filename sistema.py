import os
import json

from gmail import buscar_emails, mover_para_limpeza, mover_antigos_para_lixeira, PASTA_LIMPEZA
# Agora a caixa de entrada vem do Gmail (veja o final do arquivo)
caixa_de_entrada = []


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
        
def adicionar_em_lote():
    tipo = input("Essas regras são (i)mportantes ou (l)ixo? ").strip().lower()
    if tipo != "i" and tipo != "l":
        print("Opção inválida")
        return

    texto = input("Cole tudo separado por vírgula:\n").lower()
    adicionados = 0
    repetidos = 0

    for item in texto.split(","):
        item = item.strip()
        if item == "":
            continue

        if len(item.split()) == 1:
            if tipo == "i":
                lista = PISTAS_IMPORTANTES
            else:
                lista = PISTAS_LIXO
        else:
            if tipo == "i":
                lista = FRASES_IMPORTANTES
            else:
                lista = FRASES_LIXO

        if item in lista:
            repetidos += 1
            continue

        lista.append(item)
        adicionados += 1

    salvar()
    print(f"✅ {adicionados} regras adicionadas ({repetidos} já existiam).")
    print("-----------------------------------------------------")


def adicionar_regra():
    while True:
        print("Quer adicionar alguma coisa?")
        print("1 - palavra importante")
        print("2 - palavra lixo")
        print("3 - frase importante")
        print("4 - frase lixo")
        print("5 - Pode rodar o sistema, já está como eu quero")
        print("6 - Adicionar várias de uma vez (separadas por vírgula)")
        print("7 - Apagar e-mails com mais de 4 anos")
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
        elif numero == 6:
            adicionar_em_lote()
            continue
        elif numero == 7:
            mover_antigos_para_lixeira(anos=4)
            print("-----------------------------------------------------")
            continue
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
def perguntar_categoria():
    while True:
        resposta = input("   É (i)mportante ou (l)ixo? ").strip().lower()
        if resposta == "i":
            return "importante"
        elif resposta == "l":
            return "lixo"
        print("   Digite i ou l.")


def revisar_caixa():
    decididos = 0
    lixo = []   # uids dos e-mails que vão para a pasta de limpeza

    for email in caixa_de_entrada:
        print()
        print("De:", email["remetente"])
        print("Assunto:", email["assunto"])

        palpite = classificar(email)

        if palpite == "não sei":
            print("   Não sei classificar esse.")
            categoria = perguntar_categoria()
            aprender(email, categoria)
        else:
            print(f"   → {palpite.upper()}")
            categoria = palpite
            decididos += 1

        if categoria == "lixo":
            lixo.append(email["uid"])

    print()
    print(f"Decidi sozinho {decididos} de {len(caixa_de_entrada)}")
    return lixo


ARQUIVO_MEMORIA = "memoria.json"

def salvar():
    dados = {
        "memoria": MEMORIA,
        "pistas_importantes": PISTAS_IMPORTANTES,
        "pistas_lixo": PISTAS_LIXO,
        "frases_importantes": FRASES_IMPORTANTES,
        "frases_lixo": FRASES_LIXO,
    }
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def carregar():
    if not os.path.exists(ARQUIVO_MEMORIA):
        print("Primeira vez rodando: começando do zero.")
        return

    with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    MEMORIA["importante"] = dados["memoria"]["importante"]
    MEMORIA["lixo"] = dados["memoria"]["lixo"]

    PISTAS_IMPORTANTES.clear()
    PISTAS_IMPORTANTES.extend(dados["pistas_importantes"])
    PISTAS_LIXO.clear()
    PISTAS_LIXO.extend(dados["pistas_lixo"])
    FRASES_IMPORTANTES.clear()
    FRASES_IMPORTANTES.extend(dados["frases_importantes"])
    FRASES_LIXO.clear()
    FRASES_LIXO.extend(dados["frases_lixo"])

    print("Memória carregada!")


carregar()
adicionar_regra()

TAMANHO_LOTE = 1000
inicio = 0   # de onde começar a ler (0 = o e-mail mais novo)

while True:
    print()
    print(f"Buscando e-mails {inicio + 1} a {inicio + TAMANHO_LOTE}...")
    caixa_de_entrada = buscar_emails(inicio=inicio, quantidade=TAMANHO_LOTE)

    if len(caixa_de_entrada) == 0:
        print("Acabaram os e-mails da Caixa de entrada! 🎉")
        break

    lixo = revisar_caixa()
    salvar()

    print()
    print(f"{len(lixo)} e-mails foram classificados como LIXO.")
    movidos = False
    if lixo:
        confirma = input("Mover esses e-mails para a LIXEIRA do Gmail? (s/n) ").strip().lower()
        if confirma == "s":
            mover_para_limpeza(lixo)
            movidos = True
        else:
            print("Ok, nada foi movido.")

    # Os e-mails movidos saem da Caixa de entrada, então a lista "anda".
    # Só pulamos os que FICARAM lá.
    if movidos:
        inicio += len(caixa_de_entrada) - len(lixo)
    else:
        inicio += len(caixa_de_entrada)

    continuar = input("\nIr para o próximo lote? (s/n) ").strip().lower()
    if continuar != "s":
        print("Até a próxima!")
        break