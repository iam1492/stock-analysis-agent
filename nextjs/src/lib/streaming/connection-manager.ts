/**
 * Connection Manager
 *
 * This module handles SSE streaming connection lifecycle management including
 * connection establishment, data streaming, error handling, and cleanup.
 */

import { RefObject } from "react";
import {
  SSEConnectionState,
  StreamProcessingCallbacks,
  StreamingAPIPayload,
  ConnectionManagerOptions,
} from "./types";
import { processSseEventData } from "./stream-processor";
import { createDebugLog } from "@/lib/handlers/run-sse-common";

/**
 * Manages SSE streaming connections
 */
export class StreamingConnectionManager {
  private connectionState: SSEConnectionState = "idle";
  private retryFn: <T>(fn: () => Promise<T>) => Promise<T>;
  private endpoint: string;
  private abortController: AbortController | null = null;

  constructor(options: ConnectionManagerOptions = {}) {
    this.retryFn = options.retryFn || ((fn) => fn());
    this.endpoint = options.endpoint || "/api/run_sse";
  }

  /**
   * Gets the current connection state
   */
  public getConnectionState(): SSEConnectionState {
    return this.connectionState;
  }

  /**
   * Starts a streaming connection and processes SSE events in real-time
   *
   * @param apiPayload - API request payload
   * @param callbacks - Stream processing callbacks
   * @param accumulatedTextRef - Reference to accumulated text
   * @param currentAgentRef - Reference to current agent state
   * @param setCurrentAgent - Agent state setter
   * @param setIsLoading - Loading state setter
   * @returns Promise that resolves when streaming completes
   */
  public async submitMessage(
    apiPayload: StreamingAPIPayload,
    callbacks: StreamProcessingCallbacks,
    accumulatedTextRef: RefObject<string>,
    currentAgentRef: RefObject<string>,
    setCurrentAgent: (agent: string) => void,
    setIsLoading: (loading: boolean) => void,
    aiMessageId: string,
    onAnalysisComplete?: () => void
  ): Promise<void> {
    this.connectionState = "connecting";
    setIsLoading(true);
    accumulatedTextRef.current = "";
    currentAgentRef.current = "";
    this.abortController = new AbortController();

    try {
      createDebugLog(
        "CONNECTION",
        "Sending API request with payload",
        apiPayload
      );

      const response = await this.retryFn(() =>
        fetch(this.endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(apiPayload),
          signal: this.abortController?.signal,
        })
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      this.connectionState = "connected";

      // Handle SSE streaming with proper event processing
      await this.handleSSEStream(
        response,
        aiMessageId,
        callbacks,
        accumulatedTextRef,
        currentAgentRef,
        setCurrentAgent,
        onAnalysisComplete
      );

      this.connectionState = "idle";
      setIsLoading(false);
    } catch (error) {
      if ((error as Error).name === "AbortError") {
        this.connectionState = "closed";
        createDebugLog("CONNECTION", "Request was cancelled by the user");
      } else {
        this.connectionState = "error";
        createDebugLog("CONNECTION", "Streaming error", error);
      }

      // Don't create fake error messages - let the UI handle error states
      // The error will be propagated up to the calling code
      setIsLoading(false);
    } finally {
      this.abortController = null;
    }
  }

  /**
   * Cancels the current streaming connection
   *
   * @param accumulatedTextRef - Reference to accumulated text (for cleanup)
   * @param currentAgentRef - Reference to current agent state (for cleanup)
   * @param setCurrentAgent - Agent state setter (for cleanup)
   * @param setIsLoading - Loading state setter
   */
  public cancelRequest(
    accumulatedTextRef: RefObject<string>,
    currentAgentRef: RefObject<string>,
    setCurrentAgent: (agent: string) => void,
    setIsLoading: (loading: boolean) => void
  ): void {
    if (this.abortController) {
      this.abortController.abort();
    }
    this.connectionState = "closed";
    setIsLoading(false);

    // Clear any accumulated state
    accumulatedTextRef.current = "";
    currentAgentRef.current = "";
    setCurrentAgent("");
  }

  /**
   * Handle SSE streaming from both local backend and Agent Engine
   * Both backends now send standard SSE format (text/event-stream)
   *
   * @param response - Fetch response with SSE stream
   * @param aiMessageId - AI message ID for updates
   * @param callbacks - Stream processing callbacks
   * @param accumulatedTextRef - Reference to accumulated text
   * @param currentAgentRef - Reference to current agent state
   * @param setCurrentAgent - Agent state setter
   * @param onAnalysisComplete - Callback for when analysis is complete
   */
  private async handleSSEStream(
    response: Response,
    aiMessageId: string,
    callbacks: StreamProcessingCallbacks,
    accumulatedTextRef: RefObject<string>,
    currentAgentRef: RefObject<string>,
    setCurrentAgent: (agent: string) => void,
    onAnalysisComplete?: () => void
  ): Promise<void> {
    const contentType = response.headers.get("content-type") || "";

    createDebugLog(
      "ROUTING",
      `Content-Type: ${contentType} - Processing as SSE`
    );

    // Both local backend and Agent Engine now send standard SSE format
    // No content-type branching needed - unified SSE processing for all backends

    // Handle SSE streaming response from both backends
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("No readable stream available");
    }

    const decoder = new TextDecoder();
    let buffer = ""; // Changed from lineBuffer to buffer for event-based accumulation
    let eventCounter = 0;

    createDebugLog("SSE START", "Beginning to process streaming response");

    // Use recursive pump function instead of while(true) loop
    const pump = async (): Promise<void> => {
      const { done, value } = await reader.read();

      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        createDebugLog("SSE CHUNK", `Received ${chunk.length} bytes, total buffer: ${buffer.length}`);
      }

      // Process all complete SSE events in the buffer (separated by \n\n)
      let eventEndIndex;
      while (
        (eventEndIndex = buffer.indexOf("\n\n")) >= 0 ||
        (done && buffer.length > 0)
      ) {
        let eventData: string;
        if (eventEndIndex >= 0) {
          eventData = buffer.substring(0, eventEndIndex);
          buffer = buffer.substring(eventEndIndex + 2); // Remove the event + \n\n
        } else {
          // Only if done and buffer has content without trailing \n\n
          eventData = buffer;
          buffer = "";
        }

        createDebugLog("SSE EVENT", `Processing event data (${eventData.length} chars): "${eventData.substring(0, 200)}${eventData.length > 200 ? '...' : ''}"`);

        // Extract JSON data from the event (remove "data: " prefix if present)
        let jsonDataToParse = eventData;
        if (eventData.startsWith("data: ")) {
          jsonDataToParse = eventData.substring(6); // Remove "data: " prefix
        }

        // Skip empty events or comments
        if (jsonDataToParse.trim() === "" || jsonDataToParse.startsWith(":")) {
          createDebugLog("SSE SKIP", `Skipping empty/comment event: "${eventData}"`);
          continue;
        }

        eventCounter++;
        createDebugLog(
          "SSE DISPATCH EVENT",
          `Event #${eventCounter} - JSON length: ${jsonDataToParse.length}`
        );
        createDebugLog(
          "SSE DISPATCH EVENT",
          `Event #${eventCounter} JSON preview: ${jsonDataToParse.substring(0, 200)}...`
        );

        // Process the event immediately for real-time updates
        try {
          createDebugLog("SSE DISPATCH EVENT", `Event #${eventCounter} - About to call processSseEventData`);
          await processSseEventData(
            jsonDataToParse,
            aiMessageId,
            callbacks,
            accumulatedTextRef,
            currentAgentRef,
            setCurrentAgent,
            onAnalysisComplete
          );
          createDebugLog("SSE DISPATCH EVENT", `Event #${eventCounter} - processSseEventData completed successfully`);

          // 🔑 CRITICAL: Force immediate UI update by yielding to event loop
          // This prevents React from batching updates and ensures real-time streaming
          await new Promise((resolve) => setTimeout(resolve, 0));
          createDebugLog("SSE DISPATCH EVENT", `Event #${eventCounter} - UI update yielded`);
        } catch (error) {
          console.error(
            `❌ [SSE ERROR] Event #${eventCounter} - Failed to process SSE event:`,
            error
          );
          console.error(
            `❌ [SSE ERROR] Event #${eventCounter} - Problematic JSON:`,
            jsonDataToParse.substring(0, 500)
          );
          console.error(
            `❌ [SSE ERROR] Event #${eventCounter} - Full JSON:`,
            jsonDataToParse
          );
        }
        createDebugLog("SSE DISPATCH EVENT", `Event #${eventCounter} - Event processed, continuing...`);
      }

      if (done) {
        // Handle any remaining data in buffer (final incomplete event)
        if (buffer.length > 0) {
          createDebugLog("SSE FINAL BUFFER", `Processing remaining buffer (${buffer.length} chars): "${buffer.substring(0, 200)}${buffer.length > 200 ? '...' : ''}"`);

          // Extract JSON data from remaining buffer
          let jsonDataToParse = buffer;
          if (buffer.startsWith("data: ")) {
            jsonDataToParse = buffer.substring(6); // Remove "data: " prefix
          }

          // Skip empty or comment data
          if (jsonDataToParse.trim() !== "" && !jsonDataToParse.startsWith(":")) {
            eventCounter++;
            createDebugLog(
              "SSE DISPATCH FINAL EVENT",
              `Final Event #${eventCounter} - JSON length: ${jsonDataToParse.length}`
            );
            createDebugLog(
              "SSE DISPATCH FINAL EVENT",
              `Final Event #${eventCounter} JSON preview: ${jsonDataToParse.substring(0, 200)}...`
            );

            try {
              createDebugLog("SSE DISPATCH FINAL EVENT", `Final Event #${eventCounter} - About to call processSseEventData`);
              await processSseEventData(
                jsonDataToParse,
                aiMessageId,
                callbacks,
                accumulatedTextRef,
                currentAgentRef,
                setCurrentAgent,
                onAnalysisComplete
              );
              createDebugLog("SSE DISPATCH FINAL EVENT", `Final Event #${eventCounter} - processSseEventData completed successfully`);

              // 🔑 CRITICAL: Force immediate UI update by yielding to event loop
              // This prevents React from batching updates and ensures real-time streaming
              await new Promise((resolve) => setTimeout(resolve, 0));
              createDebugLog("SSE DISPATCH FINAL EVENT", `Final Event #${eventCounter} - UI update yielded`);
            } catch (error) {
              console.error(
                `❌ [SSE ERROR] Final Event #${eventCounter} - Failed to process final SSE event:`,
                error
              );
              console.error(
                `❌ [SSE ERROR] Final Event #${eventCounter} - Problematic JSON:`,
                jsonDataToParse.substring(0, 500)
              );
              console.error(
                `❌ [SSE ERROR] Final Event #${eventCounter} - Full JSON:`,
                jsonDataToParse
              );
            }
          }
          buffer = "";
          createDebugLog("SSE DISPATCH FINAL EVENT", `Final Event #${eventCounter} - Buffer cleared`);
        }
        createDebugLog("SSE END", `Stream processing finished - Total events processed: ${eventCounter}`);
        return; // Exit recursion
      }

      // Continue processing next chunk
      return pump();
    };

    try {
      await pump();
    } catch (error) {
      createDebugLog("SSE ERROR", "Error reading stream", error);
      throw error;
    }
  }

  // Removed Agent Engine JSON processing methods:
  // - handleAgentEngineJsonStream()
  // - processCompleteJsonLines()
  // - processAgentEngineJsonPart()
  // - hashPart()
  //
  // These are no longer needed since Agent Engine now sends standard SSE format
  // and uses the same processing pipeline as local backend.
}
