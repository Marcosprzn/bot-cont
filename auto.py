import time
import sys
from pywinauto import Desktop, ElementNotFoundError


def main():
    print("Aguardando 5 segundos...")
    time.sleep(5)

    desktop = Desktop(backend="uia")

    print("Procurando campo AutomationId '66786'...")
    campo = desktop.child_window(
        automation_id="66786",
        control_type="Edit"
    ).wait("visible", timeout=10)

    campo.set_focus()
    campo.select()
    campo.type_keys("100283", with_spaces=False)
    print("Codigo '100283' inserido com sucesso!")


if __name__ == "__main__":
    try:
        main()
    except ElementNotFoundError as e:
        print(f"Erro: Campo nao encontrado - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)
