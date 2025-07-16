"""Command line interface to interact with ChatGPT via a browser.

This script starts Chrome in incognito mode so that no browsing data
or credentials are persisted. It prints responses to the terminal only
and stores no conversation history.

Licensed under the Apache License, Version 2.0. See the LICENSE file
for details.
"""

import argparse
import os
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.console import Console
from rich.text import Text

console = Console()


def get_args():
    """Return parsed command-line arguments."""
    parser = argparse.ArgumentParser(description="Interact with ChatGPT from the terminal")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome in headless mode"
    )
    parser.add_argument(
        "--save-file",
        type=str,
        help="Optional path to save the conversation"
    )
    return parser.parse_args()


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

def main():
    args = get_args()
    driver = iniciar_navegador(args.headless)
    history = []

    print("[INFO] Si ves login o captcha, resuélvelo en el navegador.")
    input("[MANUAL] Pulsa ENTER cuando puedas escribir en el prompt...\n")

    try:
        while True:
            pregunta = input(">> Pregunta ('salir' o 'historia'): ").strip()

            if pregunta.lower() == "salir":
                break

            if pregunta.lower() == "historia":
                for i, (q, r) in enumerate(history, 1):
                    console.print(f"{i}. Q: {q}\n   A: {r}\n")
                continue

            start = time.time()
            respuesta = enviar_pregunta(driver, pregunta)
            dur = time.time() - start

            print("\n--- CMD response ---\n")
            imprimir_respuesta(respuesta)
            print(f"\n[INFO] Tiempo de respuesta: {dur:.1f}s\n----XXXX----\n")

            history.append((pregunta, respuesta))

            if args.save_file:
                with open(args.save_file, "a", encoding="utf-8") as f:
                    f.write(f"Q: {pregunta}\nA: {respuesta}\n\n")
    except KeyboardInterrupt:
        print("\n[INFO] Sesión interrumpida por el usuario.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
