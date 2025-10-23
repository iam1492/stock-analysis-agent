"use client";

import { useCallback, useEffect } from "react";
import { useStreaming } from "@/hooks/useStreaming";
import { useBackendHealth } from "@/hooks/useBackendHealth";
import { Message } from "@/types";
import { ProcessedEvent } from "@/components/ActivityTimeline";

interface StreamingManagerProps {
  userId: string;
  sessionId: string;
  onMessageUpdate: (message: Message) => void;
  onEventUpdate: (messageId: string, event: ProcessedEvent) => void;
  onWebsiteCountUpdate: (count: number) => void;
  onLoadingChange?: (isLoading: boolean) => void;
  onAnalysisComplete?: () => void;
}

export interface StreamingManagerReturn {
  isLoading: boolean;
  currentAgent: string;
  submitMessage: (message: string, model?: string) => Promise<void>;
}

/**
 * Streaming management component that coordinates SSE streaming
 * Uses the useStreaming hook for stream processing and useBackendHealth for retry logic
 */
export function useStreamingManager({
  userId,
  sessionId,
  onMessageUpdate,
  onEventUpdate,
  onWebsiteCountUpdate,
  onLoadingChange,
  onAnalysisComplete,
}: StreamingManagerProps): StreamingManagerReturn {
  const { retryWithBackoff } = useBackendHealth();

  const { isLoading, currentAgent, startStream } =
    useStreaming(retryWithBackoff);

  // Notify parent of loading state changes
  useEffect(() => {
    if (onLoadingChange) {
      onLoadingChange(isLoading);
    }
  }, [isLoading, onLoadingChange]);

  // Submit a message for streaming
  const submitMessage = useCallback(
    async (message: string, model?: string): Promise<void> => {
      if (!message.trim() || !userId || !sessionId) {
        throw new Error("Message, userId, and sessionId are required");
      }

      const apiPayload = {
        message: message.trim(),
        userId,
        sessionId,
        ...(model && { model }),
      };

      try {
        await startStream(
          apiPayload,
          onMessageUpdate,
          onEventUpdate,
          onWebsiteCountUpdate,
          onAnalysisComplete
        );
      } catch (error) {
        console.error("Streaming error:", error);
        throw error;
      }
    },
    [
      userId,
      sessionId,
      startStream,
      onMessageUpdate,
      onEventUpdate,
      onWebsiteCountUpdate,
      onAnalysisComplete,
    ]
  );

  return {
    isLoading,
    currentAgent,
    submitMessage,
  };
}
