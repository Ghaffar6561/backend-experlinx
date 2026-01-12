from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
from uuid import UUID
import httpx
import time
import asyncio
from enum import Enum
from datetime import datetime, timedelta
from ..models.tool import Tool
from ..models.subscription import Subscription
from ..schemas.tool import ToolSummary, ToolDetail, ToolInvocationRequest, ToolInvocationResult
from ..core.config import settings
from .subscription import check_user_subscription_valid
from .usage import log_tool_invocation


class CircuitBreakerState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Tripped, requests blocked
    HALF_OPEN = "half_open"  # Testing if failure condition is resolved


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold  # Number of failures before opening
        self.timeout = timeout  # Time in seconds before attempting to close
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute the function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    async def async_call(self, func, *args, **kwargs):
        """Execute the async function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def _should_attempt_reset(self):
        """Check if enough time has passed to attempt resetting the circuit."""
        if self.last_failure_time is None:
            return False
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)


# Global circuit breaker instances for each tool
_TOOL_CIRCUIT_BREAKERS = {}


def get_circuit_breaker(tool_id: str) -> CircuitBreaker:
    """Get or create a circuit breaker for a specific tool."""
    if tool_id not in _TOOL_CIRCUIT_BREAKERS:
        _TOOL_CIRCUIT_BREAKERS[tool_id] = CircuitBreaker()
    return _TOOL_CIRCUIT_BREAKERS[tool_id]


class ToolService:
    @staticmethod
    async def list_tools(
        db_session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = True
    ) -> List[ToolSummary]:
        """
        List available tools with pagination.
        
        Args:
            db_session: The database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Whether to return only active tools
            
        Returns:
            A list of tool summaries
        """
        stmt = select(Tool)
        if active_only:
            stmt = stmt.where(Tool.is_active == True)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db_session.execute(stmt)
        tools = result.scalars().all()
        
        return [ToolSummary.from_orm(tool) for tool in tools]
    
    @staticmethod
    async def get_tool(db_session: AsyncSession, tool_id: str) -> Optional[ToolDetail]:
        """
        Get detailed information about a specific tool.
        
        Args:
            db_session: The database session
            tool_id: The ID of the tool to retrieve
            
        Returns:
            Detailed information about the tool, or None if not found
        """
        stmt = select(Tool).where(Tool.id == tool_id)
        result = await db_session.execute(stmt)
        tool = result.scalar_one_or_none()
        
        if tool:
            return ToolDetail.from_orm(tool)
        return None
    
    @staticmethod
    async def invoke_tool(
        db_session: AsyncSession,
        user: Any,  # User object (we can't import here due to circular dependency)
        tool_id: str,
        invocation_request: ToolInvocationRequest
    ) -> ToolInvocationResult:
        """
        Invoke a tool with the given input.

        Args:
            db_session: The database session
            user: The user invoking the tool
            tool_id: The ID of the tool to invoke
            invocation_request: The input for the tool

        Returns:
            The result of the tool invocation
        """
        # First, check if the user has a valid subscription
        has_valid_subscription = await check_user_subscription_valid(db_session, user.id)
        if not has_valid_subscription:
            return ToolInvocationResult(
                success=False,
                error="User does not have an active subscription"
            )

        # Check if the user has exceeded their token limit
        from .subscription import SubscriptionService
        has_token_limit = await SubscriptionService.check_token_limit(db_session, user.id)
        if not has_token_limit:
            return ToolInvocationResult(
                success=False,
                error="User has exceeded their token limit"
            )

        # Get the tool
        stmt = select(Tool).where(Tool.id == tool_id, Tool.is_active == True)
        result = await db_session.execute(stmt)
        tool = result.scalar_one_or_none()

        if not tool:
            return ToolInvocationResult(
                success=False,
                error="Tool not found or inactive"
            )

        # Get the circuit breaker for this tool
        circuit_breaker = get_circuit_breaker(tool.id)

        # Measure execution time
        start_time = time.time()

        try:
            # Execute the tool invocation with circuit breaker protection
            result_data = await circuit_breaker.async_call(
                _invoke_external_tool,
                tool,
                invocation_request.input,
                start_time
            )

            # Calculate tokens used (simplified calculation)
            tokens_used = len(str(result_data))

            # Update the subscription's token usage
            stmt = select(Subscription).where(Subscription.user_id == user.id)
            result = await db_session.execute(stmt)
            subscription = result.scalar_one_or_none()

            if subscription:
                subscription.tokens_used += tokens_used
                await db_session.commit()

            duration_ms = int((time.time() - start_time) * 1000)

            # Log the usage
            await log_tool_invocation(
                db_session=db_session,
                user_id=user.id,
                tool_id=tool.id,
                tokens_used=tokens_used,
                duration_ms=duration_ms
            )

            return ToolInvocationResult(
                success=True,
                result=result_data,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Log the error
            await log_tool_invocation(
                db_session=db_session,
                user_id=user.id,
                tool_id=tool.id,
                tokens_used=0,
                duration_ms=duration_ms,
                response_status="error"
            )

            return ToolInvocationResult(
                success=False,
                error=f"Tool invocation failed: {str(e)}",
                duration_ms=duration_ms
            )


async def _invoke_external_tool(tool, input_data, start_time):
    """
    Internal function to invoke the external tool.

    Args:
        tool: The tool object with API endpoint
        input_data: The input data for the tool
        start_time: The start time for measuring duration

    Returns:
        The result from the external tool
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                tool.api_endpoint,
                json=input_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"JoyfullUIHub/{settings.APP_VERSION}"
                }
            )

            if response.status_code != 200:
                raise Exception(f"Tool returned status code: {response.status_code}")

            return response.json()
    except httpx.TimeoutException:
        duration_ms = int((time.time() - start_time) * 1000)
        raise Exception("Tool invocation timed out")
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        raise e