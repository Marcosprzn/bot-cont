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
LOG_PROGRESSO = os.path.join(LOG_DIR, "progresso.tmp")

pausado = False
console_oculto = False

# --- CONFIGURACOES DAS AUTOMACOES ---
MODOS = {
    1: {
        "nome": "Primaria",
        "passos": [
            ("campo",    343,  147, "codigo"),
            ("procurar", 433,  142, "Procurar"),
            ("excluir",  1231, 148, "Excluir"),
            ("sim",      665,  424, "Sim"),
        ],
        "esperas": ["procurar", "popup", "exclusao"],
        "tempos_iniciais": {"procurar": 2.5, "popup": 1.5, "exclusao": 4.0},
        "pisos":           {"procurar": 0.5, "popup": 0.3, "exclusao": 1.0},
    },
    2: {
        "nome": "Secundaria",
        "passos": [
            ("campo",     343,  147, "codigo"),
            ("procurar",  409,  147, "Procurar"),
            ("aplicar",   815,  627, "Aplicar"),
            ("selecionar",1034, 587, "Selecionar"),
            ("excluir",   1248, 144, "Excluir"),
            ("sim",       771,  420, "Sim"),
        ],
        "esperas": ["procurar", "popup", "exclusao"],
        "tempos_iniciais": {"procurar": 2.5, "popup": 2.0, "exclusao": 4.0},
        "pisos":           {"procurar": 0.5, "popup": 0.3, "exclusao": 1.0},
    },
}

MODO = 1         # modo ativo
HIST = {}        # historico de tempos do modo ativo
FLOOR = {}       # pisos do modo ativo
PRIMEIRO = True
INICIO_CODIGO = 0.0


def media(arr):
    return sum(arr) / len(arr)


def configurar_modo(modo):
    """Inicializa historico e pisos para o modo escolhido."""
    global MODO, HIST, FLOOR, PRIMEIRO
    cfg = MODOS[modo]
    MODO = modo
    HIST = {k: [v] for k, v in cfg["tempos_iniciais"].items()}
    FLOOR = cfg["pisos"].copy()
    PRIMEIRO = True


def esperar(etapa):
    arr = HIST[etapa]
    t = max(FLOOR[etapa], media(arr))
    time.sleep(t)
    return t


def registrar_etapa(etapa, t_gasto):
    arr = HIST[etapa]
    arr.append(t_gasto)
    if len(arr) > 5:
        arr.pop(0)


def recalcular_apos_primeiro():
    global HIST
    cfg = MODOS[MODO]
    total = time.time() - INICIO_CODIGO
    n = len(cfg["esperas"])
    parte = max(0.5, total / n)
    for k in cfg["esperas"]:
        HIST[k] = [parte, parte * 0.9]


def reduzir_tempos():
    for k in HIST:
        arr = HIST[k]
        novo = [max(FLOOR[k], v * 0.97) for v in arr]
        HIST[k] = novo


def passo_exige_espera(passo):
    """Retorna a chave de espera se o passo exige, ou None."""
    if passo[0] == "procurar":  return "procurar"
    if passo[0] == "excluir":   return "popup"
    if passo[0] == "sim":       return "exclusao"
    return None


# --- FIM CONFIG ---


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
        with open(LOG_PROGRESSO, "a", encoding="utf-8") as f:
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
    pyautogui.doubleClick(x, y)
    time.sleep(0.15)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("backspace")
    time.sleep(0.05)
    pyautogui.write(texto, interval=0.02)
    return True


def clicar(x, y):
    aguardar_se_pausado()
    pyautogui.click(x, y)
    return True


def processar_codigo(codigo, idx, total):
    global PRIMEIRO, INICIO_CODIGO

    INICIO_CODIGO = time.time()
    cfg = MODOS[MODO]
    passos = cfg["passos"]
    n = len(passos)

    p(f"\n[{idx}/{total}] Codigo {codigo}")

    aguardar_se_pausado()

    for i, passo in enumerate(passos, 1):
        tipo, x, y, nome = passo
        aguardar_se_pausado()

        if tipo == "campo":
            p(f"  {i}/{n} {nome}... ", end="")
            digitar_texto(str(codigo), x, y)
            p("OK")
        else:
            chave_espera = passo_exige_espera(passo)
            if chave_espera:
                p(f"  {i}/{n} {nome}... ", end="")
            else:
                p(f"  {i}/{n} {nome}... ", end="")

            clicar(x, y)

            if chave_espera:
                t = esperar(chave_espera)
                registrar_etapa(chave_espera, time.time() - INICIO_CODIGO)
                p(f"({t:.1f}s) OK")
            else:
                p("OK")

    # --- AJUSTES POS-CODIGO ---
    if PRIMEIRO:
        recalcular_apos_primeiro()
        PRIMEIRO = False
        p(f"  >> Calibrado! Proximos serao mais rapidos.")
    else:
        reduzir_tempos()

    return True


def main():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05

    print("=" * 55)
    print("  BOT MEGA ERP - Exclusao em Lote")
    print("  (Adaptativo: fica mais rapido a cada codigo)")
    print("=" * 55)
    print("  F8 = Pausar / Continuar")
    print("  Ctrl+C = Parar")
    print("=" * 55)
    print()

    print("Selecione o modo:")
    for k, v in MODOS.items():
        print(f"  {k} - Automacao {v['nome']}")
    try:
        escolha = int(input("Modo (1 ou 2): ").strip())
        if escolha not in MODOS:
            print("Modo invalido. Usando modo 1.")
            escolha = 1
    except ValueError:
        print("Entrada invalida. Usando modo 1.")
        escolha = 1

    configurar_modo(escolha)
    cfg = MODOS[escolha]

    try:
        inicio = int(input("Digite o CODIGO INICIAL: ").strip())
        fim = int(input("Digite o CODIGO FINAL:   ").strip())
    except ValueError:
        print("Codigo invalido. Digite apenas numeros.")
        sys.exit(1)

    if inicio > fim:
        inicio, fim = fim, inicio

    total = fim - inicio + 1
    print(f"\nModo: {cfg['nome']} | {total} codigos: {inicio} ate {fim}")
    print("Conectando ao MEGA ERP...")

    raiz, app = encontrar_janela_raiz()
    iniciar_listener_f8()
    focar_mega(raiz)

    print("Iniciando em 5 segundos... Mova o mouse para o MEGA ERP.")
    for s in range(5, 0, -1):
        print(f"  {s}...")
        time.sleep(1)

    with open(LOG_PROGRESSO, "w", encoding="utf-8") as f:
        f.write(f"Modo: {cfg['nome']} | {inicio} ate {fim} ({total} codigos)\n\n")
    time.sleep(0.3)
    focar_mega(raiz)
    time.sleep(0.3)
    _esconder_console()
    time.sleep(0.3)
    focar_mega(raiz)

    sucessos = 0
    falhas = 0
    tempo_geral = time.time()

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
        decorrido = int(time.time() - tempo_geral)
        print()
        print("=" * 55)
        print("  RESUMO FINAL")
        print("=" * 55)
        print(f"  Total processados: {total}")
        print(f"  Sucessos:          {sucessos}")
        print(f"  Falhas:            {falhas}")
        print(f"  Tempo total:       {decorrido // 60}m {decorrido % 60}s")
        if sucessos > 0:
            print(f"  Media por codigo:  {decorrido / sucessos:.1f}s")
        print(f"  Log de progresso:  {LOG_PROGRESSO}")
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
