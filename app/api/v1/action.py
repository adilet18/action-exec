import requests
from kubernetes import client, config
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from app.agents.action_executor import ActionExecutorAgent


router = APIRouter()

class ActionRequest(BaseModel):
    type: str
    parameters: dict[str, Any]
    simulate: bool = True
 

@router.post("/action/execute")
def execute_action(request: ActionRequest):
    agent = ActionExecutorAgent(simulation_mode=request.simulate)
    alert = dict(request.parameters)
    alert["type"] = request.type
    result = agent.execute(alert)
    return {"result": result}

@router.get("/")
def root():
    return {"message": "SRE Agent API is running"}


# example of json
# #   {
# #     "type": "restart",
# #     "parameters": {"pod_name": "my-app-123", "namespace": "default"},
# #     "simulate": true
# #   }

