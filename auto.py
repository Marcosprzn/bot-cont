import os
import time
import sys
import traceback
from datetime import datetime

import pyautogui
import keyboard
from pywinauto import Application, ElementNotFoundError
from pywinauto.findwindows import find_elements

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "erro_auto.txt")

pausado = False


def alternar_pausa():
    global pausado
    pausado = not pausado
    status = "PAUSADO" if pausado else "CONTINUANDO"
    print(f"\n  [{status}] F8 para alternar\n")


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


def esperar_exclusao(timeout=40):
    """Aguarda o popup de confirmacao fechar. Tenta 3 metodos em cascata."""
    inicio = time.time()

    # --- METODO 1: UIA (detectar botao 'Sim' pelo nome) ---
    try:
        while time.time() - inicio < timeout:
            aguardar_se_pausado()
            botoes = find_elements(control_type="Button", backend="uia")
            sim = [b for b in botoes if b.name and "Sim" in b.name]
            if not sim:
                time.sleep(0.3)
                return True
            time.sleep(0.5)
        return True
    except Exception:
        pass

    # --- METODO 2: pixel do botao Sim ---
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

    # --- METODO 3: espera fixa ---
    print("  (aguardando processamento 5s...)")
    time.sleep(5)
    return True


def processar_codigo(codigo, idx, total):
    print(f"\n[{idx}/{total}] Codigo {codigo}")
    sys.stdout.flush()

    aguardar_se_pausado()

    print("  - Digitando codigo...", end=" ")
    digitar_texto(str(codigo), 343, 147)
    print("OK")
    time.sleep(0.2)

    print("  - Clicando Excluir...", end=" ")
    clicar(1231, 148)
    print("OK")
    time.sleep(0.3)

    print("  - Confirmando Sim...", end=" ")
    clicar(665, 424)
    print("OK")

    print("  - Aguardando exclusao...", end=" ")
    esperar_exclusao()
    print("OK")

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
        print("\n\n[!] Interrompido pelo usuario.")
    finally:
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
