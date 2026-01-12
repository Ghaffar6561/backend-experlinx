from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...db.session import get_db_session
from ...schemas.subscription import SubscriptionPlanInfo, SubscriptionDetail
from ...schemas.common import ApiResponse
from ...services.subscription import SubscriptionService
from ...core.dependencies import get_current_user, require_role
from ...models.user import User


router = APIRouter()


@router.get("/plans", response_model=ApiResponse[List[SubscriptionPlanInfo]])
async def list_subscription_plans():
    """
    List all available subscription plans.
    """
    plans = await SubscriptionService.list_plans()
    return ApiResponse(data=plans)


@router.get("/current", response_model=ApiResponse[SubscriptionDetail])
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get the current subscription for the authenticated user.
    """
    subscription = await SubscriptionService.get_current(db_session, current_user.id)
    if not subscription:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    return ApiResponse(data=subscription)


@router.post("/subscribe", response_model=ApiResponse[SubscriptionDetail])
async def subscribe_to_plan(
    plan: str,  # In a real app, this would be in the request body
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Subscribe the authenticated user to a plan.
    """
    from ...schemas.subscription import SubscriptionPlan
    try:
        plan_enum = SubscriptionPlan(plan)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    subscription = await SubscriptionService.subscribe(db_session, current_user.id, plan_enum)
    return ApiResponse(data=subscription)


@router.post("/cancel", response_model=ApiResponse[SubscriptionDetail])
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Cancel the authenticated user's subscription.
    """
    subscription = await SubscriptionService.cancel(db_session, current_user.id)
    if not subscription:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No subscription found to cancel")
    
    return ApiResponse(data=subscription)