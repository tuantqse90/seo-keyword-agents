import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schedule import Schedule
from app.models.report import ReportModule

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


class ScheduleCreate(BaseModel):
    module: ReportModule
    query: str
    interval_hours: int = 168  # weekly
    project_id: uuid.UUID | None = None


class ScheduleOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID | None
    module: ReportModule
    query: str
    interval_hours: int
    is_active: bool
    last_run_at: datetime | None
    next_run_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ScheduleUpdate(BaseModel):
    interval_hours: int | None = None
    is_active: bool | None = None
    query: str | None = None


@router.get("", response_model=list[ScheduleOut])
async def list_schedules(db: AsyncSession = Depends(get_db)):
    stmt = select(Schedule).order_by(Schedule.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=ScheduleOut, status_code=201)
async def create_schedule(data: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    schedule = Schedule(
        module=data.module,
        query=data.query,
        interval_hours=data.interval_hours,
        project_id=data.project_id,
        next_run_at=datetime.utcnow() + timedelta(hours=data.interval_hours),
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(schedule_id: uuid.UUID, data: ScheduleUpdate, db: AsyncSession = Depends(get_db)):
    schedule = await db.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    if data.interval_hours is not None:
        schedule.interval_hours = data.interval_hours
        schedule.next_run_at = datetime.utcnow() + timedelta(hours=data.interval_hours)
    if data.is_active is not None:
        schedule.is_active = data.is_active
    if data.query is not None:
        schedule.query = data.query
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(schedule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    schedule = await db.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    await db.delete(schedule)
    await db.commit()
