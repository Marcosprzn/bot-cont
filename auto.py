import os
import time
import sys
import traceback
from datetime import datetime
import pyautogui
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


def digitar_texto(raiz, app, texto, auto_id, control_type, x, y, descricao):
    print(f"  {descricao}: ", end="")
    sys.stdout.flush()

    # Tentativa 1: UIA na janela raiz
    try:
        campo = raiz.child_window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        campo.set_focus()
        campo.select()
        time.sleep(0.2)
        campo.type_keys(texto, with_spaces=False)
        print("OK (UIA)")
        return True
    except Exception:
        pass

    # Tentativa 2: UIA no app
    try:
        campo = app.window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        campo.set_focus()
        campo.select()
        time.sleep(0.2)
        campo.type_keys(texto, with_spaces=False)
        print("OK (UIA app)")
        return True
    except Exception:
        pass

    # Tentativa 3: pyautogui (fallback coordenadas)
    try:
        pyautogui.click(x, y)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.write(texto)
        print("OK (pyautogui)")
        return True
    except Exception:
        print("FALHOU")
        return False


def clicar_botao(raiz, app, auto_id, control_type, x, y, descricao):
    print(f"  {descricao}: ", end="")
    sys.stdout.flush()

    # Tentativa 1: UIA na janela raiz
    try:
        btn = raiz.child_window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        btn.click()
        print("OK (UIA)")
        return True
    except Exception:
        pass

    # Tentativa 2: UIA no app
    try:
        btn = app.window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        btn.click()
        print("OK (UIA app)")
        return True
    except Exception:
        pass

    # Tentativa 3: pyautogui (fallback coordenadas)
    try:
        pyautogui.click(x, y)
        print(f"OK (pyautogui)")
        return True
    except Exception:
        print("FALHOU")
        return False


def main():
    pyautogui.FAILSAFE = True

    print("Aguardando 5 segundos...")
    time.sleep(5)

    raiz, app = encontrar_janela_raiz()
    time.sleep(0.5)

    print("\n--- Executando passos ---")

    passo1 = digitar_texto(
        raiz, app,
        texto="100283",
        auto_id="66786", control_type="Edit",
        x=343, y=147,
        descricao="Passo 1/3 - Digitar codigo"
    )
    time.sleep(0.5)

    passo2 = clicar_botao(
        raiz, app,
        auto_id="66792", control_type="Button",
        x=1231, y=148,
        descricao="Passo 2/3 - Clicar Excluir"
    )
    time.sleep(1)

    passo3 = clicar_botao(
        raiz, app,
        auto_id="1578668", control_type="Button",
        x=665, y=424,
        descricao="Passo 3/3 - Clicar Sim"
    )

    print("\n--- Resumo ---")
    print(f"  Passo 1: {'OK' if passo1 else 'FALHOU'}")
    print(f"  Passo 2: {'OK' if passo2 else 'FALHOU'}")
    print(f"  Passo 3: {'OK' if passo3 else 'FALHOU'}")

    if passo1 and passo2 and passo3:
        print("\nAutomacao concluida com sucesso!")
    else:
        print("\nAutomacao concluida com falhas em alguns passos.")


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
