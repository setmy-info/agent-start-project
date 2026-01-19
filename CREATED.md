# Project Starting Point

This file documents the initial setup steps for the project.

## Step-by-Step Installation

1. **Create a virtual environment:**
```shell
python3 -m venv .venv
```

2. **Activate the virtual environment:**
```shell
source .venv/bin/activate
```

3. **Check Python version:**
```shell
python --version
# Expected output: Python 3.13.7
```

4. **Create the necessary directories:**
```shell
mkdir api agent
```

5. **Upgrade pip:**
```shell
python -m pip install --upgrade pip
```

6. **Install required libraries:**
```shell
pip install fastapi uvicorn openai
```

*Or use the requirements.txt file:*

```shell
pip install -r requirements.txt
```

7. **RAG data folder created**

```shell
mkdir rag
```
