import os
import time
import sys
import traceback
from datetime import datetime
from pywinauto import Application, ElementNotFoundError
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


def encontrar_janela_raiz():
    """Encontra a janela principal do MEGA ERP pelo nome."""
    elems = find_elements(control_type="Window", backend="uia")
    for e in elems:
        nome = e.name if e.name else ""
        if "MEGA" in nome.upper():
            print(f"  Janela MEGA encontrada: '{nome}'")
            app = Application(backend="uia").connect(handle=e.handle)
            janela = app.window(handle=e.handle)
            janela.set_focus()
            return janela, app

    raise ElementNotFoundError(
        "MEGA ERP nao encontrado.\n"
        "Confirme que o programa esta aberto e visivel."
    )


def main():
    print("Aguardando 5 segundos...")
    time.sleep(5)

    raiz, app = encontrar_janela_raiz()
    time.sleep(0.5)

    # --- PASSO 1: digitar codigo no campo Edit ---
    print("Passo 1/3: Digitando codigo 100283...")
    campo = raiz.child_window(
        auto_id="66786", control_type="Edit"
    ).wait("visible", timeout=8)
    campo.set_focus()
    campo.select()
    time.sleep(0.3)
    campo.type_keys("100283", with_spaces=False)
    print("  OK")

    # --- PASSO 2: clicar em "Excluir" ---
    print("Passo 2/3: Clicando em Excluir...")
    btn_excluir = raiz.child_window(
        auto_id="66792", control_type="Button"
    ).wait("visible", timeout=8)
    btn_excluir.click()
    time.sleep(0.5)
    print("  OK")

    # --- PASSO 3: clicar em "Sim" (confirmar) ---
    print("Passo 3/3: Confirmando exclusao...")
    time.sleep(1)
    try:
        btn_sim = raiz.child_window(
            auto_id="1578668", control_type="Button"
        ).wait("visible", timeout=5)
    except ElementNotFoundError:
        btn_sim = app.window(
            auto_id="1578668", control_type="Button"
        ).wait("visible", timeout=5)
    btn_sim.click()
    print("  OK")

    print("\nAutomacao concluida com sucesso!")


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
