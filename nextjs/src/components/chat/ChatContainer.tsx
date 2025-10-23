"use client";

import { BackendHealthChecker } from "@/components/chat/BackendHealthChecker";
import { ChatHeader } from "./ChatHeader";
import { ChatContent } from "./ChatContent";
import { ChatInput } from "./ChatInput";

/**
 * ChatLayout - Pure layout component for chat interface
 * Handles only UI structure and layout, no business logic
 * Uses context for all state management
 */
export function ChatContainer(): React.JSX.Element {
  return (
    <div className="h-screen flex flex-col bg-cream-50 relative">
      <BackendHealthChecker>
        {/* Fixed background */}
        <div className="absolute inset-0 bg-gradient-to-br from-cream-50 via-cream-25 to-cream-50 pointer-events-none"></div>
        {/* Stock market themed accent elements */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-20 right-10 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

        {/* Fixed Header - stays at top */}
        <div className="relative z-20 flex-shrink-0">
          <ChatHeader />
        </div>

        {/* Scrollable Messages Area - takes remaining space */}
        <div className="relative z-10 flex-1 min-h-0">
          <ChatContent />
        </div>

        {/* Fixed Input Area - always at bottom */}
        <div className="relative z-10 flex-shrink-0">
          <ChatInput />
        </div>
      </BackendHealthChecker>
    </div>
  );
}
