from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
from typing import List, Optional

app = FastAPI()

class RowboatCall(BaseModel):
    user_id: str
    provider_id: str = "openai"
    flavor: str = "openai"
    api_key: str
    model: str = "gpt-5.1"
    base_url: Optional[str] = ""
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    rowboat_args: List[str] = []
    agent: str = ""            # ex: "web_scraper_agent" ou "copilot"
    run_id: Optional[str] = None


@app.post("/call")
def call_rowboat(payload: RowboatCall):
    cmd = [
        "rowboatx-multi",
        payload.user_id,
        "--provider-id", payload.provider_id,
        "--flavor", payload.flavor,
        "--api-key", payload.api_key,
        "--model", payload.model,
    ]

    if payload.base_url:
        cmd += ["--base-url", payload.base_url]
    if payload.default_provider:
        cmd += ["--default-provider", payload.default_provider]
    if payload.default_model:
        cmd += ["--default-model", payload.default_model]

    if payload.run_id:
        cmd += ["--run_id", payload.run_id]

    # 🔥 Construire les arguments CLI pour rowboatx
    cli_args = list(payload.rowboat_args or [])

    # 1) Injecter --agent si présent dans le payload et pas déjà dans les args
    if payload.agent:
        has_agent = any(
            a == "--agent" or a.startswith("--agent=")
            for a in cli_args
        )
        if not has_agent:
            # syntaxe style --agent=name (compatible avec doc README)
            cli_args.insert(0, f"--agent={payload.agent}")

    # 2) Forcer --no-interactive=true si pas déjà demandé
    has_no_interactive = any(
        a.startswith("--no-interactive") for a in cli_args
    )
    if not has_no_interactive:
        cli_args.append("--no-interactive=true")

    if cli_args:
        cmd.append("--")
        cmd.extend(cli_args)

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "cmd": cmd,
    }
