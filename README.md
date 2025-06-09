# Oracle DB with LLM on Compute

## Local deployment

```bash
cd container
```

```bash
podman build -t ollama .
```

```bash
cd ..
```

```bash
podman run -d \
    --rm --name ollama \
    -v ollama-data:/home/ollama/.ollama \
    -p 11434:11434 \
    localhost/ollama
```

```bash
podman exec ollama ollama run llama3.2:3b
```

```bash
curl http://localhost:11434/
```

```bash
curl http://localhost:11434/api/generate -d '{"model":"llama3.2:3b","prompt":"Hello"}'
```

## Client

```bash
python -m venv venv
```

```bash
source ./venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python client.py
```
