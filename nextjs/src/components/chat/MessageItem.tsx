"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MarkdownRenderer, mdComponents } from "./MarkdownRenderer";
import {
  ProcessedEvent,
} from "@/components/ActivityTimeline";
import { Copy, CopyCheck, Loader2, Bot, User, Brain, Info, Code, FileText } from "lucide-react";
import { Message } from "@/types";
import { AgentResultButtons } from "./AgentResultButtons";

interface MessageItemProps {
  message: Message;
  messageEvents?: Map<string, ProcessedEvent[]>;
  isLoading?: boolean;
  onCopy?: (text: string, messageId: string) => void;
  copiedMessageId?: string | null;
  userId?: string;
  isAnalysisComplete?: boolean;
}

/**
 * Individual message component that handles both human and AI messages
 * with proper styling, copy functionality, and activity timeline
 */
export function MessageItem({
  message,
  messageEvents,
  isLoading = false,
  onCopy,
  copiedMessageId,
  isAnalysisComplete = false,
}: MessageItemProps) {
  const handleCopy = (text: string, messageId: string) => {
    if (onCopy) {
      onCopy(text, messageId);
    }
  };

  // Human message rendering
  if (message.type === "human") {
    return (
      <div className="flex items-start justify-end gap-3 max-w-[85%] ml-auto">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 rounded-2xl rounded-tr-sm shadow-lg border border-blue-400/20">
          <ReactMarkdown
            components={{
              ...mdComponents,
              // Override styles for human messages (white text)
              p: ({ children, ...props }) => (
                <p
                  className="mb-2 leading-relaxed text-white last:mb-0"
                  {...props}
                >
                  {children}
                </p>
              ),
              h1: ({ children, ...props }) => (
                <h1
                  className="text-xl font-bold mb-3 text-white leading-tight"
                  {...props}
                >
                  {children}
                </h1>
              ),
              h2: ({ children, ...props }) => (
                <h2
                  className="text-lg font-semibold mb-2 text-white leading-tight"
                  {...props}
                >
                  {children}
                </h2>
              ),
              h3: ({ children, ...props }) => (
                <h3
                  className="text-base font-medium mb-2 text-white leading-tight"
                  {...props}
                >
                  {children}
                </h3>
              ),
              code: ({ children, ...props }) => (
                <code
                  className="bg-blue-700/50 text-blue-100 px-1.5 py-0.5 rounded text-sm font-mono"
                  {...props}
                >
                  {children}
                </code>
              ),
              strong: ({ children, ...props }) => (
                <strong className="font-semibold text-white" {...props}>
                  {children}
                </strong>
              ),
            }}
            remarkPlugins={[remarkGfm]}
          >
            {message.content}
          </ReactMarkdown>
        </div>
        <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center shadow-md border border-blue-400/30">
          <User className="h-4 w-4 text-white" />
        </div>
      </div>
    );
  }

  // AI message rendering
  const hasTimelineEvents =
    messageEvents &&
    messageEvents.has(message.id) &&
    messageEvents.get(message.id)!.length > 0;



  // Render individual event bubbles instead of timeline container
  const renderEventBubbles = () => {
    if (!hasTimelineEvents) return null;
    
    const events = messageEvents.get(message.id) || [];
    
    return events.map((event, index) => {
      const isThinking = event.title.includes("생각중") || event.title.includes("Thinking") || event.title.startsWith("🤔");
      const isFunctionCall = event.title.includes("도구 사용중");
      const isFunctionResponse = event.title.includes("도구 사용 완료");
      
      let bubbleStyle = "bg-gradient-to-br from-gray-100 to-gray-200 border border-gray-300/50";
      let icon = <Info className="h-4 w-4" />;
      let iconBg = "bg-gray-400";

      if (isThinking) {
        bubbleStyle = "bg-gradient-to-br from-purple-100/50 to-purple-200/50 border border-purple-300/50";
        icon = <Brain className="h-4 w-4 text-purple-600" />;
        iconBg = "bg-purple-200";
      } else if (isFunctionCall) {
        bubbleStyle = "bg-gradient-to-br from-blue-100/50 to-blue-200/50 border border-blue-300/50";
        icon = <Code className="h-4 w-4 text-blue-600" />;
        iconBg = "bg-blue-200";
      } else if (isFunctionResponse) {
        bubbleStyle = "bg-gradient-to-br from-green-100/50 to-green-200/50 border border-green-300/50";
        icon = <FileText className="h-4 w-4 text-green-600" />;
        iconBg = "bg-green-200";
      }
      
      // Extract friendly name from event data if available
      const data = event.data as Record<string, unknown>;
      
      return (
        <div key={index} className="flex items-start gap-3 max-w-[90%] animate-in slide-in-from-bottom-2 duration-300">
          <div className={`flex-shrink-0 w-6 h-6 ${iconBg} rounded-full flex items-center justify-center`}>
            {icon}
          </div>
          <div className={`flex-1 ${bubbleStyle} rounded-2xl rounded-tl-sm p-3 shadow-lg`}>
            <div className="text-sm font-medium mb-1 text-gray-700">
              {event.title}
            </div>
            {/* Show additional context for function calls/responses */}
            {data && (data.type === 'functionCall' || data.type === 'functionResponse') && data.name && typeof data.name === 'string' && (
              <div className="text-xs text-gray-600 mb-2">
                {data.name}
              </div>
            )}
            {/* Show agent info for thoughts */}
            {data && data.type === 'thinking' && data.friendlyAgentName && typeof data.friendlyAgentName === 'string' && (
              <div className="text-xs text-gray-600 mb-2">
                {data.friendlyAgentName}
              </div>
            )}
            {/* Don't show detailed data for cleaner UI - just show the progress */}
            <div className="text-xs text-gray-500 italic">
              {isThinking && "분석 중..."}
              {isFunctionCall && "데이터 수집 중..."}
              {isFunctionResponse && "처리 완료"}
            </div>
          </div>
        </div>
      );
    });
  };

  // AI message with events - render as individual bubbles
  if (hasTimelineEvents) {
    return (
      <div className="space-y-3">
        {renderEventBubbles()}
        
        {/* Show content if it exists */}
        {message.content && (
          <div className="flex items-start gap-3 max-w-[90%]">
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-md border border-emerald-400/30">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="flex-1 bg-gradient-to-br from-cream-25 to-white border border-gray-200 rounded-2xl rounded-tl-sm p-4 shadow-lg relative group">
              <div className="prose prose-gray max-w-none">
                <MarkdownRenderer content={message.content} />
              </div>

              {/* Copy button */}
              {onCopy && (
                <button
                  onClick={() => handleCopy(message.content, message.id)}
                  className="absolute top-3 right-3 p-2 hover:bg-gray-100 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                  title="Copy message"
                >
                  {copiedMessageId === message.id ? (
                    <CopyCheck className="h-4 w-4 text-emerald-600" />
                  ) : (
                    <Copy className="h-4 w-4 text-gray-500 hover:text-gray-700" />
                  )}
                </button>
              )}

              {/* Agent Result Buttons */}
              <AgentResultButtons
                isAnalysisComplete={isAnalysisComplete}
                onCopy={onCopy ? (text) => onCopy(text, message.id) : undefined}
                copiedText={copiedMessageId === message.id ? message.content : undefined}
              />

              {/* Timestamp */}
              <div className="mt-3 pt-2 border-t border-gray-200">
                <span className="text-xs text-gray-500">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
        )}
        
        {/* Loading indicator when no content yet */}
        {!message.content && isLoading && (
          <div className="flex items-start gap-3 max-w-[90%] animate-in slide-in-from-bottom-2 duration-300">
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-md border border-emerald-400/30">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="flex items-center gap-2 bg-gray-100 border border-gray-200 rounded-lg px-3 py-2">
              <Loader2 className="h-4 w-4 animate-spin text-emerald-600" />
              <span className="text-sm text-gray-600">
                AI 전문 에이전트가 분석을 진행하고 있습니다.
              </span>
            </div>
          </div>
        )}
      </div>
    );
  }

  // AI message with no content and not loading
  if (!message.content) {
    return (
      <div className="flex items-start gap-3 max-w-[90%]">
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-md border border-emerald-400/30">
          <Bot className="h-4 w-4 text-white" />
        </div>
        <div className="flex items-center gap-2 bg-gray-100 border border-gray-200 rounded-lg px-3 py-2">
          <span className="text-sm text-gray-600">No content</span>
        </div>
      </div>
    );
  }

  // Regular AI message display with content
  return (
    <div className="flex items-start gap-3 max-w-[90%]">
      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-md border border-emerald-400/30">
        <Bot className="h-4 w-4 text-white" />
      </div>

      <div className="flex-1 bg-gradient-to-br from-cream-25 to-white border border-gray-200 rounded-2xl rounded-tl-sm p-4 shadow-lg relative group">
        {/* Message content */}
        <div className="prose max-w-none">
          <MarkdownRenderer content={message.content} />
        </div>

        {/* Copy button */}
        {onCopy && (
          <button
            onClick={() => handleCopy(message.content, message.id)}
            className="absolute top-3 right-3 p-2 hover:bg-gray-100 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
            title="Copy message"
          >
            {copiedMessageId === message.id ? (
              <CopyCheck className="h-4 w-4 text-emerald-600" />
            ) : (
              <Copy className="h-4 w-4 text-gray-500 hover:text-gray-700" />
            )}
          </button>
        )}

        {/* Timestamp */}
        <div className="mt-3 pt-2 border-t border-gray-200">
          <span className="text-xs text-gray-500">
            {message.timestamp.toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
}
