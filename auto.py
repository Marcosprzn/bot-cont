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
LOG_ERRO = os.path.join(LOG_DIR, "erro_auto.txt")
LOG_PROGRESSO = os.path.join(LOG_DIR, "progresso.log")
LOG_PROGRESSO_TEMP = os.path.join(LOG_DIR, "progresso.tmp")

pausado = False
console_oculto = False


def alternar_pausa():
    global pausado
    pausado = not pausado
    status = "PAUSADO" if pausado else "CONTINUANDO"
    p(f"\n  [{status}] F8 para alternar\n")


def iniciar_listener_f8():
    keyboard.on_press_key("f8", lambda _: alternar_pausa())


def aguardar_se_pausado():
    while pausado:
        time.sleep(0.3)


def _esconder_console():
    global console_oculto
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 0
    )
    console_oculto = True


def _mostrar_console():
    global console_oculto
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 1
    )
    console_oculto = False


def p(msg, end="\n"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if console_oculto:
        with open(LOG_PROGRESSO_TEMP, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}{end}")
    else:
        print(msg, end=end)
        sys.stdout.flush()


def log_erro(mensagem):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_ERRO, "a", encoding="utf-8") as f:
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


def focar_mega(janela):
    for _ in range(3):
        try:
            janela.set_focus()
            return
        except Exception:
            time.sleep(0.3)


def digitar_texto(texto, x, y):
    aguardar_se_pausado()
    pyautogui.click(x, y)
    time.sleep(0.15)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.write(texto, interval=0.02)
    return True


def clicar(x, y, desc=""):
    aguardar_se_pausado()
    pyautogui.click(x, y)
    return True


def esperar_carregamento(timeout=20):
    """Aguarda a tela estabilizar apos clicar Procurar."""
    inicio = time.time()
    try:
        while time.time() - inicio < timeout:
            aguardar_se_pausado()
            botoes = find_elements(control_type="Button", backend="uia")
            for b in botoes:
                if b.name and ("Sim" in b.name or "Excluir" in b.name):
                    time.sleep(0.3)
                    return True
            time.sleep(0.5)
    except Exception:
        pass
    time.sleep(2)
    return True


def _achar_botao_sim():
    """Retorna True se o botao 'Sim' estiver visivel na tela."""
    try:
        botoes = find_elements(control_type="Button", backend="uia")
        for b in botoes:
            if b.name and "Sim" in b.name:
                return True
    except Exception:
        pass
    return None  # nao conseguiu detectar


def esperar_popup_sim(timeout=15):
    """Aguarda o popup 'Sim' aparecer apos clicar Excluir."""
    inicio = time.time()

    detectado = _achar_botao_sim()
    if detectado is True:
        time.sleep(0.3)
        return True

    try:
        while time.time() - inicio < timeout:
            aguardar_se_pausado()
            if _achar_botao_sim() is True:
                time.sleep(0.3)
                return True
            time.sleep(0.5)
    except Exception:
        pass

    try:
        time.sleep(0.5)
        cor_fundo = pyautogui.pixel(665, 424)
        while time.time() - inicio < timeout:
            aguardar_se_pausado()
            time.sleep(0.5)
            if pyautogui.pixel(665, 424) != cor_fundo:
                time.sleep(0.3)
                return True
    except Exception:
        pass

    time.sleep(2)
    return True


def esperar_exclusao(timeout=40):
    """Aguarda o popup de confirmacao fechar."""
    inicio = time.time()

    detectado = _achar_botao_sim()
    if detectado is False:
        time.sleep(0.3)
        return True
    if detectado is None:
        pass

    try:
        while time.time() - inicio < timeout:
            aguardar_se_pausado()
            if _achar_botao_sim() is False:
                time.sleep(0.3)
                return True
            time.sleep(0.5)
    except Exception:
        pass

    try:
        time.sleep(0.5)
        cor_sim = pyautogui.pixel(665, 424)
        while time.time() - inicio < timeout:
            aguardar_se_pausado()
            time.sleep(0.5)
            if pyautogui.pixel(665, 424) != cor_sim:
                time.sleep(0.3)
                return True
    except Exception:
        pass

    print("  (aguardando processamento 5s...)")
    time.sleep(5)
    return True


def processar_codigo(codigo, idx, total):
    p(f"\n[{idx}/{total}] Codigo {codigo}")

    aguardar_se_pausado()

    p("  - Digitando codigo... ", end="")
    digitar_texto(str(codigo), 343, 147)
    p("OK")

    p("  - Clicando Procurar... ", end="")
    clicar(433, 142)
    p("OK")

    p("  - Aguardando carregamento... ", end="")
    esperar_carregamento()
    p("OK")

    p("  - Clicando Excluir... ", end="")
    clicar(1231, 148)
    p("OK")

    p("  - Aguardando popup Sim... ", end="")
    esperar_popup_sim()
    p("OK")

    p("  - Confirmando Sim... ", end="")
    clicar(665, 424)
    p("OK")

    p("  - Aguardando exclusao... ", end="")
    esperar_exclusao()
    p("OK")

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

    focar_mega(raiz)

    print("Iniciando em 5 segundos... Mova o mouse para o MEGA ERP.")
    for s in range(5, 0, -1):
        print(f"  {s}...")
        time.sleep(1)

    # limpa log de progresso e esconde console
    with open(LOG_PROGRESSO_TEMP, "w", encoding="utf-8") as f:
        f.write(f"Progresso: {inicio} ate {fim} ({total} codigos)\n\n")
    time.sleep(0.3)
    focar_mega(raiz)
    time.sleep(0.3)
    _esconder_console()
    time.sleep(0.3)
    focar_mega(raiz)

    sucessos = 0
    falhas = 0
    tempo_inicio = time.time()

    try:
        for i, codigo in enumerate(range(inicio, fim + 1), 1):
            aguardar_se_pausado()
            focar_mega(raiz)

            ok = processar_codigo(codigo, i, total)
            if ok:
                sucessos += 1
            else:
                falhas += 1

    except KeyboardInterrupt:
        p("[!] Interrompido pelo usuario.")
    finally:
        _mostrar_console()
        time.sleep(0.5)
        decorrido = int(time.time() - tempo_inicio)
        print()
        print("=" * 55)
        print("  RESUMO FINAL")
        print("=" * 55)
        print(f"  Total processados: {total}")
        print(f"  Sucessos:          {sucessos}")
        print(f"  Falhas:            {falhas}")
        print(f"  Tempo total:       {decorrido // 60}m {decorrido % 60}s")
        print(f"  Log de progresso:  {LOG_PROGRESSO_TEMP}")
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
        print(f"Log salvo em: {LOG_ERRO}")
        sys.exit(1)
    except Exception as e:
        erro = traceback.format_exc()
        msg = f"Erro inesperado\n{e}\n\n{erro}"
        log_erro(msg)
        print(f"\nErro inesperado: {e}")
        print(f"Log salvo em: {LOG_ERRO}")
        sys.exit(1)
