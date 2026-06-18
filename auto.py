import os
import time
import sys
import ctypes
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
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 0
    )


def mostrar_console():
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 1
    )


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


def botao_sim_existe():
    """Verifica se o botao 'Sim' (popup de confirmacao) ainda esta visivel."""
    try:
        botoes = find_elements(control_type="Button", backend="uia")
        for b in botoes:
            if b.name and b.name.strip() == "Sim":
                return True
    except Exception:
        pass
    return False


def digitar_texto(texto, x, y):
    aguardar_se_pausado()
    try:
        pyautogui.click(x, y)
        time.sleep(0.15)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.write(texto)
        return True
    except Exception:
        return False


def clicar(x, y):
    aguardar_se_pausado()
    try:
        pyautogui.click(x, y)
        return True
    except Exception:
        return False


def esperar_exclusao(timeout=30):
    """Aguarda o popup de confirmacao ('Sim') fechar apos exclusao."""
    for _ in range(timeout * 2):
        aguardar_se_pausado()
        if not botao_sim_existe():
            time.sleep(0.3)
            return True
        time.sleep(0.5)
    return False


def processar_codigo(codigo):
    aguardar_se_pausado()

    if not digitar_texto(str(codigo), 343, 147):
        return False
    time.sleep(0.2)

    if not clicar(1231, 148):
        return False
    time.sleep(0.3)

    if not clicar(665, 424):
        return False

    if not esperar_exclusao():
        return False

    return True


def main():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05

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

    iniciar_listener_f8()

    time.sleep(0.5)
    esconder_console()
    time.sleep(0.5)
    focar_janela(raiz)

    sucessos = 0
    falhas = 0
    tempo_inicio = time.time()
    ultimo_log = time.time()

    try:
        for i, codigo in enumerate(range(inicio, fim + 1), 1):
            aguardar_se_pausado()
            focar_janela(raiz)

            ok = processar_codigo(codigo)
            if ok:
                sucessos += 1
            else:
                falhas += 1

            agora = time.time()
            if agora - ultimo_log >= 2:
                decorrido = int(agora - tempo_inicio)
                print(f"[{i}/{total}] Codigo {codigo}: {'OK' if ok else 'FALHA'} "
                      f"({decorrido // 60}m {decorrido % 60}s)")
                ultimo_log = agora

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
        input("Pressione Enter para sair...")


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
