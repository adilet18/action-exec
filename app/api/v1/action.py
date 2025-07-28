import requests
from kubernetes import client, config
import subprocess
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any
from app.agents.action_executor import ActionExecutorAgent
import re
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)

class ExecCommand(BaseModel):
    command: str

# Same dangerous pattern list
DANGEROUS_PATTERNS = [
    r"\bdelete\b",
    r"\bremove\b",
    r"\buninstall\b",
    r"\breset\b",
    r"\bpurge\b",
    r"--all\b",
    r"\bdrop\b",
    r"\brollback\b",
    r"\b--purge\b",
    r"\bformat\b"
]

def is_dangerous_command(command: str) -> bool:
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False

@router.post("/exec")
async def exec_command(cmd: ExecCommand, approve: bool = Query(default=False)):
    full_cmd = cmd.command.strip()

    if not full_cmd.startswith("kubectl ") and not full_cmd.startswith("helm "):
        raise HTTPException(status_code=400, detail="Only 'kubectl' and 'helm' commands are allowed.")

    if is_dangerous_command(full_cmd):
        if not approve:
            raise HTTPException(
                status_code=403,
                detail={
                    "warning": "⚠️ This command is considered dangerous and requires manual approval.",
                    "hint": "Resend the request with `?approve=true` query parameter to proceed."
                }
            )
        logging.warning(f"⚠️ Approved dangerous command executed: {full_cmd}")

    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "executed_command": full_cmd,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
            "warning": "⚠️ This was a dangerous command. Proceed with caution." if is_dangerous_command(full_cmd) else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def root():
    return {"message": "SRE Agent API is running"}
