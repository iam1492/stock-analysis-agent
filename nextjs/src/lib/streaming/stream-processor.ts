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

// Global callback for saving agent results to memory
let saveAgentResultCallback: ((agentName: string, content: string) => void) | null = null;

export function setAgentResultSaveCallback(callback: (agentName: string, content: string) => void) {
  saveAgentResultCallback = callback;
  console.log(`🔄 Set agent result save callback`);
}

async function saveAgentResultFromStream(agentName: string, content: string) {
  if (saveAgentResultCallback) {
    console.log(`💾 [STREAM PROCESSOR] Saving ${agentName} result to memory`);
    saveAgentResultCallback(agentName, content);
  } else {
    console.log(`⚠️ Cannot save ${agentName} result - no save callback set`);
  }
}

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
  setCurrentAgent: (agent: string) => void,
  onAnalysisComplete?: () => void
): Promise<void> {
  console.log("🔄 [STREAM PROCESSOR] processSseEventData called with JSON length:", jsonData.length);
  console.log("🔄 [STREAM PROCESSOR] JSON preview:", jsonData.substring(0, 200) + "...");

  const parsed = JSON.parse(jsonData);
  const { textParts, thoughtParts, agent, functionCall, functionResponse } =
    extractDataFromSSE(jsonData);

  console.log("🔄 [STREAM PROCESSOR] Parsed data:", {
    textPartsCount: textParts.length,
    thoughtPartsCount: thoughtParts.length,
    agent,
    hasFunctionCall: !!functionCall,
    hasFunctionResponse: !!functionResponse,
    aiMessageId
  });

  // Show all agent activities in timeline, but only show hedge_fund_manager_agent text in UI
  const actualMessageId = aiMessageId;

  // Update current agent if changed
  if (agent && agent !== currentAgentRef.current) {
    currentAgentRef.current = agent;
    setCurrentAgent(agent);
  }

  // Process function calls (show all in timeline)
  if (functionCall) {
    console.log("🔧 [STREAM PROCESSOR] Processing function call:", functionCall);
    processFunctionCall(functionCall, actualMessageId, callbacks.onEventUpdate);
    console.log("✅ [STREAM PROCESSOR] Function call processed");
  }

  // Process function responses (show all in timeline)
  if (functionResponse) {
    console.log("🔧 [STREAM PROCESSOR] Processing function response:", functionResponse);
    processFunctionResponse(
      functionResponse,
      actualMessageId,
      callbacks.onEventUpdate
    );
    console.log("✅ [STREAM PROCESSOR] Function response processed");
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
    console.log("✅ [STREAM PROCESSOR] Thoughts processed");
  } else {
    console.log("⚠️ [STREAM PROCESSOR] No thoughts to process");
  }

  // Process text content only for hedge_fund_manager_agent
  if (textParts.length > 0) {
    console.log("📝 [STREAM PROCESSOR] Processing text content:", {
      textPartsCount: textParts.length,
      agent,
      isHedgeFundManager: agent === "hedge_fund_manager_agent",
      textPreview: textParts.join("").substring(0, 100) + "..."
    });

    // Check if this is a chunked text (has chunkInfo)
    const content = (parsed as Record<string, unknown>).content;
    const hasChunkInfo = content &&
      typeof content === 'object' &&
      content !== null &&
      'parts' in content &&
      Array.isArray((content as { parts?: unknown[] }).parts) &&
      (content as { parts?: unknown[] }).parts?.some((part: unknown) =>
        typeof part === 'object' && part !== null && 'chunkInfo' in part
      );
    if (hasChunkInfo) {
      console.log("📦 [STREAM PROCESSOR] Detected chunked text content, processing chunks");
      await processChunkedTextContent(
        parsed,
        agent,
        actualMessageId,
        accumulatedTextRef,
        callbacks.onMessageUpdate,
        onAnalysisComplete
      );
    } else if (agent === "hedge_fund_manager_agent" || !agent) {
      console.log("📝 [STREAM PROCESSOR] Processing text for hedge_fund_manager_agent");
      await processTextContent(
        textParts,
        agent,
        actualMessageId,
        accumulatedTextRef,
        callbacks.onMessageUpdate,
        onAnalysisComplete
      );
      console.log("✅ [STREAM PROCESSOR] Text content processed for hedge_fund_manager_agent");
    } else {
      // Save results for other agents
      console.log(`💾 [STREAM PROCESSOR] Saving result for agent: ${agent}`);
      await saveAgentResultFromStream(agent, textParts.join(""));
      console.log(`💾 [STREAM PROCESSOR] Saved result for agent: ${agent}`);

      // Check if this is senior_financial_advisor_agent or senior_quantitative_advisor completing
      if ((agent === "senior_financial_advisor_agent" || agent === "senior_quantitative_advisor_agent") && onAnalysisComplete) {
        console.log(`🎯 [STREAM PROCESSOR] ${agent} analysis completed - triggering completion callback`);
        // Use setTimeout to ensure UI updates are processed first
        setTimeout(() => onAnalysisComplete(), 100);
      }
    }
  } else {
    console.log("⚠️ [STREAM PROCESSOR] No text content to process");
  }

  console.log("🎉 [STREAM PROCESSOR] processSseEventData completed successfully");
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
    'fmt_stock_news': '뉴스 분석',
    'fmp_price_target_summary': '목표 주가 분석',
    'fmp_price_target_news': '목표 주가 뉴스 분석',
    'fmp_historical_stock_grade': '주식 등급 분석',
    'fmp_simple_moving_average_long_term_trend': '장기 이동평균선 분석',
    'fmp_simple_moving_average_mid_term_trend': '중기 이동평균선 분석',
    'fmp_relative_strength_index': 'RSI 분석',
    'fmp_standard_deviation': '변동성 분석',
    'fmp_balance_sheet_statement_growth': '대차대조표 성장 분석',
    'fmp_cash_flow_statement_growth': '현금흐름 성장 분석',
    'fmp_income_statement_growth': '손익계산서 성장 분석',
    'fmp_key_metrics_ttm':'12개월 핵심 지표 분석',
    'fmp_analyst_estimates':'애널리스트 미래 실적 추정치 분석',
    'fmp_average_directional_index':'추세 강도 데이터 분석',

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
    'fmt_stock_news': '뉴스 분석',
    'fmp_price_target_summary': '목표 주가 분석',
    'fmp_price_target_news': '목표 주가 뉴스 분석',
    'fmp_historical_stock_grade': '주식 등급 분석',
    'fmp_simple_moving_average_long_term_trend': '장기 이동평균선 분석',
    'fmp_simple_moving_average_mid_term_trend': '중기 이동평균선 분석',
    'fmp_relative_strength_index': 'RSI 분석',
    'fmp_standard_deviation': '변동성 분석',
    'fmp_balance_sheet_statement_growth': '대차대조표 성장 분석',
    'fmp_cash_flow_statement_growth': '현금흐름 성장 분석',
    'fmp_income_statement_growth': '손익계산서 성장 분석',
    'fmp_key_metrics_ttm':'12개월 핵심 지표 분석',
    'fmp_analyst_estimates':'애널리스트 미래 실적 추정치 분석',
    'fmp_average_directional_index':'추세 강도 데이터 분석',
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
    'project_manager_agent': '프로젝트 매니저',
    'balance_sheet_agent': '대차대조표 분석가',
    'income_statement_agent': '손익계산서 분석가', 
    'cash_flow_statement_agent': '현금흐름 분석가',
    'basic_financial_analyst_agent': '기본 재무 분석가',
    'growth_analyst_agent': '기업 성장 분석가',
    'intrinsic_value_analyst_agent': '내제가치 분석가',
    'technical_analyst_agent': '기술적 분석가',
    'stock_researcher_agent': '기본 종목 분석 연구원',
    'macro_economy_analyst_agent': '매크로 경제 분석가',
    'senior_financial_advisor_agent': '선임 재무 연구원',
    'senior_quantitative_advisor_agent': '선임 퀀트 분석가',
    'hedge_fund_manager_agent': '헤지펀드 매니저',
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
            ? `🤔 ${friendlyAgentName} "${section.title}" 생각중...`
            : `🤔 ${friendlyAgentName} 생각중...`,
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
 * Processes chunked text content parts (split by backend due to size limits)
 *
 * @param parsed - Raw parsed SSE data
 * @param agent - Current agent name
 * @param aiMessageId - AI message ID
 * @param accumulatedTextRef - Reference to accumulated text
 * @param onMessageUpdate - Message update callback
 * @param onAnalysisComplete - Analysis completion callback
 */
async function processChunkedTextContent(
  parsed: Record<string, unknown>,
  agent: string,
  aiMessageId: string,
  accumulatedTextRef: { current: string },
  onMessageUpdate: (message: Message) => void,
  onAnalysisComplete?: () => void
): Promise<void> {
  const content = parsed.content as { parts?: unknown[] };
  if (!content?.parts) return;

  // Collect all text chunks and sort by chunk index
  const textChunks: Array<{ text: string; chunkInfo: Record<string, unknown> }> = [];
  let isComplete = false;

  for (const part of content.parts) {
    const partObj = part as { text?: string; chunkInfo?: Record<string, unknown> };
    if (partObj.text && partObj.chunkInfo) {
      textChunks.push({ text: partObj.text, chunkInfo: partObj.chunkInfo });
      if (partObj.chunkInfo.isLast) {
        isComplete = true;
      }
    }
  }

  // Sort chunks by index to ensure correct order
  textChunks.sort((a, b) => (a.chunkInfo.index as number) - (b.chunkInfo.index as number));

  // Combine all chunks into final text
  const finalText = textChunks.map(chunk => chunk.text).join('');

  console.log(`📦 [STREAM PROCESSOR] Processed ${textChunks.length} chunks, total length: ${finalText.length}, isComplete: ${isComplete}`);

  // Update accumulated text
  accumulatedTextRef.current = finalText;

  const updatedMessage: Message = {
    type: "ai",
    content: finalText.trim(),
    id: aiMessageId,
    timestamp: new Date(),
  };

  // Force immediate update
  flushSync(() => {
    onMessageUpdate(updatedMessage);
  });

  // Check if this is hedge_fund_manager_agent completing
  if (isComplete && agent === "hedge_fund_manager_agent" && onAnalysisComplete) {
    console.log("🎯 [STREAM PROCESSOR] Chunked hedge fund manager analysis completed - triggering completion callback");
    // Use setTimeout to ensure UI updates are processed first
    setTimeout(() => onAnalysisComplete(), 100);
  }
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
  onMessageUpdate: (message: Message) => void,
  onAnalysisComplete?: () => void
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

      // Check if this is hedge_fund_manager_agent completing - signal analysis complete
      if (agent === "hedge_fund_manager_agent" && onAnalysisComplete) {
        console.log("🎯 [STREAM PROCESSOR] Hedge fund manager analysis completed - triggering completion callback");
        // Use setTimeout to ensure UI updates are processed first
        setTimeout(() => onAnalysisComplete(), 100);
      }

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
