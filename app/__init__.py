"""Stock Analysis Agent Application Package"""

# Disable OpenTelemetry tracing to prevent context detachment errors
# This must be done before any ADK imports to prevent OpenTelemetry initialization
import os
import sys

# Set environment variables to completely disable OpenTelemetry
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_TRACES_EXPORTER"] = "none"

# Completely disable OpenTelemetry by overriding critical functions
def _disable_opentelemetry():
    """Completely disable OpenTelemetry to prevent context detachment errors"""
    
    # Override context management to prevent token issues
    try:
        import opentelemetry.context
        
        # Save original detach function
        original_detach = opentelemetry.context._RUNTIME_CONTEXT.detach
        
        def safe_detach(token):
            """Safe detach that handles context detachment errors"""
            try:
                return original_detach(token)
            except (ValueError, RuntimeError) as e:
                # Log of error but don't crash
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"OpenTelemetry context detachment error suppressed: {e}")
                return None
        
        # Replace: detach function
        opentelemetry.context._RUNTIME_CONTEXT.detach = safe_detach
        
        # Also override: context reset to prevent errors
        original_reset = opentelemetry.context._RUNTIME_CONTEXT.reset
        
        def safe_reset(token):
            """Safe reset that handles context reset errors"""
            try:
                return original_reset(token)
            except (ValueError, RuntimeError) as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"OpenTelemetry context reset error suppressed: {e}")
                return None
        
        opentelemetry.context._RUNTIME_CONTEXT.reset = safe_reset
    except (ImportError, AttributeError) as e:
        # If OpenTelemetry is not available or doesn't have expected attributes, skip
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"OpenTelemetry not available or incompatible: {e}")

# Apply: disable function
_disable_opentelemetry()

# Additional monkey patch to handle context detachment at the source
def _patch_context_detach():
    """Patch: detach function to handle context detachment errors gracefully"""
    try:
        import opentelemetry.context
        
        # Get: runtime context
        runtime_context = opentelemetry.context._RUNTIME_CONTEXT
        
        # Override: detach method to handle errors gracefully
        def patched_detach(token):
            try:
                return runtime_context.__class__.detach(runtime_context, token)
            except (ValueError, RuntimeError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"OpenTelemetry context detachment error handled gracefully: {e}")
                return None
        
        # Apply: patch
        runtime_context.detach = patched_detach
        
    except (ImportError, AttributeError):
        # OpenTelemetry not available, skip
        pass

# Apply: additional patch
_patch_context_detach()

# Monkey patch OpenTelemetry to prevent initialization
class NoOpTracer:
    def start_as_current_span(self, *args, **kwargs):
        return self._no_op_context_manager()
    
    def start_span(self, *args, **kwargs):
        return self._no_op_context_manager()
    
    def _no_op_context_manager(self):
        class NoOpSpan:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def set_attribute(self, *args, **kwargs):
                pass
            def set_status(self, *args, **kwargs):
                pass
            def record_exception(self, *args, **kwargs):
                pass
            def end(self, *args, **kwargs):
                pass
        return NoOpSpan()
    
    @property
    def tracer_provider(self):
        return NoOpTracerProvider()

class NoOpTracerProvider:
    def get_tracer(self, *args, **kwargs):
        return NoOpTracer()

class NoOpContextManager:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

# Prevent OpenTelemetry from being imported and used
sys.modules['opentelemetry'] = type(sys)('opentelemetry')
sys.modules['opentelemetry.trace'] = type(sys)('opentelemetry.trace')
sys.modules['opentelemetry.context'] = type(sys)('opentelemetry.context')
sys.modules['opentelemetry.sdk'] = type(sys)('opentelemetry.sdk')
sys.modules['opentelemetry.sdk.trace'] = type(sys)('opentelemetry.sdk.trace')

# Patch Python's ContextVar to prevent context detachment issues
def _patch_contextvar():
    """Patch ContextVar to handle context detachment gracefully"""
    try:
        import contextvars
        
        # Save original ContextVar
        original_contextvar = contextvars.ContextVar
        
        class SafeContextVar:
            """Safe ContextVar that handles context detachment gracefully"""
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
            
            def set(self, value):
                try:
                    return super().set(value)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"ContextVar set error handled gracefully: {e}")
                    return None
            
            def get(self, default=None):
                try:
                    return super().get(default)
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.warning(f"ContextVar get error handled gracefully: {e}")
                    return default
        
        # Replace ContextVar with SafeContextVar
        contextvars.ContextVar = SafeContextVar
        
    except ImportError:
        # contextvars not available, skip
        pass

# Apply ContextVar patch
_patch_contextvar()

# Patch asyncio TaskGroup to handle context issues
def _patch_asyncio():
    """Patch asyncio TaskGroup to handle context issues gracefully"""
    try:
        import asyncio
        
        # Save original TaskGroup
        original_taskgroup = asyncio.TaskGroup
        
        class SafeTaskGroup(original_taskgroup):
            """Safe TaskGroup that handles context detachment gracefully"""
            def __aexit__(self, exc_type, exc_val, exc_tb):
                try:
                    return super().__aexit__(exc_type, exc_val, exc_tb)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"TaskGroup exit error handled gracefully: {e}")
                    return None
        
        # Replace TaskGroup with SafeTaskGroup
        asyncio.TaskGroup = SafeTaskGroup
        
    except ImportError:
        # asyncio not available, skip
        pass

# Apply asyncio patch
_patch_asyncio()

# Patch ADK internal tracing functions to completely disable OpenTelemetry
def _patch_adk_tracing():
    """Patch ADK internal tracing functions to completely disable OpenTelemetry"""
    try:
        # Patch base_llm_flow tracing - use safe attribute access
        import google.adk.flows.llm_flows.base_llm_flow
        
        def no_op_tracing_context_manager():
            class NoOpTracingSpan:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
                def set_attribute(self, *args, **kwargs):
                    pass
                def set_status(self, *args, **kwargs):
                    pass
                def record_exception(self, *args, **kwargs):
                    pass
                def end(self, *args, **kwargs):
                    pass
            return NoOpTracingSpan()
        
        # Safely replace _call_llm_with_tracing if it exists
        if hasattr(google.adk.flows.llm_flows.base_llm_flow, '_call_llm_with_tracing'):
            original_call_llm_with_tracing = google.adk.flows.llm_flows.base_llm_flow._call_llm_with_tracing
            
            def no_op_call_llm_with_tracing(llm_response, ctx, *args, **kwargs):
                """No-op version of _call_llm_with_tracing that doesn't use OpenTelemetry"""
                yield llm_response
            
            google.adk.flows.llm_flows.base_llm_flow._call_llm_with_tracing = no_op_call_llm_with_tracing
        
        # Patch runners tracing - use safe attribute access
        import google.adk.runners
        
        if hasattr(google.adk.runners, '_run_with_trace'):
            original_run_with_trace = google.adk.runners._run_with_trace
            
            def no_op_run_with_trace(agent_or_app, ctx, *args, **kwargs):
                """No-op version of _run_with_trace that doesn't use OpenTelemetry"""
                # Directly call the agent without tracing
                if hasattr(agent_or_app, 'run_async'):
                    return agent_or_app.run_async(ctx)
                else:
                    # Fallback for app objects
                    return agent_or_app(ctx)
            
            google.adk.runners._run_with_trace = no_op_run_with_trace
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info("ADK internal tracing functions patched to disable OpenTelemetry")
        
    except ImportError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to patch ADK tracing: {e}")

# Apply ADK tracing patch
_patch_adk_tracing()

# Disable MCP to prevent context issues from MCP connections
def _disable_mcp():
    """Disable MCP to prevent context issues from MCP connections"""
    try:
        # Disable MCP toolsets
        import google.adk.tools.mcp_tool
        
        original_mcp_toolset_init = google.adk.tools.mcp_tool.MCPToolset.__init__
        
        def no_op_mcp_toolset_init(self, *args, **kwargs):
            """No-op MCP Toolset initialization"""
            # Don't initialize MCP session manager
            pass
        
        google.adk.tools.mcp_tool.MCPToolset.__init__ = no_op_mcp_toolset_init
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info("MCP toolsets disabled to prevent context issues")
        
    except ImportError:
        pass

# Apply MCP disable
_disable_mcp()

# Set up logging configuration
from .logging_config import setup_logging
setup_logging()

# Load Firestore configurations before importing agents
# This ensures model configurations are ready when agents are created
from .sub_agents.utils.firestore_config import FirestoreConfig
FirestoreConfig.load_configs()

# Import main agent module
from . import agent

__all__ = ["agent"]