import argparse
import os
from glob import glob
import requests

def load_rag_rules(paths):
    """
    Load RAG rules
    """
    rules = []
    for path in paths:
        if not os.path.isdir(path):
            print(f"Warning: {path} is not folder. Skipped.")
            continue

        files = glob(os.path.join(path, "*.sexp")) + glob(os.path.join(path, "*.lisp"))
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                rules.append(content)
    return rules

def load_mcp(url: str):
    """
    Load MCP JSON from API.
    """
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        mcp_json = resp.json()
        print(f"MCP JSON loaded: service={mcp_json.get('serviceName')}")
        return mcp_json
    except requests.RequestException as e:
        print(f"MCP request fail: {e}")
        return None


def load_tasklist(file_path):
    if not os.path.isfile(file_path):
        print(f"Tasklist faili ei leitud: {file_path}")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def load_tasklists(file_paths):
    """
    Load one or multiple tasklist files and combine into a single string.
    """
    all_tasks = []
    for path in file_paths:
        if not os.path.isfile(path):
            print(f"Tasklist faili ei leitud: {path}. Skipped.")
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                all_tasks.append(content)
    if not all_tasks:
        return None
    return "\n\n".join(all_tasks)


def main():
    parser = argparse.ArgumentParser(description="CLI AI Agent")
    parser.add_argument(
        "--rag",
        "-r",
        nargs="+",
        required=True,
        help="Path(s) to RAG rule directories"
    )
    parser.add_argument(
        "--mcp",
        "-m",
        nargs="+",
        required=True,
        help="URL(s) to MCP endpoint(s) (FastAPI)"
    )
    parser.add_argument(
        "--tasklist",
        "-t",
        nargs="+",  # lubab mitu faili
        required=True,
        help="Path(s) to tasklist file(s) (txt or md) to process"
    )

    args = parser.parse_args()

    rag_rules = load_rag_rules(args.rag)

    print(f"Loaded {len(rag_rules)} RAG file:")
    for i, rule in enumerate(rag_rules, start=1):
        print(f"\n--- File {i} ---")
        print(rule)
        print("--------------")

    all_mcp = []
    for url in args.mcp:
        mcp_json = load_mcp(url)
        if mcp_json:
            all_mcp.append(mcp_json)

    print("\nMCP endpoints:")
    for i, mcp in enumerate(all_mcp, start=1):
        print(f"\n--- MCP Server {i}: {mcp.get('serviceName')} ---")
        for ep in mcp.get("endpoints", []):
            print(f"  {ep['method']} {ep['path']} - {ep['description']}")

    tasklist_content = load_tasklists(args.tasklist)
    if not tasklist_content:
        print("Tasklist file cant be read.")
        return

    print("\nCombined Tasklist content:")
    print(tasklist_content)

if __name__ == "__main__":
    main()
