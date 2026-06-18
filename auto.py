import os
import time
import sys
import ctypes
import threading
import traceback
from datetime import datetime

import pyautogui
import keyboard
from pywinauto import Application, ElementNotFoundError
from pywinauto.findwindows import find_elements

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "erro_auto.txt")

pausado = False


def esconder_console():
    janela = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(janela, 0)


def mostrar_console():
    janela = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(janela, 1)


def alternar_pausa():
    global pausado
    pausado = not pausado
    status = "PAUSADO" if pausado else "CONTINUANDO"
    print(f"\n[{status}] F8 para alternar\n")


def iniciar_listener_f8():
    keyboard.on_press_key("f8", lambda _: alternar_pausa())


def aguardar_se_pausado():
    while pausado:
        time.sleep(0.3)


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
    for tentativa in range(10):
        elems = find_elements(control_type="Window", backend="uia")
        for e in elems:
            nome = e.name if e.name else ""
            if "MEGA" in nome.upper():
                print(f"Janela MEGA encontrada: '{nome}'")
                app = Application(backend="uia").connect(handle=e.handle)
                janela = app.window(handle=e.handle)
                janela.set_focus()
                return janela, app
        print(f"Aguardando janela MEGA... ({tentativa + 1}/10)")
        time.sleep(2)
    raise ElementNotFoundError(
        "MEGA ERP nao encontrado.\n"
        "Confirme que o programa esta aberto e visivel."
    )


def focar_janela(janela):
    try:
        janela.set_focus()
    except Exception:
        pass


def digitar_texto(raiz, app, texto, auto_id, control_type, x, y):
    aguardar_se_pausado()

    try:
        campo = raiz.child_window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        campo.set_focus()
        campo.select()
        time.sleep(0.2)
        campo.type_keys(texto, with_spaces=False)
        return True
    except Exception:
        pass

    try:
        campo = app.window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        campo.set_focus()
        campo.select()
        time.sleep(0.2)
        campo.type_keys(texto, with_spaces=False)
        return True
    except Exception:
        pass

    try:
        pyautogui.click(x, y)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.write(texto)
        return True
    except Exception:
        return False


def clicar_botao(raiz, app, auto_id, control_type, x, y):
    aguardar_se_pausado()

    try:
        btn = raiz.child_window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        btn.click()
        return True
    except Exception:
        pass

    try:
        btn = app.window(
            auto_id=auto_id, control_type=control_type
        ).wait("visible", timeout=4)
        btn.click()
        return True
    except Exception:
        pass

    try:
        pyautogui.click(x, y)
        return True
    except Exception:
        return False


def processar_codigo(raiz, app, codigo, total, idx):
    aguardar_se_pausado()
    focar_janela(raiz)
    time.sleep(0.3)

    status = digitar_texto(
        raiz, app,
        texto=str(codigo),
        auto_id="66786", control_type="Edit",
        x=343, y=147,
    )
    if not status:
        return False
    time.sleep(0.3)

    status = clicar_botao(
        raiz, app,
        auto_id="66792", control_type="Button",
        x=1231, y=148,
    )
    if not status:
        return False
    time.sleep(0.5)

    status = clicar_botao(
        raiz, app,
        auto_id="1578668", control_type="Button",
        x=665, y=424,
    )
    return status


def main():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1

    print("=" * 55)
    print("  BOT MEGA ERP - Exclusao em Lote")
    print("=" * 55)
    print("  F8 = Pausar / Continuar")
    print("  Ctrl+C = Parar")
    print("=" * 55)
    print()

    try:
        inicio = int(input("Digite o CODIGO INICIAL: ").strip())
        fim = int(input("Digite o CODIGO FINAL:   ").strip())
    except ValueError:
        print("Codigo invalido. Digite apenas numeros.")
        sys.exit(1)

    if inicio > fim:
        inicio, fim = fim, inicio

    total = fim - inicio + 1
    print(f"\nProcessando {total} codigos: {inicio} ate {fim}")
    print("Conectando ao MEGA ERP...")

    raiz, app = encontrar_janela_raiz()

    # inicia listener do F8 em segundo plano
    iniciar_listener_f8()

    # esconde o console para nao roubar foco
    time.sleep(0.5)
    esconder_console()
    time.sleep(0.5)
    focar_janela(raiz)

    sucessos = 0
    falhas = 0
    tempo_inicio = time.time()

    try:
        for i, codigo in enumerate(range(inicio, fim + 1), 1):
            aguardar_se_pausado()
            focar_janela(raiz)

            ok = processar_codigo(raiz, app, codigo, total, i)
            if ok:
                sucessos += 1
            else:
                falhas += 1

            # mostra progresso no terminal mesmo invisivel
            print(f"[{i}/{total}] Codigo {codigo}: {'OK' if ok else 'FALHA'}")

            # pequena pausa entre ciclos
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n[!] Interrompido pelo usuario.")
    finally:
        mostrar_console()
        print()
        print("=" * 55)
        print("  RESUMO FINAL")
        print("=" * 55)
        print(f"  Total processados: {total}")
        print(f"  Sucessos:          {sucessos}")
        print(f"  Falhas:            {falhas}")
        decorrido = int(time.time() - tempo_inicio)
        print(f"  Tempo total:       {decorrido // 60}m {decorrido % 60}s")
        print("=" * 55)


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
