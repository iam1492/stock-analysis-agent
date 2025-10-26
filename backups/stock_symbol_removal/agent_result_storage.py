"""
Agent Result Storage Service

This module handles saving and loading agent results to/from the filesystem.
Results are organized by user ID, session ID, and stock symbol for easy retrieval.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from pathlib import Path


class AgentResultStorage:
    """Service for storing and retrieving agent analysis results"""

    def __init__(self, base_dir: str = "results"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def _extract_stock_symbol(self, query: str) -> str:
        """
        Extract stock symbol from user query.
        Examples:
        - "Tesla 종목을 분석해줘" -> "tesla"
        - "AAPL 주식을 분석해달라" -> "aapl"
        - "삼성전자 분석 부탁해" -> "samsung"
        """
        # Common patterns for stock mentions
        patterns = [
            r'([A-Z]{1,5})\s+(?:종목|주식|주가|주)',  # AAPL 종목, TSLA 주식
            r'([A-Z]{1,5})\s+(?:을|를)\s+분석',  # AAPL을 분석
            r'([A-Z]{1,5})\s+(?:에\s+대해|에\s+대한)',  # AAPL에 대해
            r'([가-힣a-zA-Z]+)\s+(?:종목|주식|주가|주)',  # 삼성전자 종목, Tesla 주식
            r'([가-힣a-zA-Z]+)\s+(?:을|를)\s+분석',  # 삼성전자를 분석
            r'([가-힣a-zA-Z]+)\s+(?:에\s+대해|에\s+대한)',  # 삼성전자에 대해
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                symbol = match.group(1).lower()
                # Clean up Korean company names
                symbol = re.sub(r'[가-힣]', '', symbol)
                return symbol.strip() if symbol.strip() else "unknown"

        return "unknown"

    def _get_folder_path(self, user_id: str, session_id: str, stock_symbol: str) -> Path:
        """Generate folder path for storing results"""
        # Sanitize inputs for filesystem safety
        safe_user_id = re.sub(r'[^\w\-_]', '_', user_id)
        safe_session_id = re.sub(r'[^\w\-_]', '_', session_id)
        safe_stock_symbol = re.sub(r'[^\w\-_]', '_', stock_symbol)

        folder_name = f"session_{safe_session_id}_{safe_stock_symbol}"
        return self.base_dir / f"user_{safe_user_id}" / folder_name

    async def save_agent_result(
        self,
        user_id: str,
        session_id: str,
        stock_symbol: str,
        agent_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save agent result to file

        Args:
            user_id: User identifier
            session_id: Session identifier
            stock_symbol: Stock symbol (extracted from query)
            agent_name: Name of the agent
            content: Full text content from agent
            metadata: Additional metadata (timestamps, etc.)

        Returns:
            bool: Success status
        """
        try:
            folder_path = self._get_folder_path(user_id, session_id, stock_symbol)
            folder_path.mkdir(parents=True, exist_ok=True)

            file_path = folder_path / f"{agent_name}.json"

            result_data = {
                "agent_name": agent_name,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "stock_symbol": stock_symbol,
                "metadata": metadata or {}
            }

            # Write to file asynchronously
            def write_file():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)

            await asyncio.get_event_loop().run_in_executor(None, write_file)

            print(f"✅ Saved {agent_name} result to {file_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to save {agent_name} result: {e}")
            return False

    async def load_agent_result(
        self,
        user_id: str,
        session_id: str,
        stock_symbol: str,
        agent_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load agent result from file

        Returns:
            Dict containing result data or None if not found
        """
        try:
            folder_path = self._get_folder_path(user_id, session_id, stock_symbol)
            file_path = folder_path / f"{agent_name}.json"

            if not file_path.exists():
                return None

            def read_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            result_data = await asyncio.get_event_loop().run_in_executor(None, read_file)
            return result_data

        except Exception as e:
            print(f"❌ Failed to load {agent_name} result: {e}")
            return None

    async def get_available_agents(
        self,
        user_id: str,
        session_id: str,
        stock_symbol: str
    ) -> List[str]:
        """
        Get list of available agent results for a session

        Returns:
            List of agent names that have saved results
        """
        try:
            folder_path = self._get_folder_path(user_id, session_id, stock_symbol)

            if not folder_path.exists():
                return []

            def list_files():
                return [f.stem for f in folder_path.glob("*.json") if f.is_file()]

            agents = await asyncio.get_event_loop().run_in_executor(None, list_files)
            return agents

        except Exception as e:
            print(f"❌ Failed to get available agents: {e}")
            return []

    def extract_stock_from_query(self, query: str) -> str:
        """Public method to extract stock symbol from query"""
        return self._extract_stock_symbol(query)


# Global instance
agent_storage = AgentResultStorage()