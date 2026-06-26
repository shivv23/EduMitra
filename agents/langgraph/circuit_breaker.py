"""Circuit breaker and timeout wrapper for agent nodes.

Prevents a failing or hanging agent from blocking the entire graph.
"""

import asyncio
import inspect
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

AGENT_TIMEOUT_SECONDS = 30  # max time per agent node
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
CIRCUIT_BREAKER_RESET_SECONDS = 60


class CircuitState(Enum):
    CLOSED = "closed"       # normal operation
    OPEN = "open"           # failing — block requests
    HALF_OPEN = "half_open" # testing if service recovered


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        reset_seconds: int = CIRCUIT_BREAKER_RESET_SECONDS,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_seconds = reset_seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker OPEN for agent '%s' after %d failures", self.name, self.failure_count)

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.reset_seconds:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker HALF_OPEN for agent '%s' — allowing test request", self.name)
                return True
            return False
        # HALF_OPEN — allow one request
        return True

    async def call(self, fn: Callable[..., T], *args, **kwargs) -> T:
        if not self.allow_request():
            raise CircuitBreakerOpenError(f"Circuit breaker open for agent '{self.name}'")

        try:
            if inspect.iscoroutinefunction(fn):
                result = await asyncio.wait_for(fn(*args, **kwargs), timeout=AGENT_TIMEOUT_SECONDS)
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(fn, *args, **kwargs),
                    timeout=AGENT_TIMEOUT_SECONDS,
                )
            self.record_success()
            return result
        except asyncio.TimeoutError:
            self.record_failure()
            raise AgentTimeoutError(f"Agent '{self.name}' timed out after {AGENT_TIMEOUT_SECONDS}s")
        except Exception as e:
            self.record_failure()
            raise


class CircuitBreakerOpenError(Exception):
    pass


class AgentTimeoutError(Exception):
    pass


# Registry of per-agent circuit breakers
_breakers: Dict[str, CircuitBreaker] = {}


def get_breaker(agent_name: str) -> CircuitBreaker:
    if agent_name not in _breakers:
        _breakers[agent_name] = CircuitBreaker(name=agent_name)
    return _breakers[agent_name]


def agent_node_wrapper(agent_name: str, fn: Callable) -> Callable:
    """Wrap an agent node function with circuit breaker + timeout."""
    breaker = get_breaker(agent_name)

    async def wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return await breaker.call(fn, state)
        except (CircuitBreakerOpenError, AgentTimeoutError) as e:
            logger.error("Agent '%s' failed: %s", agent_name, str(e))
            state["agent_outputs"][agent_name] = {
                "agent_name": agent_name,
                "success": False,
                "data": None,
                "error": str(e),
            }
            state["processing_error"] = str(e)
            return state

    return wrapped
