"use client";

import React, {
  createContext,
  useContext,
  useRef,
  useCallback,
  useEffect,
  useState,
} from "react";

import { useSession } from "@/hooks/useSession";
import { useMessages } from "@/hooks/useMessages";
import { useStreamingManager } from "@/components/chat/StreamingManager";
import { Message } from "@/types";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { toast } from "sonner";
import { loadSessionHistoryAction } from "@/lib/actions/session-history-actions";
import { setAgentResultSaveCallback } from "@/lib/streaming/stream-processor";

// Context value interface - consolidates all chat state and actions
export interface ChatContextValue {
  // Session state
  userId: string;
  sessionId: string;

  // Model state
  selectedModel: string;
  setSelectedModel: (model: string) => void;

  // Message state
  messages: Message[];
  messageEvents: Map<string, ProcessedEvent[]>;
  websiteCount: number;

  // Loading state
  isLoading: boolean;
  isLoadingHistory: boolean; // New loading state for session history
  currentAgent: string;
  isAnalysisComplete: boolean;

  // Agent results storage
  agentResults: Record<string, string>;
  saveAgentResult: (agentName: string, content: string) => void;
  getAgentResult: (agentName: string) => string | undefined;

  // Session actions
  handleUserIdChange: (newUserId: string) => void;
  handleUserIdConfirm: (confirmedUserId: string) => void;
  handleCreateNewSession: (sessionUserId: string) => Promise<void>;
  handleSessionSwitch: (newSessionId: string) => void;

  // Message actions
  handleSubmit: (
    query: string,
    requestUserId?: string,
    requestSessionId?: string
  ) => Promise<void>;
  addMessage: (message: Message) => void;

  // Refs for external access
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
}

interface ChatProviderProps {
  children: React.ReactNode;
}

// Create context
const ChatContext = createContext<ChatContextValue | null>(null);

/**
 * ChatProvider - Consolidated context provider for all chat state management
 * Combines useSession, useMessages, and useStreamingManager into single provider
 */
export function ChatProvider({
  children,
}: ChatProviderProps): React.JSX.Element {
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);

  // Session history loading state
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Model selection state with localStorage persistence
  const [selectedModel, setSelectedModelState] = useState<string>("gemini-2.5-flash");

  // Helper functions for localStorage management
  const getModelKey = useCallback(() => {
    return `selectedModel`;
  }, []);

  const saveModelToStorage = useCallback((model: string) => {
    try {
      const key = getModelKey();
      localStorage.setItem(key, model);
      console.log(`💾 [CHAT_PROVIDER] Saved selected model to localStorage: ${model}`);
    } catch (error) {
      console.error('Failed to save model to localStorage:', error);
    }
  }, [getModelKey]);

  const loadModelFromStorage = useCallback((): string => {
    try {
      const key = getModelKey();
      const stored = localStorage.getItem(key);
      if (stored) {
        console.log(`📂 [CHAT_PROVIDER] Loaded selected model from localStorage: ${stored}`);
        return stored;
      }
    } catch (error) {
      console.error('Failed to load model from localStorage:', error);
    }
    return "gemini-2.5-flash"; // default
  }, [getModelKey]);

  // Model setter with persistence
  const setSelectedModel = useCallback((model: string) => {
    setSelectedModelState(model);
    saveModelToStorage(model);
  }, [saveModelToStorage]);

  // Load saved model on mount
  useEffect(() => {
    const savedModel = loadModelFromStorage();
    setSelectedModelState(savedModel);
  }, [loadModelFromStorage]);

  // Consolidate all hooks
  const {
    userId,
    sessionId,
    handleUserIdChange,
    handleUserIdConfirm,
    handleCreateNewSession,
    handleSessionSwitch,
  } = useSession();

  const {
    messages,
    messageEvents,
    websiteCount,
    addMessage,
    setMessages,
    setMessageEvents,
    updateWebsiteCount,
  } = useMessages();

  // Analysis completion state
  const [isAnalysisComplete, setIsAnalysisComplete] = useState(false);

  // Agent results storage (in-memory)
  const [agentResults, setAgentResults] = useState<Record<string, string>>({});

  // Helper functions for localStorage management
  const getAgentResultsKey = useCallback((userId: string, sessionId: string) => {
    return `agentResults_${userId}_${sessionId}`;
  }, []);

  const saveAgentResultsToStorage = useCallback((userId: string, sessionId: string, results: Record<string, string>) => {
    try {
      const key = getAgentResultsKey(userId, sessionId);
      localStorage.setItem(key, JSON.stringify(results));
      console.log(`💾 [CHAT_PROVIDER] Saved agent results to localStorage: ${key}`);
    } catch (error) {
      console.error('Failed to save agent results to localStorage:', error);
    }
  }, [getAgentResultsKey]);

  const loadAgentResultsFromStorage = useCallback((userId: string, sessionId: string): Record<string, string> => {
    try {
      const key = getAgentResultsKey(userId, sessionId);
      const stored = localStorage.getItem(key);
      if (stored) {
        const results = JSON.parse(stored);
        console.log(`📂 [CHAT_PROVIDER] Loaded agent results from localStorage: ${key}`);
        return results;
      }
    } catch (error) {
      console.error('Failed to load agent results from localStorage:', error);
    }
    return {};
  }, [getAgentResultsKey]);

  // Agent result management functions
  const saveAgentResult = useCallback((agentName: string, content: string) => {
    console.log(`💾 [CHAT_PROVIDER] Saving ${agentName} result to memory`);
    setAgentResults(prev => {
      const newResults = {
        ...prev,
        [agentName]: content
      };
      // Save to localStorage when results are updated
      if (userId && sessionId) {
        saveAgentResultsToStorage(userId, sessionId, newResults);
      }
      return newResults;
    });
  }, [userId, sessionId, saveAgentResultsToStorage]);

  const getAgentResult = useCallback((agentName: string) => {
    return agentResults[agentName];
  }, [agentResults]);

  // Set up the save callback for stream processor
  useEffect(() => {
    setAgentResultSaveCallback(saveAgentResult);
    return () => {
      setAgentResultSaveCallback(() => {});
    };
  }, [saveAgentResult]);

  // Streaming management
  const streamingManager = useStreamingManager({
    userId,
    sessionId,
    onMessageUpdate: (message: Message) => {
      console.log("🔄 [CHAT_PROVIDER] onMessageUpdate called:", {
        messageId: message.id,
        messageType: message.type,
        contentLength: message.content.length,
        hasContent: !!message.content,
      });

      setMessages((prev) => {
        const existingMessage = prev.find((msg) => msg.id === message.id);
        console.log("🔍 [CHAT_PROVIDER] Message state check:", {
          messageId: message.id,
          existingMessage: !!existingMessage,
          totalMessages: prev.length,
          lastMessageType:
            prev.length > 0 ? prev[prev.length - 1].type : "none",
        });

        if (existingMessage) {
          // Update existing message while preserving any additional data
          console.log("🔄 [CHAT_PROVIDER] Updating existing message");
          return prev.map((msg) =>
            msg.id === message.id
              ? {
                  ...existingMessage, // Keep existing data
                  ...message, // Update with new content
                }
              : msg
          );
        } else {
          // Create new message with proper initial state
          const newMessage: Message = {
            ...message,
            timestamp: message.timestamp || new Date(),
          };
          console.log("✅ [CHAT_PROVIDER] Creating new message:", {
            id: newMessage.id,
            type: newMessage.type,
            contentLength: newMessage.content.length,
          });
          const newMessages = [...prev, newMessage];
          console.log("📊 [CHAT_PROVIDER] Updated messages array:", {
            totalMessages: newMessages.length,
            lastMessageType: newMessages[newMessages.length - 1].type,
          });
          return newMessages;
        }
      });
    },
    onEventUpdate: (messageId, event) => {
      console.log("📅 [CHAT_PROVIDER] onEventUpdate called:", {
        messageId,
        eventTitle: event.title,
        eventType:
          typeof event.data === "object" && event.data && "type" in event.data
            ? event.data.type
            : undefined,
        isThought: event.title.startsWith("🤔"),
      });

      setMessageEvents((prev) => {
        const newMap = new Map(prev);
        const existingEvents = newMap.get(messageId) || [];
        console.log("🔍 [CHAT_PROVIDER] Event state check:", {
          messageId,
          existingEventsCount: existingEvents.length,
          eventTitle: event.title,
        });

        // Handle thinking activities with progressive content accumulation
        if (event.title.startsWith("🤔")) {
          const existingThinkingIndex = existingEvents.findIndex(
            (existingEvent) => existingEvent.title === event.title
          );

          if (existingThinkingIndex >= 0) {
            // Accumulate content progressively instead of replacing
            const updatedEvents = [...existingEvents];
            const existingEvent = updatedEvents[existingThinkingIndex];
            const existingData =
              existingEvent.data && typeof existingEvent.data === "object"
                ? existingEvent.data
                : {};
            const existingContent =
              "content" in existingData ? String(existingData.content) : "";
            const newContent =
              event.data &&
              typeof event.data === "object" &&
              "content" in event.data
                ? String(event.data.content)
                : "";

            // Accumulate content (don't replace - add new content)
            const accumulatedContent = existingContent
              ? `${existingContent}\n\n${newContent}`
              : newContent;

            updatedEvents[existingThinkingIndex] = {
              ...existingEvent,
              data: {
                ...existingData,
                content: accumulatedContent,
              },
            };
            newMap.set(messageId, updatedEvents);
          } else {
            // Add new thinking activity (each distinct thought title)
            newMap.set(messageId, [...existingEvents, event]);
          }
        } else {
          // For non-thinking activities, add normally (no deduplication needed)
          newMap.set(messageId, [...existingEvents, event]);
        }

        return newMap;
      });
    },
    onWebsiteCountUpdate: updateWebsiteCount,
    onAnalysisComplete: () => {
      console.log("🎯 [CHAT_PROVIDER] Analysis completed - showing agent result buttons");
      setIsAnalysisComplete(true);
    },
  });

  // Load session history when session changes
  useEffect(() => {
    if (userId && sessionId) {
      // Function to load session history
      const loadSessionHistory = async () => {
        try {
          console.log("🔄 [CHAT_PROVIDER] Loading session history:", {
            userId,
            sessionId,
          });

          setIsLoadingHistory(true);

          // Clear current state
          setMessages([]);
          setMessageEvents(new Map());
          updateWebsiteCount(0);

          // Clear agent results and analysis state for new session
          setAgentResults({});
          setIsAnalysisComplete(false);

          // Load agent results from localStorage for this session
          const storedAgentResults = loadAgentResultsFromStorage(userId, sessionId);
          if (Object.keys(storedAgentResults).length > 0) {
            setAgentResults(storedAgentResults);
            // If we have stored results, assume analysis was complete
            setIsAnalysisComplete(true);
            console.log("✅ [CHAT_PROVIDER] Loaded agent results from localStorage");
          }

          // Load session history using Server Action (keeps Google Auth on server)
          const result = await loadSessionHistoryAction(userId, sessionId);

          if (result.success) {
            console.log(
              "✅ [CHAT_PROVIDER] Session history loaded successfully:",
              {
                messagesCount: result.messages.length,
                eventsCount: result.messageEvents.size,
              }
            );

            // Set historical messages
            if (result.messages.length > 0) {
              setMessages(result.messages);
            }

            // Set timeline events
            if (result.messageEvents.size > 0) {
              setMessageEvents(result.messageEvents);
            }

            console.log("✅ [CHAT_PROVIDER] Session history applied to state");
          } else {
            console.warn(
              "⚠️ [CHAT_PROVIDER] Session history loading failed:",
              result.error
            );

            // Show error toast to user
            toast.error("Failed to load chat history", {
              description:
                result.error ||
                "Could not load previous messages for this session.",
            });
          }
        } catch (error) {
          console.error(
            "❌ [CHAT_PROVIDER] Error loading session history:",
            error
          );

          // Show error toast to user
          toast.error("Network error", {
            description:
              "Could not connect to load chat history. Please check your connection.",
          });

          // On error, just clear state and continue (graceful degradation)
          setMessages([]);
          setMessageEvents(new Map());
          updateWebsiteCount(0);
          setAgentResults({});
          setIsAnalysisComplete(false);
        } finally {
          setIsLoadingHistory(false);
        }
      };

      // Load session history
      loadSessionHistory();
    }
  }, [userId, sessionId, setMessages, setMessageEvents, updateWebsiteCount, loadAgentResultsFromStorage]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messages]);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messageEvents]);

  // Extract stock symbol from query
  const extractStockSymbol = useCallback((query: string): string => {
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
      const match = query.match(pattern);
      if (match) {
        let symbol = match[1].toLowerCase();
        // Clean up Korean company names
        symbol = symbol.replace(/[가-힣]/g, '');
        return symbol.trim() || "unknown";
      }
    }

    return "unknown";
  }, []);

  // Handle message submission
  const handleSubmit = useCallback(
    async (
      query: string,
      requestUserId?: string,
      requestSessionId?: string
    ): Promise<void> => {
      if (!query.trim()) return;

      // Use provided userId or current state
      const currentUserId = requestUserId || userId;
      if (!currentUserId) {
        throw new Error("User ID is required to send messages");
      }

      try {
        // Use provided session ID or current state
        const currentSessionId = requestSessionId || sessionId;

        if (!currentSessionId) {
          throw new Error(
            "No session available. Please create a session first."
          );
        }

        // Extract stock symbol from query
        const stockSymbol = extractStockSymbol(query);

        // Agent result context is now handled by the save callback
        console.log(`🔄 [CHAT_PROVIDER] Starting analysis for ${stockSymbol} with model ${selectedModel}`);

        // Reset analysis complete state for new analysis
        setIsAnalysisComplete(false);

        // Clear agent results for new analysis
        setAgentResults({});

        // Add user message to chat immediately
        const userMessage: Message = {
          type: "human",
          content: query,
          id: `user-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
          timestamp: new Date(),
        };
        addMessage(userMessage);

        // Submit message for streaming with selected model - the backend will provide AI response
        await streamingManager.submitMessage(query, selectedModel);
      } catch (error) {
        console.error("Error submitting message:", error);
        // Don't create fake error messages - let the UI handle the error state
        throw error;
      }
    },
    [userId, sessionId, selectedModel, addMessage, streamingManager, extractStockSymbol]
  );

  // Context value
  const contextValue: ChatContextValue = {
    // Session state
    userId,
    sessionId,

    // Model state
    selectedModel,
    setSelectedModel,

    // Message state
    messages,
    messageEvents,
    websiteCount,

    // Loading state
    isLoading: streamingManager.isLoading,
    isLoadingHistory,
    currentAgent: streamingManager.currentAgent,
    isAnalysisComplete,

    // Agent results storage
    agentResults,
    saveAgentResult,
    getAgentResult,

    // Session actions
    handleUserIdChange,
    handleUserIdConfirm,
    handleCreateNewSession,
    handleSessionSwitch,

    // Message actions
    handleSubmit,
    addMessage,

    // Refs
    scrollAreaRef,
  };

  return (
    <ChatContext.Provider value={contextValue}>{children}</ChatContext.Provider>
  );
}

/**
 * Custom hook for consuming chat context
 * Provides error handling when used outside provider
 */
export function useChatContext(): ChatContextValue {
  const context = useContext(ChatContext);

  if (!context) {
    throw new Error(
      "useChatContext must be used within a ChatProvider. " +
        "Make sure your component is wrapped with <ChatProvider>."
    );
  }

  return context;
}
