import argparse
import os
from glob import glob
import requests
import openai
import json

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

def ask_ai_to_process_tasks(tasklist_content, rag_rules, mcp_json_list):
    """
    Request AI
    """
    prompt = f"""
RAG rules:
{'\n'.join(rag_rules)}

MCP metadata:
"""
    for mcp in mcp_json_list:
        prompt += f"\nService: {mcp.get('serviceName')}, endpoints:\n"
        for ep in mcp.get("endpoints", []):
            prompt += f"  {ep['method']} {ep['path']} - {ep['description']}\n"

    prompt += f"\n{tasklist_content}\n\n"

    # response = openai.ChatCompletion.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "Sa oled AI agent, kes täidab taskliste MCP teenuste abil."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0
    # )
    # return response.choices[0].message.content
    return prompt


def execute_ai_tasks(ai_output, mcp_servers):
    try:
        tasks = json.loads(ai_output)
    except json.JSONDecodeError:
        print("AI output ei ole korrektne JSON.")
        print(ai_output)
        return

    for task in tasks:
        service_name = task.get("serviceName")
        endpoint_template = task.get("endpoint")
        method = task.get("method", "POST").upper()
        data = task.get("data", {})

        server_url = None
        for mcp in mcp_servers:
            if mcp.get("serviceName") == service_name:
                server_url = mcp.get("_url", None)
                break

        if not server_url:
            print(f"Server for {service_name} not found. Skipping task: {task}")
            continue

        if "{person_id}" in endpoint_template:
            person_id = len(data.get("firstName", "")) + len(data.get("lastName", ""))  # lihtne dummy ID
            endpoint = endpoint_template.replace("{person_id}", str(person_id))
        else:
            endpoint = endpoint_template

        url = f"{server_url}{endpoint}"

        try:
            if method == "POST":
                resp = requests.post(url, json=data)
            elif method == "GET":
                resp = requests.get(url, params=data)
            else:
                print(f"Method {method} not supported. Skipping.")
                continue

            if resp.status_code in (200, 201):
                print(f"[SUCCESS] {method} {url} -> {resp.json()}")
            else:
                print(f"[FAIL] {method} {url} -> {resp.status_code}: {resp.text}")

        except requests.RequestException as e:
            print(f"[ERROR] {method} {url} -> {e}")



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

    openai.api_key = os.getenv("OPENAI_API_KEY")
    ai_output = ask_ai_to_process_tasks(tasklist_content, rag_rules, all_mcp)

    print("\nAI Model Output:")
    print(ai_output)

    execute_ai_tasks(ai_output, all_mcp)

if __name__ == "__main__":
    main()
