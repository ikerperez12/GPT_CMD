"""Command line interface to interact with ChatGPT via a browser.

This script starts Chrome in incognito mode so that no browsing data
or credentials are persisted. It prints responses to the terminal only
and stores no conversation history.

Licensed under the Apache License, Version 2.0. See the LICENSE file
for details.
"""

import os
import time
from typing import Optional

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.console import Console
from rich.text import Text
import pyperclip

console = Console()


def iniciar_navegador(headless: bool = False):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    if headless:
        options.add_argument("--headless=new")
    driver = uc.Chrome(options=options, use_subprocess=True)
    driver.get("https://chatgpt.com")
    return driver


def configurar() -> tuple[bool, Optional[str]]:
    """Interactively ask the user how to start the session."""
    head = input("¿Ejecutar en modo headless? (s/N): ").strip().lower() == "s"
    save_file: Optional[str] = None
    if input("¿Guardar la conversación en un archivo? (s/N): ").strip().lower() == "s":
        save_file = input("Ruta del archivo: ").strip() or None
    return head, save_file

def enviar_pregunta(driver, pregunta):
    try:
        wait = WebDriverWait(driver, 60)
        caja = wait.until(EC.element_to_be_clickable((By.ID, "prompt-textarea")))
        caja.click()
        caja.send_keys(pregunta)
        caja.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.markdown")))
        time.sleep(2)

        respuestas = driver.find_elements(By.CSS_SELECTOR, "div.markdown")
        return respuestas[-1].text.strip() if respuestas else "[Sin respuesta]"
    except Exception as e:
        return f"[ERROR] {e}"

def imprimir_respuesta(texto: str) -> None:
    """Pretty print a response using rich."""
    rich_text = Text(texto)
    console.print(rich_text)

def mostrar_historia(history):
    for i, (q, r) in enumerate(history, 1):
        console.print(f"{i}. Q: {q}\n   A: {r}\n")


def main():
    headless, save_file = configurar()
    driver = iniciar_navegador(headless)
    history: list[tuple[str, str]] = []

    print("[INFO] Si ves login o captcha, resuélvelo en el navegador.")
    input("[MANUAL] Pulsa ENTER cuando puedas escribir en el prompt...\n")

    try:
        while True:
            print("\nMenú:\n1. Preguntar\n2. Ver historia\n3. Borrar historia\n4. Copiar última respuesta\n5. Salir")
            opcion = input("Selecciona opción: ").strip()

            if opcion == "5":
                break
            elif opcion == "2":
                mostrar_historia(history)
                continue
            elif opcion == "3":
                history.clear()
                if save_file:
                    open(save_file, "w").close()
                print("[INFO] Historia borrada.")
                continue
            elif opcion == "4":
                if history:
                    pyperclip.copy(history[-1][1])
                    print("[INFO] Última respuesta copiada al portapapeles.")
                else:
                    print("[WARN] No hay respuestas para copiar.")
                continue
            elif opcion != "1":
                print("[WARN] Opción no reconocida.")
                continue

            pregunta = input("Escribe tu pregunta: ").strip()
            if not pregunta:
                continue

            start = time.time()
            respuesta = enviar_pregunta(driver, pregunta)
            dur = time.time() - start

            print("\n--- CMD response ---\n")
            imprimir_respuesta(respuesta)
            print(f"\n[INFO] Tiempo de respuesta: {dur:.1f}s\n----XXXX----\n")

            history.append((pregunta, respuesta))

            if save_file:
                with open(save_file, "a", encoding="utf-8") as f:
                    f.write(f"Q: {pregunta}\nA: {respuesta}\n\n")
    except KeyboardInterrupt:
        print("\n[INFO] Sesión interrumpida por el usuario.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
