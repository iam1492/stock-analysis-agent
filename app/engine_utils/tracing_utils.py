"""
Tracing Utilities for ADK Agent Engine

This module provides utilities for handling OpenTelemetry tracing issues,
particularly around async generator cleanup and context management.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar, Any, Optional

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TracingSafeAsyncGenerator:
    """
    Wrapper for async generators that handles GeneratorExit and OTEL context issues safely.

    This wrapper ensures that async generators are properly cleaned up even when
    clients disconnect abruptly, preventing OTEL context token errors.
    """

    def __init__(self, async_gen: AsyncGenerator[T, None]):
        self._async_gen = async_gen
        self._closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._safe_aclose()

    def __aiter__(self):
        return self

    async def __anext__(self) -> T:
        try:
            if self._closed:
                raise StopAsyncIteration
            return await self._async_gen.__anext__()
        except GeneratorExit:
            # This is expected when client disconnects - log at debug level
            logger.debug("GeneratorExit caught - client likely disconnected")
            await self._safe_aclose()
            raise StopAsyncIteration
        except Exception as e:
            # Log other exceptions but don't suppress them
            logger.error(f"Error in async generator: {e}")
            await self._safe_aclose()
            raise

    async def _safe_aclose(self):
        """Safely close the async generator, handling OTEL context issues."""
        if self._closed:
            return

        self._closed = True
        try:
            await self._async_gen.aclose()
        except Exception as e:
            # Suppress OTEL context errors during cleanup
            if "Context" in str(e) and "different Context" in str(e):
                logger.debug(f"Suppressed OTEL context error during cleanup: {e}")
            else:
                logger.warning(f"Error during async generator cleanup: {e}")


@asynccontextmanager
async def safe_async_generator_context(async_gen: AsyncGenerator[T, None]):
    """
    Context manager that wraps an async generator with safe cleanup.

    Usage:
        async with safe_async_generator_context(agent.run_async(ctx)) as agen:
            async for event in agen:
                yield event
    """
    wrapper = TracingSafeAsyncGenerator(async_gen)
    try:
        yield wrapper
    finally:
        await wrapper._safe_aclose()


async def consume_async_generator_safely(
    async_gen: AsyncGenerator[T, None],
    max_events: Optional[int] = None
) -> list[T]:
    """
    Consume an async generator safely, handling GeneratorExit and cleanup.

    Args:
        async_gen: The async generator to consume
        max_events: Maximum number of events to consume (None for all)

    Returns:
        List of all events consumed
    """
    events = []
    event_count = 0

    async with safe_async_generator_context(async_gen) as safe_gen:
        try:
            async for event in safe_gen:
                events.append(event)
                event_count += 1
                if max_events and event_count >= max_events:
                    break
        except StopAsyncIteration:
            pass  # Normal end of generator
        except GeneratorExit:
            logger.debug("GeneratorExit during consumption - normal client disconnect")
        except Exception as e:
            logger.error(f"Unexpected error during generator consumption: {e}")
            raise

    return events


def create_sse_event_generator(
    async_gen: AsyncGenerator[Any, None],
    event_formatter: Optional[callable] = None
) -> AsyncGenerator[str, None]:
    """
    Create a safe SSE event generator from an async generator.

    Args:
        async_gen: Source async generator
        event_formatter: Function to format events (default: JSON dump)

    Yields:
        SSE formatted event strings
    """
    if event_formatter is None:
        def event_formatter(event):
            if hasattr(event, 'model_dump_json'):
                return event.model_dump_json(exclude_none=True, by_alias=True)
            else:
                return str(event)

    async def sse_generator():
        async with safe_async_generator_context(async_gen) as safe_gen:
            try:
                async for event in safe_gen:
                    formatted_event = event_formatter(event)
                    yield f"data: {formatted_event}\n\n"
            except StopAsyncIteration:
                pass
            except GeneratorExit:
                logger.debug("SSE generator exited - client disconnected")
            except Exception as e:
                logger.error(f"Error in SSE generator: {e}")
                yield f'data: {{"error": "{str(e)}"}}\n\n'

    return sse_generator()


class TracingErrorHandler:
    """Handles OTEL tracing errors gracefully."""

    @staticmethod
    def suppress_context_errors(func):
        """
        Decorator to suppress OTEL context token errors.

        Use this for cleanup functions that might fail due to context issues.
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                if "Context" in str(e) and "different Context" in str(e):
                    logger.debug(f"Suppressed OTEL context error: {e}")
                    return None
                else:
                    raise
        return wrapper

    @staticmethod
    async def safe_aclose(async_gen: AsyncGenerator[Any, None]):
        """Safely close an async generator, suppressing context errors."""
        try:
            await async_gen.aclose()
        except ValueError as e:
            if "Context" in str(e) and "different Context" in str(e):
                logger.debug(f"Suppressed OTEL context error during aclose: {e}")
            else:
                raise
        except Exception as e:
            logger.warning(f"Error during async generator close: {e}")
            raise