"""
Agent Results API

Provides REST API endpoints for saving and loading agent analysis results.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.agent_result_storage import agent_storage

logger = logging.getLogger(__name__)

# Create router - will be mounted at /agent-results
router = APIRouter(tags=["agent-results"])


class SaveAgentResultRequest(BaseModel):
    user_id: str
    session_id: str
    stock_symbol: str
    agent_name: str
    content: str
    message_id: Optional[str] = None


class SaveAgentResultResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None


class LoadAgentResultResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ListAgentResultsResponse(BaseModel):
    success: bool
    results: Optional[list] = None
    agents: Optional[list] = None
    error: Optional[str] = None


@router.post("/save", response_model=SaveAgentResultResponse)
async def save_agent_result(
    request: SaveAgentResultRequest,
    background_tasks: BackgroundTasks
):
    """
    Save an agent analysis result to the filesystem.
    """
    try:
        logger.info(f"Saving {request.agent_name} result for user {request.user_id}, session {request.session_id}")

        # Save the result asynchronously in the background
        success = await agent_storage.save_agent_result(
            user_id=request.user_id,
            session_id=request.session_id,
            stock_symbol=request.stock_symbol,
            agent_name=request.agent_name,
            content=request.content,
            metadata={
                "message_id": request.message_id,
                "saved_via": "api"
            }
        )

        if success:
            # Construct file path for response
            folder_path = agent_storage._get_folder_path(
                request.user_id,
                request.session_id,
                request.stock_symbol
            )
            file_path = str(folder_path / f"{request.agent_name}.json")

            logger.info(f"Successfully saved {request.agent_name} result to {file_path}")

            return SaveAgentResultResponse(
                success=True,
                message=f"Successfully saved {request.agent_name} result",
                file_path=file_path
            )
        else:
            logger.error(f"Failed to save {request.agent_name} result")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save {request.agent_name} result"
            )

    except Exception as e:
        logger.error(f"Error saving agent result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load", response_model=LoadAgentResultResponse)
async def load_agent_result(request: dict):
    """
    Load a specific agent result.
    """
    try:
        user_id = request.get("user_id")
        session_id = request.get("session_id")
        stock_symbol = request.get("stock_symbol")
        agent_name = request.get("agent_name")

        if not all([user_id, session_id, stock_symbol, agent_name]):
            raise HTTPException(status_code=400, detail="Missing required parameters")

        logger.info(f"Loading {agent_name} result for user {user_id}, session {session_id}")

        result = await agent_storage.load_agent_result(
            user_id=user_id,
            session_id=session_id,
            stock_symbol=stock_symbol,
            agent_name=agent_name
        )

        if result:
            return LoadAgentResultResponse(success=True, result=result)
        else:
            return LoadAgentResultResponse(
                success=False,
                error=f"Agent result not found: {agent_name}"
            )

    except Exception as e:
        logger.error(f"Error loading agent result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/list", response_model=ListAgentResultsResponse)
async def list_agent_results(request: dict):
    """
    List all available agent results for a session.
    """
    try:
        user_id = request.get("user_id")
        session_id = request.get("session_id")
        stock_symbol = request.get("stock_symbol")

        if not all([user_id, session_id, stock_symbol]):
            raise HTTPException(status_code=400, detail="Missing required parameters")

        logger.info(f"Listing agent results for user {user_id}, session {session_id}")

        agents = await agent_storage.get_available_agents(
            user_id=user_id,
            session_id=session_id,
            stock_symbol=stock_symbol
        )

        if agents:
            # Load all results
            results = []
            for agent_name in agents:
                result = await agent_storage.load_agent_result(
                    user_id=user_id,
                    session_id=session_id,
                    stock_symbol=stock_symbol,
                    agent_name=agent_name
                )
                if result:
                    results.append(result)

            return ListAgentResultsResponse(success=True, results=results, agents=agents)
        else:
            return ListAgentResultsResponse(
                success=True,
                results=[],
                agents=[],
                error="No agent results found for this session"
            )

    except Exception as e:
        logger.error(f"Error listing agent results: {e}")
        raise HTTPException(status_code=500, detail=str(e))