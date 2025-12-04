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
    rowboat_args: List[str] = []  # ex: ["init"] ou ["run", "--workflow", "..."]


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

    if payload.rowboat_args:
        cmd.append("--")
        cmd.extend(payload.rowboat_args)

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
