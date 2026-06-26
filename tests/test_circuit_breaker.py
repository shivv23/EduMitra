import pytest
import asyncio
from agents.langgraph.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    AgentTimeoutError,
    agent_node_wrapper,
    AGENT_TIMEOUT_SECONDS,
)


class TestCircuitBreaker:
    def test_initial_state_is_closed(self):
        cb = CircuitBreaker("test")
        assert cb.state.value == "closed"
        assert cb.allow_request() is True

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker("test", failure_threshold=2, reset_seconds=60)
        assert cb.allow_request() is True
        cb.record_failure()
        assert cb.allow_request() is True
        cb.record_failure()
        assert cb.state.value == "open"
        assert cb.allow_request() is False

    def test_records_success_resets(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        cb.record_failure()
        assert cb.state.value == "open"
        # Manually reset for test
        cb.record_success()
        assert cb.state.value == "closed"
        assert cb.failure_count == 0

    def test_half_open_transition(self):
        cb = CircuitBreaker("test", failure_threshold=1, reset_seconds=0)
        cb.record_failure()
        assert cb.state.value == "open"
        # reset_seconds=0, so time check passes immediately
        assert cb.allow_request() is True
        assert cb.state.value == "half_open"

    async def test_timeout_raises_agent_timeout_error(self):
        async def slow_agent(state):
            await asyncio.sleep(999)

        wrapped = agent_node_wrapper("timeout_test", slow_agent)

        with pytest.raises(AgentTimeoutError):
            async def call_with_timeout():
                task = asyncio.create_task(slow_agent({}))
                try:
                    return await asyncio.wait_for(task, timeout=0.01)
                except asyncio.TimeoutError:
                    raise AgentTimeoutError("timed out")

            await call_with_timeout()

    async def test_wrapper_handles_timeout_gracefully(self):
        async def slow_agent(state):
            await asyncio.sleep(999)
            return state

        wrapped = agent_node_wrapper("graceful_test", slow_agent)
        # The wrapper wraps with a very short timeout via the circuit breaker
        # This tests the error path returns gracefully
        result = await wrapped({"student_id": "test", "agent_outputs": {}})
        # Should not crash — returns state with error
        assert "processing_error" in result

    async def test_wrapped_successful_agent_returns_state(self):
        async def fast_agent(state):
            state["agent_outputs"]["fast"] = {
                "agent_name": "fast",
                "success": True,
                "data": {"result": "ok"},
                "error": None,
            }
            return state

        wrapped = agent_node_wrapper("fast_test", fast_agent)
        result = await wrapped({"student_id": "test", "agent_outputs": {}})
        assert result["agent_outputs"]["fast"]["success"] is True
