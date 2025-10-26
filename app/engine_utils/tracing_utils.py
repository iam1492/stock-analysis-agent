"""
Tracing Utilities for ADK Agent Engine

This module provides utilities for handling OpenTelemetry tracing issues,
particularly around async generator cleanup and context management.
"""

import asyncio
import logging
import time
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
        self._context_tokens = []  # Track context tokens for safe detach

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

        # First, safely detach any tracked context tokens
        for token in reversed(self._context_tokens):
            TracingErrorHandler.safe_context_detach(token)
        self._context_tokens.clear()

        # Then close the async generator
        try:
            await self._async_gen.aclose()
        except Exception as e:
            # Suppress OTEL context errors during cleanup
            if "Context" in str(e) and "different Context" in str(e):
                logger.debug(f"Suppressed OTEL context error during cleanup: {e}")
            else:
                logger.warning(f"Error during async generator cleanup: {e}")

    def track_context_token(self, token):
        """Track a context token for safe detach during cleanup."""
        if token is not None:
            self._context_tokens.append(token)


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


class TracingContextManager:
    """
    Enhanced context manager for OpenTelemetry tracing with safe cleanup.

    This provides a more robust alternative to direct use of start_as_current_span
    that handles GeneratorExit scenarios properly.
    """

    def __init__(self, span_name: str, **span_attributes):
        self.span_name = span_name
        self.span_attributes = span_attributes
        self.span = None
        self.context_token = None
        self.start_time = None

    async def __aenter__(self):
        self.start_time = time.time()
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            self.span = tracer.start_span(self.span_name, **self.span_attributes)
            self.context_token = trace.set_span_in_context(self.span)

            # Add performance monitoring attributes
            if self.span:
                self.span.set_attribute("tracing.operation.start_time", self.start_time)

            return self.span
        except Exception as e:
            logger.warning(f"Failed to start tracing span '{self.span_name}': {e}")
            return None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration = end_time - (self.start_time or end_time)

        # Safely detach context first
        if self.context_token:
            detach_start = time.time()
            detach_success = TracingErrorHandler.safe_context_detach(self.context_token)
            detach_duration = time.time() - detach_start

            # Log performance metrics for context operations
            if not detach_success:
                logger.debug(f"Context detach failed for span '{self.span_name}' after {detach_duration:.4f}s")

        # End span if it was created
        if self.span:
            try:
                # Add performance metrics to span
                self.span.set_attribute("tracing.operation.duration", duration)
                self.span.set_attribute("tracing.context.detach_duration", detach_duration if 'detach_duration' in locals() else 0)

                if exc_type is not None:
                    # Record exception in span
                    self.span.record_exception(exc_val)
                    self.span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc_val)))
                    self.span.set_attribute("tracing.operation.error", str(exc_val))
                else:
                    self.span.set_attribute("tracing.operation.success", True)

                self.span.end()
            except Exception as e:
                logger.debug(f"Error ending span: {e}")


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


def create_traced_async_generator(
    async_gen: AsyncGenerator[T, None],
    span_name: str = "async_generator",
    **span_attributes
) -> TracingSafeAsyncGenerator:
    """
    Create a traced async generator with safe cleanup.

    This function wraps an async generator with tracing and safe context management,
    providing better error handling for GeneratorExit scenarios.

    Args:
        async_gen: The async generator to wrap
        span_name: Name for the tracing span
        span_attributes: Additional attributes for the span

    Returns:
        TracingSafeAsyncGenerator with tracing and safe cleanup
    """
    wrapper = TracingSafeAsyncGenerator(async_gen)

    async def traced_generator():
        async with TracingContextManager(span_name, **span_attributes):
            async for item in wrapper:
                yield item

    # Return a new TracingSafeAsyncGenerator wrapping the traced generator
    return TracingSafeAsyncGenerator(traced_generator())


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

    @staticmethod
    def handle_generator_exit(func):
        """
        Decorator to standardize GeneratorExit handling across tracing operations.

        This decorator ensures consistent behavior when GeneratorExit occurs,
        which is common in async generator scenarios with client disconnections.
        """
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"Function {func.__name__} completed successfully in {duration:.4f}s")
                return result
            except GeneratorExit:
                duration = time.time() - start_time
                logger.debug(f"GeneratorExit handled in {func.__name__} after {duration:.4f}s - client disconnection")
                # Don't re-raise GeneratorExit as it's expected
                return None
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {func.__name__} after {duration:.4f}s: {e}")
                raise
        return wrapper

    @staticmethod
    def monitor_tracing_performance(operation_name: str):
        """
        Decorator to monitor tracing operation performance.

        Args:
            operation_name: Name of the operation being monitored
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.debug(f"Tracing operation '{operation_name}' completed in {duration:.4f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.warning(f"Tracing operation '{operation_name}' failed after {duration:.4f}s: {e}")
                    raise
            return wrapper
        return decorator

    @staticmethod
    def safe_context_detach(token) -> bool:
        """
        Safely detach an OpenTelemetry context token.

        This method handles the specific case where GeneratorExit causes
        context detach to fail with "different Context" error.

        Args:
            token: OpenTelemetry context token to detach

        Returns:
            bool: True if detach succeeded, False if safely suppressed
        """
        if token is None:
            return True

        try:
            # Import here to avoid circular imports and handle missing OTEL
            from opentelemetry.context import detach
            detach(token)
            return True
        except ValueError as e:
            if "Context" in str(e) and "different Context" in str(e):
                logger.debug(f"Safely suppressed context detach error (GeneratorExit scenario): {e}")
                return False
            else:
                # Re-raise non-context related ValueError
                raise
        except Exception as e:
            logger.warning(f"Unexpected error during context detach: {e}")
            raise