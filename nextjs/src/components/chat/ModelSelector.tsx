"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useChatContext } from "@/components/chat/ChatProvider";

export type ModelOption = {
  value: string;
  label: string;
  description: string;
};

const AVAILABLE_MODELS: ModelOption[] = [
  {
    value: "gemini-2.0-flash",
    label: "Gemini 2.0 Flash",
    description: "Fast and efficient Gemini model"
  },
  {
    value: "gemini-2.5-flash",
    label: "Gemini 2.5 Flash",
    description: "Latest fast Gemini model (default)"
  },
  {
    value: "gemini-2.5-pro",
    label: "Gemini 2.5 Pro",
    description: "Most capable Gemini model"
  },
  {
    value: "openrouter/z-ai/glm-4.6",
    label: "GLM-4.6 (OpenRouter)",
    description: "High-performance open-source model"
  },
  {
    value: "openrouter/qwen/qwen3-max",
    label: "Qwen3 Max (OpenRouter)",
    description: "Advanced Qwen model via OpenRouter"
  },
  {
    value: "openrouter/x-ai/grok-4-fast",
    label: "Grok4 fast (OpenRouter)",
    description: "xAI's latest multimodal model"
  }
];

/**
 * ModelSelector - Dropdown component for selecting LLM models
 * Integrates with ChatProvider for state management and persistence
 */
export function ModelSelector(): React.JSX.Element {
  const { selectedModel, setSelectedModel } = useChatContext();

  const handleModelChange = (value: string) => {
    setSelectedModel(value);
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-600">Model:</span>
      <Select value={selectedModel} onValueChange={handleModelChange}>
        <SelectTrigger className="w-44 h-12 text-xs bg-sky-100 border-sky-200 text-gray-900 hover:bg-sky-200 focus:border-sky-400 px-4 py-1">
          <SelectValue placeholder="Select model" />
        </SelectTrigger>
        <SelectContent className="bg-white border-gray-200 min-w-44">
          {AVAILABLE_MODELS.map((model) => (
            <SelectItem
              key={model.value}
              value={model.value}
              className="text-gray-900 focus:bg-sky-100 focus:text-gray-900 cursor-pointer py-3 px-3"
            >
              <div className="flex flex-col items-start w-full min-w-0">
                <span className="font-medium text-gray-900 text-sm truncate w-full">
                  {model.label}
                </span>
                <span className="text-gray-600 text-xs mt-1">
                  {model.description}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}