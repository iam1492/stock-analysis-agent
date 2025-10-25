import { useState, useCallback, useEffect } from "react";
import { useSession as useNextAuthSession } from "next-auth/react";

export interface UseSessionReturn {
  // State
  sessionId: string;
  userId: string;

  // User ID management
  handleUserIdChange: (newUserId: string) => void;
  handleUserIdConfirm: (confirmedUserId: string) => void;

  // Session management
  handleSessionSwitch: (newSessionId: string) => void;
  handleCreateNewSession: (sessionUserId: string) => Promise<void>;
}

/**
 * Custom hook for managing chat sessions and user ID (integrated with NextAuth)
 */
export function useSession(): UseSessionReturn {
  const { data: session } = useNextAuthSession();
  const [sessionId, setSessionId] = useState<string>("");
  const [userId, setUserId] = useState<string>("");

  // Set userId from NextAuth session
  useEffect(() => {
    if (session?.user?.id) {
      setUserId(session.user.id);
    }
  }, [session?.user?.id]);

  // Handle session switching
  const handleSessionSwitch = useCallback(
    (newSessionId: string): void => {
      console.log(
        `🔄 handleSessionSwitch called: current=${sessionId}, new=${newSessionId}, userId=${userId}`
      );

      if (!userId || newSessionId === sessionId) {
        console.log(`⏭️ Skipping session switch: no userId or same session`);
        return;
      }

      // Switch to new session
      console.log(`🎯 Setting sessionId state to: ${newSessionId}`);
      setSessionId(newSessionId);

      console.log(`✅ Session switch completed to: ${newSessionId}`);
    },
    [userId, sessionId]
  );

  // Handle new session creation
  const handleCreateNewSession = useCallback(
    async (sessionUserId: string): Promise<void> => {
      if (!sessionUserId) {
        throw new Error("User ID is required to create a session");
      }

      let actualSessionId = "";

      try {
        // Import Server Action dynamically to avoid circular dependencies in hooks
        const { createSessionAction } = await import(
          "@/lib/actions/session-actions"
        );

        const sessionResult = await createSessionAction(sessionUserId);

        if (sessionResult.success) {
          // Use the session ID returned by the backend
          if (!sessionResult.sessionId) {
            throw new Error(
              "Session creation succeeded but no session ID was returned"
            );
          }
          actualSessionId = sessionResult.sessionId;
          console.log(
            `✅ Session created via Server Action: ${actualSessionId}`
          );
          console.log(`📝 Session result:`, sessionResult);
        } else {
          console.error(
            "❌ Session creation Server Action failed:",
            sessionResult.error
          );
          throw new Error(`Session creation failed: ${sessionResult.error}`);
        }
      } catch (error) {
        console.error("❌ Session creation Server Action error:", error);
        throw error;
      }

      console.log(`🔄 Switching to new session: ${actualSessionId}`);
      handleSessionSwitch(actualSessionId);
    },
    [handleSessionSwitch]
  );

  // Handle user ID changes (now read-only from NextAuth session)
  const handleUserIdChange = useCallback((newUserId: string): void => {
    // User ID is now managed by NextAuth session, so this is a no-op
    console.log("User ID change ignored - managed by NextAuth session");
  }, []);

  // Handle user ID confirmation (now read-only from NextAuth session)
  const handleUserIdConfirm = useCallback((confirmedUserId: string): void => {
    // User ID is now managed by NextAuth session, so this is a no-op
    console.log("User ID confirmation ignored - managed by NextAuth session");
  }, []);

  return {
    // State
    sessionId,
    userId,

    // User ID management
    handleUserIdChange,
    handleUserIdConfirm,

    // Session management
    handleSessionSwitch,
    handleCreateNewSession,
  };
}
