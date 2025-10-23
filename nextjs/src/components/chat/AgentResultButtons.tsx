"use client";

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { AgentResultModal } from "@/components/ui/agent-result-modal";
import { useChatContext } from "./ChatProvider";
import { Eye, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface AgentResultButtonsProps {
  isAnalysisComplete: boolean;
  onCopy?: (text: string) => void;
  copiedText?: string | null;
}

const agentButtonConfig = [
  {
    agentName: 'senior_financial_advisor_agent',
    label: '선임 재무 연구원 결과보기',
    color: 'bg-blue-600 hover:bg-blue-700'
  },
  {
    agentName: 'senior_quantitative_advisor_agent',
    label: '선임 퀀트 분석가 결과보기',
    color: 'bg-purple-600 hover:bg-purple-700'
  },
  {
    agentName: 'technical_analyst_agent',
    label: '기술적 분석가 결과보기',
    color: 'bg-green-600 hover:bg-green-700'
  },
  {
    agentName: 'stock_researcher_agent',
    label: '주식 연구원 결과보기',
    color: 'bg-orange-600 hover:bg-orange-700'
  }
];

export function AgentResultButtons({
  isAnalysisComplete,
  onCopy,
  copiedText
}: AgentResultButtonsProps) {
  const { agentResults, getAgentResult } = useChatContext();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [agentResult, setAgentResult] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loadingAgent, setLoadingAgent] = useState<string | null>(null);

  const handleAgentClick = (agentName: string) => {
    setSelectedAgent(agentName);
    setLoadingAgent(agentName);

    try {
      const result = getAgentResult(agentName);
      if (result) {
        setAgentResult(result);
        setIsModalOpen(true);
      } else {
        console.warn(`No result found for ${agentName}`);
        toast.error("결과를 찾을 수 없습니다", {
          description: `${agentName}에 대한 분석 결과가 아직 준비되지 않았습니다.`
        });
      }
    } catch (error) {
      console.error(`Failed to load ${agentName} result:`, error);
      toast.error("결과 로딩 실패", {
        description: `${agentName} 결과를 불러오는데 실패했습니다. 잠시 후 다시 시도해주세요.`
      });
    } finally {
      setLoadingAgent(null);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedAgent(null);
    setAgentResult(null);
  };

  // Don't render anything if analysis is not complete
  if (!isAnalysisComplete) {
    return null;
  }

  return (
    <>
      <div className="flex flex-wrap gap-2 mt-4 p-4 bg-gray-100 rounded-lg border border-gray-200">
        <div className="w-full mb-2">
          <p className="text-sm text-gray-600 font-medium">상세 분석 결과 보기:</p>
        </div>

        {agentButtonConfig.map((config) => {
          const isAvailable = agentResults[config.agentName] && agentResults[config.agentName].length > 0;
          const isLoadingThis = loadingAgent === config.agentName;

          return (
            <Button
              key={config.agentName}
              onClick={() => handleAgentClick(config.agentName)}
              disabled={!isAvailable || isLoadingThis}
              className={`flex items-center gap-2 text-white text-sm px-3 py-2 h-auto ${
                isAvailable ? config.color : 'bg-slate-600 cursor-not-allowed'
              }`}
            >
              {isLoadingThis ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
              {config.label}
              {!isAvailable && (
                <span className="text-xs opacity-75">(준비중)</span>
              )}
            </Button>
          );
        })}
      </div>

      <AgentResultModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        agentResult={agentResult}
        agentName={selectedAgent || undefined}
        onCopy={onCopy}
        copiedText={copiedText}
      />
    </>
  );
}