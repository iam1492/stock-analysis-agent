"use client";

import { Bot } from "lucide-react";
import { UserIdInput } from "@/components/chat/UserIdInput";
import { SessionSelector } from "@/components/chat/SessionSelector";
import { ModelSelector } from "@/components/chat/ModelSelector";
import { useChatContext } from "@/components/chat/ChatProvider";

/**
 * ChatHeader - User and session management interface
 * Extracted from ChatMessagesView header section
 * Handles user ID input and session selection
 */
export function ChatHeader(): React.JSX.Element {
  const {
    userId,
    sessionId,
    handleUserIdChange,
    handleUserIdConfirm,
    handleSessionSwitch,
    handleCreateNewSession,
  } = useChatContext();

  return (
    <div className="relative z-20 flex-shrink-0 border-b border-gray-200 bg-cream-25/80 backdrop-blur-sm shadow-[0_4px_8px_-2px_rgba(0,0,0,0.1)] px-4 py-3">
      <div className="max-w-5xl mx-auto w-full flex justify-between items-center">
        {/* Left side - App branding */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-md">
            <Bot className="h-4 w-4 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">
              AI Agentic Stock Analysis
            </h1>
            <p className="text-xs text-gray-500">Powered by Ramus Corp</p>
          </div>
        </div>

        {/* Right side - User controls */}
        <div className="flex items-center gap-4">
          {/* Model Selection */}
          <ModelSelector />

          {/* User ID Management */}
          <UserIdInput
            currentUserId={userId}
            onUserIdChange={handleUserIdChange}
            onUserIdConfirm={handleUserIdConfirm}
            className="text-xs"
          />

          {/* Session Management */}
          {userId && (
            <SessionSelector
              currentUserId={userId}
              currentSessionId={sessionId}
              onSessionSelect={handleSessionSwitch}
              onCreateSession={handleCreateNewSession}
              className="text-xs"
            />
          )}
        </div>
      </div>
    </div>
  );
}
