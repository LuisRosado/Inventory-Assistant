# Chatbot Ollama

Bot sencillo en Python que usa un modelo instalado de Ollama.

## Archivos

- `app.py`: script de chat por consola.

## Uso

1. Abre una terminal en la carpeta del proyecto.
2. Ejecuta:

```powershell
python .\app.py
```

3. Escribe tus preguntas y presiona Enter.
4. Deja la entrada vacía para salir.

## Dataset

El chatbot usa `inventory.csv` como dataset de inventario y puede responder preguntas sobre productos, stock, precios, proveedores y almacenes.

## Modelo predeterminado

El script usa por defecto `llama-3.2-3b-it:latest`.
Puedes cambiarlo con:

```powershell
python .\app.py --model qwen-2.5.1-coder-it:latest
```

## Requisitos

- `ollama` instalado y accesible en la terminal.
- Modelo descargado en Ollama (por ejemplo `llama-3.2-3b-it:latest`).
