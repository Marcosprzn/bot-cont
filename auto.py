import os
import time
import sys
import traceback
from datetime import datetime
from pywinauto import Desktop, Application, ElementNotFoundError
from pywinauto.findwindows import find_elements

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "erro_auto.txt")


def log_erro(mensagem):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== {timestamp} ===\n")
        f.write(mensagem)
        f.write("\n\n")


def listar_janelas():
    texto = "\n--- Janelas abertas ---\n"
    elems = find_elements(control_type="Window", backend="uia")
    for e in elems:
        nome = e.name if e.name else ""
        if nome.strip():
            texto += f"  - '{nome}' (handle: {e.handle})\n"
    texto += "------------------------\n"
    print(texto)
    return texto


def main():
    print("Aguardando 5 segundos...")
    time.sleep(5)

    # --- TENTATIVA 1: buscar campo direto no Desktop ---
    print("Tentativa 1: buscar campo direto no Desktop...")
    desktop = Desktop(backend="uia")
    try:
        campo = desktop.child_window(
            automation_id="66786",
            control_type="Edit"
        ).wait("visible", timeout=5)
        campo.set_focus()
        campo.select()
        time.sleep(0.3)
        campo.type_keys("100283", with_spaces=False)
        print("Codigo '100283' inserido com sucesso!")
        return
    except ElementNotFoundError:
        print("  -> Campo nao encontrado no Desktop.")

    # --- TENTATIVA 2: procurar janela MEGA e buscar dentro dela ---
    print("Tentativa 2: buscar janela MEGA...")
    elems = find_elements(control_type="Window", backend="uia")
    janela_info = None
    for e in elems:
        nome = e.name if e.name else ""
        if "MEGA" in nome.upper():
            janela_info = e
            print(f"  Janela MEGA encontrada: '{nome}' (handle: {e.handle})")
            break

    if janela_info is None:
        raise ElementNotFoundError(
            "Campo 66786 nao encontrado em lugar nenhum.\n"
            "Confirme que o MEGA ERP esta aberto, visivel, e no campo correto."
        )

    app = Application(backend="uia").connect(handle=janela_info.handle)
    janela = app.window(handle=janela_info.handle)
    janela.set_focus()
    time.sleep(0.5)

    campo = janela.child_window(
        automation_id="66786",
        control_type="Edit"
    ).wait("visible", timeout=8)

    campo.set_focus()
    campo.select()
    time.sleep(0.3)
    campo.type_keys("100283", with_spaces=False)
    print("Codigo '100283' inserido com sucesso!")


if __name__ == "__main__":
    try:
        main()
    except ElementNotFoundError as e:
        erro = traceback.format_exc()
        janelas = listar_janelas()
        msg = f"Erro: Campo nao encontrado\n{e}\n\n{erro}\n{janelas}"
        log_erro(msg)
        print(f"\nErro: Campo nao encontrado - {e}")
        print(f"Log salvo em: {LOG_FILE}")
        sys.exit(1)
    except Exception as e:
        erro = traceback.format_exc()
        msg = f"Erro inesperado\n{e}\n\n{erro}"
        log_erro(msg)
        print(f"\nErro inesperado: {e}")
        print(f"Log salvo em: {LOG_FILE}")
        sys.exit(1)
