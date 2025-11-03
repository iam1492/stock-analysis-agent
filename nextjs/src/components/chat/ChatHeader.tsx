"use client";

import { Bot, LogOut } from "lucide-react";
import { SessionSelector } from "@/components/chat/SessionSelector";
import { ModelSelector } from "@/components/chat/ModelSelector";
import { useChatContext } from "@/components/chat/ChatProvider";
import { useSession, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";

/**
 * ChatHeader - User and session management interface
 * Extracted from ChatMessagesView header section
 * Handles user ID input and session selection
 */
export function ChatHeader(): React.JSX.Element {
  const { data: session } = useSession();
  const {
    sessionId,
    handleSessionSwitch,
    handleCreateNewSession,
  } = useChatContext();

  const handleSignOut = () => {
    signOut({ callbackUrl: "/login" });
  };

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
          {/* User Info */}
          {session?.user && (
            <div className="text-sm text-gray-600 mr-2">
              Welcome, {session.user.name || session.user.email}
            </div>
          )}

          {/* Model Selection */}
          <ModelSelector />

          {/* Session Management */}
          <SessionSelector
            currentUserId={session?.user?.id || ""}
            currentSessionId={sessionId}
            onSessionSelect={handleSessionSwitch}
            onCreateSession={handleCreateNewSession}
            className="text-xs"
          />

          {/* Admin Actions */}
          {session?.user?.role === 'admin' && (
            <>
              {/* Debug info */}
              <div className="text-xs text-gray-500 mr-2">
                Role: {session.user.role}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.location.href = '/signup'}
                className="flex items-center gap-2 bg-emerald-50 border-emerald-300 hover:bg-emerald-100 text-emerald-700 hover:text-emerald-800 shadow-sm"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Account
              </Button>
            </>
          )}

          {/* Sign Out Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleSignOut}
            className="flex items-center gap-2 bg-white/80 border-gray-300 hover:bg-gray-50 text-gray-700 hover:text-gray-900 shadow-sm"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </Button>
        </div>
      </div>
    </div>
  );
}
