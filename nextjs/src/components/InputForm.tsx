"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Send } from "lucide-react";

interface InputFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
  context?: "homepage" | "chat"; // Add context prop for different placeholder text
}

export function InputForm({
  onSubmit,
  isLoading,
  context = "homepage",
}: InputFormProps): React.JSX.Element {
  const [inputValue, setInputValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current && context === "homepage") {
      textareaRef.current.focus();
    }
  }, [context]);

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSubmit(inputValue.trim());
      setInputValue("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const placeholderText = "분석하고 싶은 종목을 입력해주세요. (ex: Apple(APPL) 종목 분석해줘)"

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div
          className={`
          relative flex items-center gap-3 p-3 rounded-2xl border transition-all duration-200
          ${
            isFocused
              ? "border-emerald-400/50 bg-cream-25 shadow-lg shadow-emerald-500/10"
              : "border-gray-300 bg-cream-50 hover:border-gray-400"
          }
          backdrop-blur-sm
        `}
        >
          {/* Input Area */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholderText}
              rows={1}
              className="
                resize-none border-0 bg-transparent text-gray-900 placeholder-gray-500
                focus:ring-0 focus:outline-none focus:border-0 focus:shadow-none
                min-h-[40px] max-h-48
                scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-400
                px-0 py-2
              "
              style={{
                fontSize: "16px",
                lineHeight: "1.6",
                border: "none",
                outline: "none",
                boxShadow: "none",
              }}
            />

            {/* Character count for long messages */}
            {inputValue.length > 500 && (
              <div className="absolute bottom-1 right-1 text-xs text-gray-600 bg-white/80 rounded px-1">
                {inputValue.length}/2000
              </div>
            )}
          </div>

          {/* Send Button */}
          <Button
            type="submit"
            size="sm"
            disabled={!inputValue.trim() || isLoading}
            className="
              h-9 px-4 bg-sky-500 hover:bg-sky-600
              text-white border-0 shadow-lg transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              disabled:bg-gray-400
              flex items-center gap-2
            "
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="hidden sm:inline">Planning...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {context === "chat" ? "Send" : "Plan Goal"}
                </span>
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
