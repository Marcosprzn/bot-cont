import time
import sys
from pywinauto import Desktop, Application, ElementNotFoundError
from pywinauto.findwindows import find_elements


def listar_janelas():
    print("\n--- Janelas abertas ---")
    elems = find_elements(control_type="Window", backend="uia")
    for e in elems:
        nome = e.name if e.name else ""
        if nome.strip():
            print(f"  - '{nome}' (handle: {e.handle})")
    print("------------------------\n")


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
        listar_janelas()
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
        print(f"\nErro: Campo nao encontrado - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        sys.exit(1)
