from flask import Flask, render_template, request, session, jsonify
import subprocess
import os
import csv

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-key")

DEFAULT_MODEL = "llama-3.2-3b-it:latest"

SYSTEM_PROMPT = (
    "Eres un asistente virtual amable y útil. "
    "Responde en español a las preguntas del usuario. "
    "Si el usuario pide ejemplos o información, dale respuestas claras y breves."
)

DATASET_FILE = "inventory.csv"


def load_dataset_csv(path: str) -> str:
    rows = []
    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rows.append(','.join(row))
    except FileNotFoundError:
        return ""
    return '\n'.join(rows)


def build_dataset_prompt(dataset_text: str) -> str:
    if not dataset_text:
        return ""
    return (
        "A continuación se proporciona un dataset de inventario en formato CSV. "
        "Contesta solo usando la información que aparece en este dataset. "
        "Si la pregunta no puede responderse con los datos disponibles, responde "
        "con 'No tengo suficiente información en el dataset.'\n\n"
        f"{dataset_text}\n\n"
    )

DATASET_TEXT = build_dataset_prompt(load_dataset_csv(DATASET_FILE))


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


def build_prompt(history: list[dict]) -> str:
    lines = ["Sistema: " + SYSTEM_PROMPT]
    if DATASET_TEXT:
        lines.append(DATASET_TEXT)
    for item in history:
        role = item.get("role")
        message = item.get("message")
        prefix = "Usuario: " if role == "user" else "Asistente: "
        lines.append(prefix + message)
    lines.append("Asistente: ")
    return "\n".join(lines)


# Force using the Llama 3 model explicitly
# Ensure this matches a model you have pulled into Ollama
BEST_MODEL: str = DEFAULT_MODEL


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/models")
def api_models():
    # Return the automatically chosen best model (string)
    return jsonify({"best": BEST_MODEL})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    # Use the preselected best model on the server side
    model = BEST_MODEL
    if not message:
        return jsonify({"error": "Mensaje vacío"}), 400

    history = session.get("history", [])
    history.append({"role": "user", "message": message})
    prompt = build_prompt(history)

    try:
        reply = run_model(model, prompt)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500

    history.append({"role": "assistant", "message": reply})
    session["history"] = history
    return jsonify({"reply": reply})


@app.route("/api/reset", methods=["POST"]) 
def api_reset():
    session["history"] = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
