/**
 * Agent Engine Handler for Run SSE API Route
 *
 * Handles requests for Agent Engine deployment configuration.
 * This handler processes streaming JSON fragments from Agent Engine and converts them to SSE format.
 * Note: Agent Engine returns JSON fragments (not standard SSE), so we parse and reformat them.
 */

import { getEndpointForPath, getAuthHeaders } from "@/lib/config";
import {
  ProcessedStreamRequest,
  formatAgentEnginePayload,
  logStreamStart,
  logStreamResponse,
  SSE_HEADERS,
} from "./run-sse-common";
import {
  createInternalServerError,
  createBackendConnectionError,
} from "./error-utils";




/**
 * Handle Agent Engine query request (non-streaming)
 *
 * @param requestData - Processed request data
 * @returns SSE Response with complete agent response
 */
export async function handleAgentEngineQueryRequest(
  requestData: ProcessedStreamRequest
): Promise<Response> {
  console.log(
    "🚀🚀🚀 [AGENT ENGINE] QUERY HANDLER STARTING 🚀🚀🚀"
  );
  console.log(
    `📊 [AGENT ENGINE] Request data:`,
    JSON.stringify(requestData, null, 2)
  );

  try {
    // Format payload for Agent Engine
    const agentEnginePayload = formatAgentEnginePayload(requestData);

    // Build Agent Engine URL with the query endpoint (non-streaming)
    const agentEngineUrl = getEndpointForPath("", "query");

    // Log operation start
    logStreamStart(agentEngineUrl, agentEnginePayload, "agent_engine");

    // Get authentication headers
    const authHeaders = await getAuthHeaders();

    // Forward request to Agent Engine query endpoint (non-streaming)
    const response = await fetch(agentEngineUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders,
      },
      body: JSON.stringify(agentEnginePayload),
    });

    // Log the response from Agent Engine
    logStreamResponse(
      response.status,
      response.statusText,
      response.headers,
      "agent_engine"
    );

    // Check for errors from Agent Engine
    if (!response.ok) {
      let errorDetails = `Agent Engine returned an error: ${response.status} ${response.statusText}`;
      try {
        const errorText = await response.text();
        console.error(`❌ Agent Engine error details:`, errorText);
        if (errorText) {
          errorDetails += `. ${errorText}`;
        }
      } catch (error) {
        // Response body might not be available or already consumed
        console.error(
          "An error occurred while trying to read the error response body from Agent Engine:",
          error
        );
      }
      return createBackendConnectionError(
        "agent_engine",
        response.status,
        response.statusText,
        errorDetails
      );
    }

    // Parse the complete response from Agent Engine
    let responseData;
    try {
      const responseText = await response.text();
      console.log("✅ [AGENT ENGINE] Received complete response:", responseText);
      responseData = JSON.parse(responseText);
    } catch (error) {
      console.error("❌ [AGENT ENGINE] Failed to parse response:", error);
      return createInternalServerError(
        "agent_engine",
        error,
        "Failed to parse Agent Engine response"
      );
    }

    // Create a simple SSE response with the complete data
    const stream = new ReadableStream({
      async start(controller) {
        try {
          // Send the complete response as a single SSE event
          const sseEvent = `data: ${JSON.stringify(responseData)}\n\n`;
          controller.enqueue(Buffer.from(sseEvent));
          
          console.log("✅ [AGENT ENGINE] Sent complete response as SSE event");
          controller.close();
        } catch (error) {
          console.error("❌ [AGENT ENGINE] Error sending response:", error);
          controller.error(error);
        }
      },
    });

    // Return SSE response with proper headers
    return new Response(stream, {
      status: 200,
      headers: SSE_HEADERS,
    });
  } catch (error) {
    console.error("❌ Agent Engine handler error:", error);

    if (error instanceof TypeError && error.message.includes("fetch")) {
      return createBackendConnectionError(
        "agent_engine",
        500,
        "Connection failed",
        "Failed to connect to Agent Engine"
      );
    }

    return createInternalServerError(
      "agent_engine",
      error,
      "Failed to process Agent Engine streaming request"
    );
  }
}
