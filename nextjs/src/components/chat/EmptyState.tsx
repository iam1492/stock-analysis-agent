"use client";

import { TrendingUp, BarChart3, PieChart, Brain, Users, Zap } from "lucide-react";

/**
 * EmptyState - AI Goal Planner welcome screen
 * Extracted from ChatMessagesView empty state section
 * Displays when no messages exist in the current session
 */
export function EmptyState(): React.JSX.Element {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 text-center min-h-[60vh]">
      <div className="max-w-4xl w-full space-y-8">
        {/* Main header */}
        <div className="space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-emerald-600" />
            </div>
            <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900">AI Agentic Stock Analysis</h1>
          <p className="text-xl text-gray-600">Powered by Ramus Corp</p>
        </div>

        {/* Description */}
        <div className="space-y-4">
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            AI agents analyze stocks from multiple specialized perspectives to
            provide comprehensive investment insights and data-driven
            recommendations.
          </p>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          <div className="space-y-3">
            <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center mx-auto">
              <TrendingUp className="w-6 h-6 text-emerald-600" />
            </div>
            <h3 className="font-semibold text-emerald-600">Multi-Agent Analysis</h3>
            <p className="text-sm text-gray-500">
              Specialized AI agents analyze stocks from different perspectives
            </p>
          </div>
          <div className="space-y-3">
            <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mx-auto">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-blue-600">Comprehensive Data</h3>
            <p className="text-sm text-gray-500">
              Financial statements, technical indicators, and market data
            </p>
          </div>
          <div className="space-y-3">
            <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mx-auto">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-purple-600">AI-Powered Insights</h3>
            <p className="text-sm text-gray-500">
              Intelligent recommendations based on advanced analysis
            </p>
          </div>
        </div>

        {/* Try asking about section */}
        <div className="space-y-4">
          <p className="text-gray-500">Try asking about:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm">
              Stock analysis for AAPL
            </span>
            <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm">
              Quant Analysis
            </span>
            <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm">
              Market trends analysis
            </span>
            <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm">
              Investment recommendations
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
