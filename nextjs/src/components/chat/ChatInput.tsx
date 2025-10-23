"use client";

import { InputForm } from "@/components/InputForm";
import { useChatContext } from "@/components/chat/ChatProvider";

/**
 * ChatInput - Input form wrapper with context integration
 * Handles message submission through context instead of prop drilling
 * Extracted from ChatMessagesView input section
 */
export function ChatInput(): React.JSX.Element {
  const { handleSubmit, isLoading } = useChatContext();

  return (
    <div className="relative z-10 flex-shrink-0 border-t border-gray-200 bg-cream-25/95 backdrop-blur-md shadow-2xl shadow-gray-200/40 shadow-[0_-8px_16px_-4px_rgba(0,0,0,0.15)] px-4 py-4">
      <div className="max-w-4xl mx-auto w-full">
        <InputForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          context="chat"
        />
      </div>
    </div>
  );
}
