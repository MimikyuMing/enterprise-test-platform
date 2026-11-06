from datetime import datetime

from pydantic import BaseModel, Field


class ExecutionCreate(BaseModel):
    total_cases: int = Field(default=1, ge=1, deprecated="要执行的用例总数")


class ExecutionResponse(BaseModel):
    id: int
    status: str
    total_cases: int
    passed: int
    failed: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = {"from_attributes": True}\


class CaseResultResponse(BaseModel):
    id: int
    nodeid: str
    outcome: str
    duration: float
    message: str | None

    model_config = {"from_attributes": True}


class CaseResultListResponse(BaseModel):
    execution_id: int
    total: int
    items: list[CaseResultResponse]