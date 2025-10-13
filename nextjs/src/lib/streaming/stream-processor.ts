/**
 * Stream Processor
 *
 * This module handles the processing of parsed SSE data into UI updates.
 * It coordinates message updates, event timeline updates, and website count updates
 * based on the parsed SSE data.
 *
 * Implements the Official ADK Termination Signal Pattern:
 * - Streaming chunks are accumulated and displayed progressively
 * - Complete responses are used as termination signals (not displayed)
 * - When complete response matches accumulated text, streaming stops
 */

import { flushSync } from "react-dom";
import { Message } from "@/types";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { StreamProcessingCallbacks } from "./types";
import { extractDataFromSSE } from "./sse-parser";
import { createDebugLog } from "../handlers/run-sse-common";

/**
 * Processes SSE event data and triggers appropriate callbacks
 *
 * This function takes raw JSON data, parses it using the SSE parser,
 * and then processes the results to trigger UI updates through callbacks.
 * Based on the working example's real-time streaming approach.
 *
 * @param jsonData - Raw SSE JSON data string
 * @param aiMessageId - ID of the AI message being streamed
 * @param callbacks - Callback functions for UI updates
 * @param accumulatedTextRef - Reference to accumulated text for message updates
 * @param currentAgentRef - Reference to current agent state
 * @param setCurrentAgent - State setter for current agent
 */
export async function processSseEventData(
  jsonData: string,
  aiMessageId: string,
  callbacks: StreamProcessingCallbacks,
  accumulatedTextRef: { current: string },
  currentAgentRef: { current: string },
  setCurrentAgent: (agent: string) => void
): Promise<void> {
  const { textParts, thoughtParts, agent, functionCall, functionResponse } =
    extractDataFromSSE(jsonData);

  // Show all agent activities in timeline, but only show hedge_fund_manager_agent text in UI
  const actualMessageId = aiMessageId;

  // Update current agent if changed
  if (agent && agent !== currentAgentRef.current) {
    currentAgentRef.current = agent;
    setCurrentAgent(agent);
  }

  // Process function calls (show all in timeline)
  if (functionCall) {
    processFunctionCall(functionCall, actualMessageId, callbacks.onEventUpdate);
  }

  // Process function responses (show all in timeline)
  if (functionResponse) {
    processFunctionResponse(
      functionResponse,
      actualMessageId,
      callbacks.onEventUpdate
    );
  }

  // Process AI thoughts (show all in timeline)
  console.log("🔍 [STREAM PROCESSOR] Checking for thoughts:", {
    thoughtPartsLength: thoughtParts.length,
    thoughtParts: thoughtParts.map((t) => t.substring(0, 50) + "..."),
    hasThoughts: thoughtParts.length > 0,
  });

  if (thoughtParts.length > 0) {
    console.log("🧠 [STREAM PROCESSOR] Processing thoughts:", {
      thoughtCount: thoughtParts.length,
      agent,
      messageId: actualMessageId,
    });

    processThoughts(
      thoughtParts,
      agent,
      actualMessageId,
      callbacks.onEventUpdate,
      callbacks.onMessageUpdate // Create AI message so timeline has somewhere to attach
    );
  } else {
    console.log("⚠️ [STREAM PROCESSOR] No thoughts to process");
  }

  // Process text content only for hedge_fund_manager_agent
  if (textParts.length > 0) {
    if (agent === "hedge_fund_manager_agent" || !agent) {
      await processTextContent(
        textParts,
        agent,
        actualMessageId,
        accumulatedTextRef,
        callbacks.onMessageUpdate
      );
    } else {
      console.log(`🚫 [STREAM PROCESSOR] Filtering out text content from agent: ${agent}`);
    }
  }
}

/**
 * Processes function call events
 *
 * @param functionCall - Function call data from parsed SSE
 * @param aiMessageId - AI message ID for timeline
 * @param onEventUpdate - Event update callback
 */
function processFunctionCall(
  functionCall: { name: string; args: Record<string, unknown>; id: string },
  aiMessageId: string,
  onEventUpdate: (messageId: string, event: ProcessedEvent) => void
): void {
  // Create user-friendly function call messages
  const friendlyFunctionNames: Record<string, string> = {
    'fmp_cash_flow_statement': '현금흐름 분석',
    'fmp_balance_sheet': '대차대조표 분석', 
    'fmp_income_statement': '손익계산서 분석',
    'fmp_financial_ratios': '재무 비율 분석',
    'fmp_key_metrics': '주요 지표 분석',
    'fmp_dcf_valuation': 'DCF 가치 평가',
    'fmp_enterprise_value': '기업 가치 분석',
    'fmp_owner_earnings': '주주 이익 분석',
    'fmp_economic_indicators': '경제 지표 분석',
    'fmp_stock_news': '뉴스 분석',
    'fmp_price_target_summary': '목표 주가 분석',
    'fmp_historical_stock_grade': '주식 등급 분석',
    'fmp_simple_moving_average': '이동평균선 분석',
    'fmp_relative_strength_index': 'RSI 분석',
    'fmp_standard_deviation': '변동성 분석'
  };

  const friendlyName = friendlyFunctionNames[functionCall.name] || functionCall.name;
  const functionCallTitle = `🔧 ${friendlyName} 도구 사용중...`;

  createDebugLog(
    "SSE HANDLER",
    "Adding Function Call timeline event:",
    functionCallTitle
  );

  onEventUpdate(aiMessageId, {
    title: functionCallTitle,
    data: {
      type: "functionCall",
      name: functionCall.name,
      friendlyName: friendlyName,
      args: functionCall.args,
      id: functionCall.id,
    },
  });
}

/**
 * Processes function response events
 *
 * @param functionResponse - Function response data from parsed SSE
 * @param aiMessageId - AI message ID for timeline
 * @param onEventUpdate - Event update callback
 */
function processFunctionResponse(
  functionResponse: {
    name: string;
    response: Record<string, unknown>;
    id: string;
  },
  aiMessageId: string,
  onEventUpdate: (messageId: string, event: ProcessedEvent) => void
): void {
  // Create user-friendly function response messages
  const friendlyFunctionNames: Record<string, string> = {
    'fmp_cash_flow_statement': '현금흐름 분석',
    'fmp_balance_sheet': '대차대조표 분석', 
    'fmp_income_statement': '손익계산서 분석',
    'fmp_financial_ratios': '재무 비율 분석',
    'fmp_key_metrics': '주요 지표 분석',
    'fmp_dcf_valuation': 'DCF 가치 평가',
    'fmp_enterprise_value': '기업 가치 분석',
    'fmp_owner_earnings': '주주 이익 분석',
    'fmp_economic_indicators': '경제 지표 분석',
    'fmp_stock_news': '뉴스 분석',
    'fmp_price_target_summary': '목표 주가 분석',
    'fmp_historical_stock_grade': '주식 등급 분석',
    'fmp_simple_moving_average': '이동평균선 분석',
    'fmp_relative_strength_index': 'RSI 분석',
    'fmp_standard_deviation': '변동성 분석'
  };

  const friendlyName = friendlyFunctionNames[functionResponse.name] || functionResponse.name;
  const functionResponseTitle = `✅ ${friendlyName} 도구 사용 완료`;

  createDebugLog(
    "SSE HANDLER",
    "Adding Function Response timeline event:",
    functionResponseTitle
  );

  onEventUpdate(aiMessageId, {
    title: functionResponseTitle,
    data: {
      type: "functionResponse",
      name: functionResponse.name,
      friendlyName: friendlyName,
      response: functionResponse.response,
      id: functionResponse.id,
    },
  });
}

/**
 * Parses a thought string and splits it into sections based on markdown headers
 *
 * @param thought - Raw thought content with **Header** sections
 * @returns Array of sections with title and content
 */
function parseThoughtSections(
  thought: string
): Array<{ title?: string; content: string }> {
  // Split by markdown headers (**Header**)
  const sections = thought.split(/(?=\*\*[^*]+\*\*)/);

  const parsedSections: Array<{ title?: string; content: string }> = [];

  for (const section of sections) {
    const trimmedSection = section.trim();
    if (!trimmedSection) continue;

    // Extract title from **Title** pattern
    const titleMatch = trimmedSection.match(/^\*\*([^*]+?)\*\*/);

    if (titleMatch) {
      const title = titleMatch[1].trim();
      // Get content after the title (remove the **Title** part)
      const content = trimmedSection.replace(/^\*\*[^*]+?\*\*\s*/, "").trim();

      parsedSections.push({
        title,
        content: content || trimmedSection, // Fallback to full section if no content
      });
    } else {
      // No title found, use entire section as content
      parsedSections.push({
        content: trimmedSection,
      });
    }
  }

  // If no sections were found, return the original content as one section
  if (parsedSections.length === 0) {
    parsedSections.push({ content: thought });
  }

  return parsedSections;
}

/**
 * Processes AI thought parts - creates separate activities for each distinct thought
 *
 * @param thoughtParts - Array of thought strings from parsed SSE
 * @param agent - Current agent name
 * @param aiMessageId - AI message ID for timeline
 * @param onEventUpdate - Event update callback
 */
function processThoughts(
  thoughtParts: string[],
  agent: string,
  aiMessageId: string,
  onEventUpdate: (messageId: string, event: ProcessedEvent) => void,
  onMessageUpdate?: (message: Message) => void
): void {
  createDebugLog(
    "SSE HANDLER",
    `Processing thought parts for agent: ${agent}`,
    { thoughts: thoughtParts }
  );

  // Create user-friendly agent names
  const friendlyAgentNames: Record<string, string> = {
    'balance_sheet_analyst': '대차대조표 분석가',
    'income_statement_analyst': '손익계산서 분석가', 
    'cash_flow_analyst': '현금흐름 분석가',
    'basic_financial_analyst': '기본 재무 분석가',
    'growth_analyst': '성장성 분석가',
    'intrinsic_value_analyst': '본질가치 분석가',
    'technical_analyst': '기술적 분석가',
    'stock_researcher': '주식 연구원',
    'macro_economy_analyst': '경제 분석가',
    'senior_financial_advisor': '선임 재무 연구원',
    'senior_quantitative_advisor': '선임 퀀트 분석가',
    'hedge_fund_manager': '헤지펀드 매니저',
    'goal_planning_agent': '목표 계획 에이전트'
  };

  const friendlyAgentName = friendlyAgentNames[agent] || agent;

  // Create AI message to enable timeline display - but preserve any existing content
  if (onMessageUpdate) {
    createDebugLog(
      "THOUGHT DEBUG",
      "🚀 Creating/updating AI message for thoughts",
      {
        aiMessageId,
        hasCallback: !!onMessageUpdate,
      }
    );

    // Create message for timeline attachment
    // NOTE: This will be updated by text content processing if text arrives
    flushSync(() => {
      onMessageUpdate({
        type: "ai",
        content: "", // Empty initially - will be updated by text processing
        id: aiMessageId,
        timestamp: new Date(),
      });
    });

    createDebugLog(
      "THOUGHT DEBUG",
      "✅ AI message created for timeline display"
    );
  } else {
    createDebugLog("THOUGHT DEBUG", "❌ No onMessageUpdate callback available");
  }

  // Process each thought and split by section headers for better organization
  thoughtParts.forEach((thought) => {
    createDebugLog("SSE HANDLER", "Processing individual thought:", {
      thought: thought.substring(0, 100) + "...",
      length: thought.length,
    });

    // Split thought into sections by headers (bold titles)
    const sections = parseThoughtSections(thought);

    // Create separate timeline activity for each section
    sections.forEach((section) => {
      flushSync(() => {
        onEventUpdate(aiMessageId, {
          title: section.title
            ? `🤔 ${friendlyAgentName}이(가) "${section.title}" 생각중...`
            : `🤔 ${friendlyAgentName}이(가) 생각중...`,
          data: { 
            type: "thinking", 
            content: section.content,
            agent: agent,
            friendlyAgentName: friendlyAgentName
          },
        });
      });
    });
  });
}

/**
 * Processes text content parts based on agent type (like working example)
 *
 * @param textParts - Array of text strings from parsed SSE
 * @param agent - Current agent name
 * @param aiMessageId - AI message ID
 * @param accumulatedTextRef - Reference to accumulated text
 * @param onMessageUpdate - Message update callback
 */
async function processTextContent(
  textParts: string[],
  agent: string,
  aiMessageId: string,
  accumulatedTextRef: { current: string },
  onMessageUpdate: (message: Message) => void
): Promise<void> {
  // Process each text chunk using OFFICIAL ADK TERMINATION SIGNAL PATTERN
  for (const text of textParts) {
    const currentAccumulated = accumulatedTextRef.current;

    // 🎯 OFFICIAL ADK TERMINATION SIGNAL PATTERN (matches Angular implementation):
    // if (newChunk == this.streamingTextMessage.text) { return; }
    if (text === currentAccumulated && currentAccumulated.length > 0) {
      // Official ADK pattern: this is the termination signal
      // But we still need to ensure the final message state is preserved
      createDebugLog(
        "STREAM PROCESSOR",
        "Received termination signal, ensuring final message state",
        {
          finalContentLength: currentAccumulated.length,
        }
      );

      // Make sure the final message is properly set in the UI
      const finalMessage: Message = {
        type: "ai",
        content: currentAccumulated.trim(),
        id: aiMessageId,
        timestamp: new Date(),
      };

      flushSync(() => {
        onMessageUpdate(finalMessage);
      });

      return;
    }

    // This is a streaming chunk - add it to accumulated text and display
    // Official ADK pattern: direct concatenation (no spaces between chunks)
    accumulatedTextRef.current += text; // Direct concatenation like official ADK

    const updatedMessage: Message = {
      type: "ai",
      content: accumulatedTextRef.current.trim(),
      id: aiMessageId,
      timestamp: new Date(),
    };

    // Force immediate update to prevent React batching
    flushSync(() => {
      onMessageUpdate(updatedMessage);
    });
  }
}
