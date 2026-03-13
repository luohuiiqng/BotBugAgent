from fastapi import FastAPI, Request
import json
import os
import requests

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@app.get("/health")
async def health():
    return {"status": "ok"}

def fetch_pr_files(repo_full_name: str, pr_number: int):
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

@app.post("/webhook/github")
async def github_webhook(request: Request):
    event = request.headers.get("X-GitHub-Event")
    body = await request.body()
    payload = json.loads(body.decode("utf-8"))

    if event == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        number = pr.get("number")
        title = pr.get("title")
        head_sha = pr.get("head", {}).get("sha")
        repo = payload.get("repository", {})
        full_name = repo.get("full_name")

        print(f"[Webhook] PR #{number} {action}: {title} ({head_sha}) in {full_name}")

        if full_name:
            files = fetch_pr_files(full_name, number)
            for f in files:
                filename = f["filename"]
                patch = f.get("patch", "")
                print(f"\n=== File: {filename} ===")
                print(patch[:1000])  # 只打印前 1000 字符
    else:
        print(f"[Webhook] Ignore event: {event}")

    return {"ok": True}