from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import uuid
from ..models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from ..schemas.subscription import SubscriptionPlanInfo, SubscriptionDetail


async def check_user_subscription_valid(db_session: AsyncSession, user_id: str) -> bool:
    """
    Check if a user has a valid (active) subscription.

    Args:
        db_session: The database session
        user_id: The ID of the user to check

    Returns:
        True if the user has an active subscription, False otherwise
    """
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE.value,
        (Subscription.expires_at.is_(None)) | (Subscription.expires_at > datetime.utcnow())
    )

    result = await db_session.execute(stmt)
    subscription = result.scalar_one_or_none()

    return subscription is not None


class SubscriptionService:
    @staticmethod
    async def list_plans() -> List[SubscriptionPlanInfo]:
        """
        List all available subscription plans.

        Returns:
            A list of subscription plan information
        """
        # Define the available plans with their token limits and prices
        from ..schemas.subscription import SubscriptionPlanInfo
        plans = [
            SubscriptionPlanInfo(
                plan=SubscriptionPlan.FREE,
                token_limit=1000,
                price_monthly=0.0
            ),
            SubscriptionPlanInfo(
                plan=SubscriptionPlan.PRO,
                token_limit=50000,
                price_monthly=29.99
            ),
            SubscriptionPlanInfo(
                plan=SubscriptionPlan.ENTERPRISE,
                token_limit=500000,
                price_monthly=299.99
            )
        ]

        return plans

    @staticmethod
    async def get_current(
        db_session: AsyncSession,
        user_id: str
    ) -> Optional[SubscriptionDetail]:
        """
        Get the current subscription for a user.

        Args:
            db_session: The database session
            user_id: The ID of the user

        Returns:
            The current subscription details, or None if no subscription exists
        """
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await db_session.execute(stmt)
        subscription = result.scalar_one_or_none()

        if subscription:
            return SubscriptionDetail.from_orm(subscription)
        return None

    @staticmethod
    async def subscribe(
        db_session: AsyncSession,
        user_id: str,
        plan: SubscriptionPlan
    ) -> SubscriptionDetail:
        """
        Subscribe a user to a plan.

        Args:
            db_session: The database session
            user_id: The ID of the user
            plan: The plan to subscribe to

        Returns:
            The new subscription details
        """
        # Get the token limit for the plan
        plan_limits = {
            SubscriptionPlan.FREE: 1000,
            SubscriptionPlan.PRO: 50000,
            SubscriptionPlan.ENTERPRISE: 500000
        }

        token_limit = plan_limits.get(plan, 1000)  # Default to free tier if plan not found

        # Check if user already has a subscription
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await db_session.execute(stmt)
        existing_subscription = result.scalar_one_or_none()

        if existing_subscription:
            # Update the existing subscription
            existing_subscription.plan = plan.value
            existing_subscription.status = SubscriptionStatus.ACTIVE.value
            existing_subscription.token_limit = token_limit
            existing_subscription.tokens_used = 0  # Reset token usage
            existing_subscription.period_start = datetime.utcnow()

            # Set expiration date based on plan (for demo purposes, set to 30 days from now)
            if plan != SubscriptionPlan.FREE:
                existing_subscription.expires_at = datetime.utcnow() + timedelta(days=30)
            else:
                existing_subscription.expires_at = None  # Free tier never expires

            await db_session.commit()
            await db_session.refresh(existing_subscription)

            return SubscriptionDetail.from_orm(existing_subscription)
        else:
            # Create a new subscription
            # Set expiration date based on plan (for demo purposes, set to 30 days from now)
            expires_at = None
            if plan != SubscriptionPlan.FREE:
                expires_at = datetime.utcnow() + timedelta(days=30)

            new_subscription = Subscription(
                user_id=user_id,
                plan=plan.value,
                status=SubscriptionStatus.ACTIVE.value,
                token_limit=token_limit,
                tokens_used=0,
                period_start=datetime.utcnow(),
                expires_at=expires_at
            )

            db_session.add(new_subscription)
            await db_session.commit()
            await db_session.refresh(new_subscription)

            return SubscriptionDetail.from_orm(new_subscription)

    @staticmethod
    async def cancel(
        db_session: AsyncSession,
        user_id: str
    ) -> Optional[SubscriptionDetail]:
        """
        Cancel a user's subscription.

        Args:
            db_session: The database session
            user_id: The ID of the user

        Returns:
            The updated subscription details, or None if no subscription exists
        """
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await db_session.execute(stmt)
        subscription = result.scalar_one_or_none()

        if not subscription:
            return None

        # Update the subscription status to cancelled
        subscription.status = SubscriptionStatus.CANCELLED.value
        await db_session.commit()
        await db_session.refresh(subscription)

        return SubscriptionDetail.from_orm(subscription)

    @staticmethod
    async def check_token_limit(
        db_session: AsyncSession,
        user_id: str
    ) -> bool:
        """
        Check if a user has exceeded their token limit.

        Args:
            db_session: The database session
            user_id: The ID of the user

        Returns:
            True if the user has not exceeded their limit, False otherwise
        """
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await db_session.execute(stmt)
        subscription = result.scalar_one_or_none()

        if not subscription:
            # If no subscription exists, assume free tier with 1000 token limit
            return 0 < 1000

        # Check if tokens used exceed the limit
        return subscription.tokens_used < subscription.token_limit