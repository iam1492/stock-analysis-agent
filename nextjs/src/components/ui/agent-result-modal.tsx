"use client";

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MarkdownRenderer } from "@/components/chat/MarkdownRenderer";
import { X, Copy, CopyCheck } from "lucide-react";
interface AgentResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  agentResult: string | null;
  agentName?: string;
  onCopy?: (text: string) => void;
  copiedText?: string | null;
}

const agentDisplayNames: Record<string, string> = {
  'senior_financial_advisor_agent': '선임 재무 연구원',
  'senior_quantitative_advisor_agent': '선임 퀀트 분석가',
  'technical_analyst_agent': '기술적 분석가',
  'senior_research_advisor_agent': '선임 주식 연구원',
  'hedge_fund_manager_agent': '헤지펀드 매니저'
};

export function AgentResultModal({
  isOpen,
  onClose,
  agentResult,
  agentName,
  onCopy,
  copiedText
}: AgentResultModalProps) {
  const [isCopySuccess, setIsCopySuccess] = useState(false);

  const handleCopy = () => {
    if (agentResult && onCopy) {
      onCopy(agentResult);
      setIsCopySuccess(true);
      setTimeout(() => {
        setIsCopySuccess(false);
      }, 5000);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col bg-cream-25 border-gray-200">
        <DialogHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl font-semibold text-gray-900">
                {agentName ? agentDisplayNames[agentName] || agentName : 'Agent 결과'}
              </DialogTitle>
              <DialogDescription className="text-sm text-gray-500 mt-1">
                {agentName && (
                  <>
                    분석 시간: {new Date().toLocaleString('ko-KR')}
                  </>
                )}
              </DialogDescription>
            </div>
            <div className="flex items-center gap-2">
              {onCopy && agentResult && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopy}
                  className="flex items-center gap-2 border-gray-300 bg-gray-50 text-gray-700 hover:bg-gray-100"
                >
                  {isCopySuccess ? (
                    <>
                      <CopyCheck className="h-4 w-4 text-green-600" />
                      복사됨
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      복사
                    </>
                  )}
                </Button>
              )}

            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 min-h-0 mt-4 overflow-y-auto overflow-x-hidden pr-4 pb-4">
          {agentResult ? (
            <div className="prose prose-gray max-w-none">
              <MarkdownRenderer content={agentResult} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-gray-500">
              <p>결과를 불러오는 중...</p>
            </div>
          )}
        </div>

        <div className="flex-shrink-0 flex justify-end gap-2 mt-4 pt-4 border-t border-gray-200">
          <Button variant="outline" onClick={onClose} className="border-gray-300 bg-gray-50 text-gray-700 hover:bg-gray-100">
            닫기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}