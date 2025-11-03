/**
 * Common utilities for run_sse API route
 *
 * This module contains shared types, request parsing, validation, and utility functions
 * used by both Agent Engine and local backend deployment strategies for the run_sse endpoint.
 */

import { NextRequest } from "next/server";

/**
 * Gets the ADK app name from environment or defaults
 */
function getAdkAppName(): string {
  return process.env.ADK_APP_NAME || "app";
}

/**
 * Common request data structure for streaming
 */
export interface ProcessedStreamRequest {
  message: string;
  userId: string;
  sessionId: string;
  stockSymbol?: string; // Extracted stock symbol from message
}

/**
 * Local backend payload format
 */
export interface LocalBackendPayload {
  appName: string;
  userId: string;
  sessionId: string;
  newMessage: {
    parts: { text: string }[];
    role: "user";
  };
  streaming: boolean;
}

/**
 * Backend payload type (now only local backend)
 */
export type BackendPayload = LocalBackendPayload;

/**
 * Validation result for request parsing
 */
export interface StreamValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * SSE response headers used by all deployment strategies
 */
export const SSE_HEADERS = {
  "Content-Type": "text/event-stream",
  "Cache-Control": "no-cache",
  Connection: "keep-alive",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
} as const;

/**
 * CORS headers for OPTIONS requests
 */
export const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
} as const;

/**
 * Extract stock symbol from user message
 * Simple pattern matching for common stock references
 */
function extractStockSymbol(message: string): string {
  // Common patterns for stock mentions
  const patterns = [
    /([A-Z]{1,5})\s+(?:종목|주식|주가|주)/,  // AAPL 종목, TSLA 주식
    /([A-Z]{1,5})\s+(?:을|를)\s+분석/,  // AAPL을 분석
    /([A-Z]{1,5})\s+(?:에\s+대해|에\s+대한)/,  // AAPL에 대해
    /([가-힣a-zA-Z]+)\s+(?:종목|주식|주가|주)/,  // 삼성전자 종목, Tesla 주식
    /([가-힣a-zA-Z]+)\s+(?:을|를)\s+분석/,  // 삼성전자를 분석
    /([가-힣a-zA-Z]+)\s+(?:에\s+대해|에\s+대한)/,  // 삼성전자에 대해
  ];

  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match) {
      let symbol = match[1].toLowerCase();
      // Clean up Korean company names
      symbol = symbol.replace(/[가-힣]/g, '');
      return symbol.trim() || "unknown";
    }
  }

  return "unknown";
}

/**
 * Parse and validate the incoming stream request body
 *
 * @param request - The incoming HTTP request
 * @returns Parsed request data and validation result
 */
export async function parseStreamRequest(request: NextRequest): Promise<{
  data: ProcessedStreamRequest | null;
  validation: StreamValidationResult;
}> {
  try {
    const requestBody = (await request.json()) as {
      message?: string;
      userId?: string;
      sessionId?: string;
    };

    // Validate the request structure
    const validation = validateStreamRequest(requestBody);
    if (!validation.isValid) {
      return { data: null, validation };
    }

    const message = requestBody.message!;

    return {
      data: {
        message,
        userId: requestBody.userId!,
        sessionId: requestBody.sessionId!,
      },
      validation: { isValid: true },
    };
  } catch (error) {
    console.error("Error parsing stream request:", error);
    return {
      data: null,
      validation: {
        isValid: false,
        error: "Invalid request format",
      },
    };
  }
}

/**
 * Validate the stream request structure
 *
 * @param requestBody - The parsed request body
 * @returns Validation result
 */
export function validateStreamRequest(requestBody: {
  message?: string;
  userId?: string;
  sessionId?: string;
}): StreamValidationResult {
  if (!requestBody.message?.trim()) {
    return {
      isValid: false,
      error: "Message is required",
    };
  }

  if (!requestBody.userId?.trim()) {
    return {
      isValid: false,
      error: "User ID is required",
    };
  }

  if (!requestBody.sessionId?.trim()) {
    return {
      isValid: false,
      error: "Session ID is required",
    };
  }

  return { isValid: true };
}

/**
 * Format local backend payload
 *
 * @param requestData - Processed request data
 * @returns Local backend formatted payload
 */
export function formatLocalBackendPayload(
  requestData: ProcessedStreamRequest
): LocalBackendPayload {
  return {
    appName: getAdkAppName(),
    userId: requestData.userId,
    sessionId: requestData.sessionId,
    newMessage: {
      parts: [{ text: requestData.message }],
      role: "user",
    },
    streaming: true,
  };
}

/**
 * Centralized logging for stream operations
 *
 * @param sessionId - Session identifier
 * @param userId - User identifier
 * @param message - Stream message (truncated for logging)
 * @param deploymentType - Deployment strategy type
 */
export function logStreamRequest(
  sessionId: string,
  userId: string,
  message: string,
  deploymentType: "local_backend"
): void {
  const truncatedMessage =
    message.length > 50 ? message.substring(0, 50) + "..." : message;
  console.log(
    `📨 Stream Request [${deploymentType}] - Session: ${sessionId}, User: ${userId}, Message: ${truncatedMessage}`
  );
}

/**
 * Log stream operation start
 *
 * @param url - Target URL for streaming
 * @param payload - Request payload (truncated for logging)
 * @param deploymentType - Deployment strategy type
 */
export function logStreamStart(
  url: string,
  payload: BackendPayload,
  deploymentType: "local_backend"
): void {
  console.log(`🔗 Forwarding to ${deploymentType}: ${url}`);
  console.log(`📤 Payload:`, payload);
}

/**
 * Log stream response details
 *
 * @param status - HTTP status code
 * @param statusText - HTTP status text
 * @param headers - Response headers
 * @param deploymentType - Deployment strategy type
 */
export function logStreamResponse(
  status: number,
  statusText: string,
  headers: Headers,
  deploymentType: "local_backend"
): void {
  console.log(
    `✅ ${deploymentType} response received, status: ${status} ${statusText}`
  );
  console.log(`📋 Content-Type: ${headers.get("content-type")}`);
}

/**
 * Create incremental SSE event for streaming text
 *
 * @param text - New text content to stream
 * @param author - Author/agent name
 * @returns Formatted SSE event string
 */
export function createIncrementalSSEEvent(
  text: string,
  author: string = "goal-planning-agent"
): string {
  const incrementalEvent = {
    content: { parts: [{ text }] },
    author,
    incremental: true, // Flag to indicate this is partial content
  };

  return `data: ${JSON.stringify(incrementalEvent)}\n\n`;
}

/**
 * Create final SSE event for complete JSON response
 *
 * @param completeJson - Complete JSON response from backend
 * @returns Formatted SSE event string
 */
export function createFinalSSEEvent(completeJson: unknown): string {
  return `data: ${JSON.stringify(completeJson)}\n\n`;
}

/**
 * Create error SSE event
 *
 * @param errorMessage - Error message to send
 * @param author - Author/agent name for the error
 * @returns Formatted SSE error event string
 */
export function createErrorSSEEvent(
  errorMessage: string,
  author: string = "error"
): string {
  const errorEvent = {
    content: {
      parts: [{ text: `Error processing response: ${errorMessage}` }],
    },
    author,
  };

  return `data: ${JSON.stringify(errorEvent)}\n\n`;
}

/**
 * Creates a debug log message with consistent formatting
 * Consolidated from stream-utils.ts
 *
 * @param category - Log category (e.g., "SSE", "PARSER", "CONNECTION")
 * @param message - Log message
 * @param data - Optional data to include
 */
export function createDebugLog(
  category: string,
  message: string,
  data?: unknown
): void {
  if (data !== undefined) {
    console.log(`[${category}] ${message}:`, data);
  } else {
    console.log(`[${category}] ${message}`);
  }
}
