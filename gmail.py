"""
Conexão com o Gmail (Aula 6)

Este arquivo só faz duas coisas:
  1. buscar_emails()       -> lê os e-mails mais recentes da Caixa de entrada
  2. mover_para_limpeza()  -> move os e-mails escolhidos para uma pasta (marcador)

Nada é apagado. Os e-mails vão para o marcador "Limpeza-Python" no Gmail,
e você confere e apaga lá mesmo, se quiser.

O e-mail e a senha de app ficam no arquivo .env (que NUNCA vai para o GitHub).
"""

import datetime
import os

from dotenv import load_dotenv
from imap_tools import AND, MailBox

load_dotenv()  # lê o arquivo .env e coloca os valores nas variáveis de ambiente

SERVIDOR = "imap.gmail.com"
EMAIL = os.getenv("GMAIL_EMAIL")
SENHA_APP = os.getenv("GMAIL_SENHA_APP")
PASTA_LIMPEZA = "Limpeza-Python"

# True  -> o lixo vai direto para a LIXEIRA do Gmail
#          (fica lá 30 dias e depois o Gmail apaga sozinho)
# False -> o lixo vai para o marcador Limpeza-Python (para conferir antes)
USAR_LIXEIRA = True


def conferir_credenciais():
    if not EMAIL or not SENHA_APP:
        print("❌ Não achei o e-mail ou a senha de app.")
        print("   Crie o arquivo .env (veja o .env.exemplo) e tente de novo.")
        raise SystemExit


def buscar_emails(inicio=0, quantidade=100):
    """
    Devolve um pedaço da Caixa de entrada, do mais novo para o mais antigo.
    Ex.: inicio=0, quantidade=100   -> e-mails 1 a 100
         inicio=100, quantidade=100 -> e-mails 101 a 200
    """
    conferir_credenciais()
    emails = []
    pedaco = slice(inicio, inicio + quantidade)

    with MailBox(SERVIDOR).login(EMAIL, SENHA_APP, "INBOX") as caixa:
        for msg in caixa.fetch(limit=pedaco, reverse=True, headers_only=True, mark_seen=False):
            remetente = msg.from_
            if "@" not in remetente:
                remetente = "sem-remetente@desconhecido"
            emails.append({
                "uid": msg.uid,
                "remetente": remetente,
                "assunto": msg.subject,
            })

    return emails


def achar_lixeira(caixa):
    """
    O nome da Lixeira muda com o idioma do Gmail ("[Gmail]/Lixeira", "[Gmail]/Trash"...).
    Mas ela sempre tem a marca especial \\Trash, então procuramos por ela.
    """
    for pasta in caixa.folder.list():
        if "\\Trash" in pasta.flags:
            return pasta.name
    return None


def mover_em_pacotes(caixa, uids, destino, tamanho_pacote=50):
    """Move de 50 em 50. Se um pacote falhar, avisa e continua. Devolve (movidos, falhas)."""
    movidos = 0
    falhas = 0

    for i in range(0, len(uids), tamanho_pacote):
        pacote = uids[i:i + tamanho_pacote]
        try:
            caixa.move(pacote, destino)
        except Exception as erro:
            falhas += len(pacote)
            print(f"   ⚠️ Um pacote de {len(pacote)} falhou: {erro}")
            continue
        movidos += len(pacote)
        print(f"   {movidos}/{len(uids)} movidos...")

    return movidos, falhas


def mover_para_limpeza(uids):
    """Move os e-mails (pelos uids) para a Lixeira ou para o marcador Limpeza-Python."""
    if not uids:
        print("Nada para mover.")
        return

    conferir_credenciais()

    with MailBox(SERVIDOR).login(EMAIL, SENHA_APP, "INBOX") as caixa:
        destino = None
        if USAR_LIXEIRA:
            destino = achar_lixeira(caixa)
            if destino is None:
                print("⚠️ Não achei a Lixeira. Vou usar o marcador Limpeza-Python.")

        if destino is None:
            destino = PASTA_LIMPEZA
            if not caixa.folder.exists(destino):
                caixa.folder.create(destino)

        movidos, falhas = mover_em_pacotes(caixa, uids, destino)

    print(f"✅ {movidos} e-mails movidos para '{destino}'.")
    if falhas > 0:
        print(f"⚠️ {falhas} não foram movidos. Rode de novo para tentar outra vez.")


def data_de_corte(anos):
    """Mesma data de hoje, só que X anos atrás."""
    hoje = datetime.date.today()
    try:
        return hoje.replace(year=hoje.year - anos)
    except ValueError:
        # hoje é 29/02 e o ano de destino não é bissexto
        return hoje.replace(year=hoje.year - anos, day=28)


def mover_antigos_para_lixeira(anos=4):
    """
    Move para a Lixeira todos os e-mails da Caixa de entrada com mais de X anos.
    E-mails com ESTRELA são mantidos (você marcou como importantes).
    """
    conferir_credenciais()
    corte = data_de_corte(anos)

    with MailBox(SERVIDOR).login(EMAIL, SENHA_APP, "INBOX") as caixa:
        # a busca acontece no próprio Gmail, sem baixar os e-mails
        uids = caixa.uids(AND(date_lt=corte, flagged=False))

        if len(uids) == 0:
            print(f"Nenhum e-mail anterior a {corte:%d/%m/%Y}. 👍")
            return

        print()
        print(f"Encontrei {len(uids)} e-mails anteriores a {corte:%d/%m/%Y} (sem estrela).")
        print("Alguns exemplos:")
        for msg in caixa.fetch(uid_list=uids[:5], headers_only=True, mark_seen=False):
            print(f"   {msg.date:%d/%m/%Y}  {msg.from_}  —  {msg.subject}")

        confirma = input(f"\nMover os {len(uids)} para a LIXEIRA? (s/n) ").strip().lower()
        if confirma != "s":
            print("Ok, nada foi movido.")
            return

        destino = achar_lixeira(caixa)
        if destino is None:
            destino = PASTA_LIMPEZA
            if not caixa.folder.exists(destino):
                caixa.folder.create(destino)

        movidos = 0
        falhas = 0
        TAMANHO_PACOTE = 50

        # move de 50 em 50; se um pacote falhar, avisa e continua com o próximo
        for i in range(0, len(uids), TAMANHO_PACOTE):
            pacote = uids[i:i + TAMANHO_PACOTE]
            try:
                caixa.move(pacote, destino)
                movidos += len(pacote)
                print(f"   {movidos}/{len(uids)} movidos...")
            except Exception as erro:
                falhas += len(pacote)
                print(f"   ⚠️ Um pacote de {len(pacote)} falhou: {erro}")

    print(f"✅ {movidos} e-mails antigos movidos para '{destino}'.")
    if falhas > 0:
        print(f"⚠️ {falhas} não foram movidos. Rode a opção 7 de novo para tentar outra vez.")