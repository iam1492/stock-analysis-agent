"""
Shared utility module for Financial Modeling Prep API calls.
This module provides common functionality to eliminate code duplication
across all FMP API tools.
"""

import os
import requests
from typing import Dict, Any, Optional

# Base URL for FMP API
FMP_API_BASE_URL = "https://financialmodelingprep.com/stable/"

def make_fmp_api_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a request to the FMP API with common error handling and authentication.
    
    Args:
        endpoint: The API endpoint (e.g., 'balance-sheet-statement', 'key-metrics')
        params: Dictionary of query parameters to include in the request
        
    Returns:
        JSON response data or error dictionary
    """
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        return {"error": "FMP_API_KEY environment variable not set"}
    
    # Build URL with endpoint and parameters
    url = f"{FMP_API_BASE_URL}/{endpoint}"
    
    # Add API key to parameters
    params_with_key = params.copy()
    params_with_key["apikey"] = api_key
    
    try:
        response = requests.get(url, params=params_with_key)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
