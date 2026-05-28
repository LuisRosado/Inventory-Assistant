import argparse
import subprocess
import sys

DEFAULT_MODEL = "llama-3.2-3b-it:latest"

SYSTEM_PROMPT = (
    "Eres un asistente virtual amable y útil. "
    "Responde en español a las preguntas del usuario. "
    "Si el usuario pide ejemplos o información, dale respuestas claras y breves."
)


def run_model(model: str, prompt: str) -> str:
    args = ["ollama", "run", model, prompt]
    process = subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output, error = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(
            f"Ocurrió un error al ejecutar ollama: {error.strip() or 'sin salida de error'}"
        )
    return output.strip()


def build_prompt(history: list[str]) -> str:
    lines = ["Sistema: " + SYSTEM_PROMPT]
    for role, message in history:
        prefix = "Usuario: " if role == "user" else "Asistente: "
        lines.append(prefix + message)
    lines.append("Asistente: ")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chatbot local usando Ollama y un modelo instalado."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Modelo Ollama a usar (por defecto: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    print("Chatbot con Ollama")
    print(f"Modelo seleccionado: {args.model}")
    print("Escribe tu mensaje y presiona Enter. Deja la entrada vacía para salir.")

    history: list[tuple[str, str]] = []
    while True:
        try:
            user_input = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAdiós.")
            break
        if not user_input:
            print("Saliendo...")
            break

        history.append(("user", user_input))
        prompt = build_prompt(history)

        try:
            response = run_model(args.model, prompt)
        except RuntimeError as exc:
            print(f"Error: {exc}")
            sys.exit(1)

        response = response.strip()
        history.append(("assistant", response))
        print(f"Bot: {response}\n")


if __name__ == "__main__":
    main()
