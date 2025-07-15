from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any

from ..schedule import Schedule, ScheduleCreate, list_schedules, create_schedule, update_schedule, delete_schedule

# Router definition
router = APIRouter(
    prefix="/schedule",
    tags=["schedule"],
    responses={404: {"description": "Not found"}}
)

@router.get("/list", response_model=List[Schedule])
async def get_schedules() -> List[Schedule]:
    """
    List all agent schedules.
    :return: A list of schedules.
    """
    return list_schedules()

@router.post("/create", response_model=Schedule)
async def create_schedule_endpoint(request: Request) -> Schedule:
    """
    Create a new agent schedule.
    :param request: The request containing the schedule data.
    :return: The created schedule.
    """
    try:
        data = await request.json()
        agent_id = data.get("agentId")
        cron_expression = data.get("cronExpression")
        user_message = data.get("user_message", f"[Scheduled Task] Execute scheduled task for agent {agent_id}")
        
        if not agent_id or not cron_expression:
            raise HTTPException(status_code=400, detail="Agent ID and cron expression are required")
        
        schedule_item = create_schedule(agent_id, cron_expression, user_message)
        
        return Schedule(
            id=schedule_item["id"],
            agentId=schedule_item["agentId"],
            agentName=schedule_item["agentName"],
            cronExpression=schedule_item["cronExpression"],
            status=schedule_item["status"],
            createdAt=schedule_item["createdAt"],
            updatedAt=schedule_item["updatedAt"],
            user_message=schedule_item.get("user_message")
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")

@router.put("/update/{schedule_id}")
async def update_schedule_endpoint(schedule_id: str, request: Request) -> Schedule:
    """
    Update a specific schedule by ID.
    :param schedule_id: The ID of the schedule to update.
    :param request: The request containing the updated schedule data.
    :return: The updated schedule.
    """
    try:
        data = await request.json()
        agent_id = data.get("agentId")
        cron_expression = data.get("cronExpression")
        user_message = data.get("user_message", f"[Scheduled Task] Execute scheduled task for agent {agent_id}")
        
        if not agent_id or not cron_expression:
            raise HTTPException(status_code=400, detail="Agent ID and cron expression are required")
        
        updated_schedule = update_schedule(schedule_id, agent_id, cron_expression, user_message)
        
        return Schedule(
            id=updated_schedule["id"],
            agentId=updated_schedule["agentId"],
            agentName=updated_schedule["agentName"],
            cronExpression=updated_schedule["cronExpression"],
            status=updated_schedule["status"],
            createdAt=updated_schedule["createdAt"],
            updatedAt=updated_schedule["updatedAt"],
            user_message=updated_schedule.get("user_message")
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")

@router.delete("/delete/{schedule_id}")
async def remove_schedule(schedule_id: str) -> Dict[str, Any]:
    """
    Delete a specific schedule by ID.
    :param schedule_id: The ID of the schedule to delete.
    :return: Confirmation of deletion.
    """
    return delete_schedule(schedule_id)
