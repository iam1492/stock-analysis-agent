import {
  getEndpointForPath,
  getAuthHeaders,
} from "@/lib/config";
import type {
  AdkSession,
  AdkSessionWithEvents,
  ListSessionsResponse,
  ListEventsResponse,
} from "@/lib/types/adk";

/**
 * ADK Session History Service - Handles session and event retrieval for chat history
 * Uses local backend for all environments
 *
 * This service provides:
 * - Session retrieval by ID
 * - Event listing for sessions
 * - Combined session + events for historical loading
 */

/**
 * Gets the ADK app name from environment or defaults
 */
function getAdkAppName(): string {
  return process.env.ADK_APP_NAME || "app";
}

/**
 * ADK Session Service - Handles all session-related API calls using local backend
 */
export class AdkSessionService {
  /**
   * Retrieves a specific session by ID
   */
  static async getSession(
    userId: string,
    sessionId: string
  ): Promise<AdkSession | null> {
    const appName = getAdkAppName();
    const endpoint = getEndpointForPath(
      `/apps/${appName}/users/${userId}/sessions/${sessionId}`
    );

    try {
      const authHeaders = await getAuthHeaders();
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          ...authHeaders,
        },
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Failed to get session: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error(
        "❌ [ADK SESSION SERVICE] Local Backend getSession error:",
        error
      );
      throw error;
    }
  }

  /**
   * Lists all sessions for a user
   */
  static async listSessions(userId: string): Promise<ListSessionsResponse> {
    const appName = getAdkAppName();
    const endpoint = getEndpointForPath(
      `/apps/${appName}/users/${userId}/sessions`
    );

    console.log(
      "🔗 [ADK SESSION SERVICE] Local Backend listSessions request:",
      {
        endpoint,
        method: "GET",
        userId,
        appName,
      }
    );

    try {
      const authHeaders = await getAuthHeaders();
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          ...authHeaders,
        },
      });

      console.log("📡 [ADK SESSION SERVICE] Local Backend response:", {
        status: response.status,
        statusText: response.statusText,
        contentType: response.headers.get("content-type"),
      });

      if (!response.ok) {
        throw new Error(`Failed to list sessions: ${response.statusText}`);
      }

      const sessions: AdkSession[] = await response.json();

      console.log("✅ [ADK SESSION SERVICE] Local Backend success:", {
        sessionsCount: sessions.length,
        sessionIds: sessions.map((s) => s.id || "no-id"),
      });

      return {
        sessions,
        sessionIds: sessions.map((session) => session.id),
      };
    } catch (error) {
      console.error("❌ [ADK SESSION SERVICE] Local Backend error:", error);
      throw error;
    }
  }

  /**
   * Lists all events for a specific session
   */
  static async listEvents(
    userId: string,
    sessionId: string
  ): Promise<ListEventsResponse> {
    const appName = getAdkAppName();
    const endpoint = getEndpointForPath(
      `/apps/${appName}/users/${userId}/sessions/${sessionId}/events`
    );

    try {
      const authHeaders = await getAuthHeaders();
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          ...authHeaders,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to list events: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error(
        "❌ [ADK SESSION SERVICE] Local Backend listEvents error:",
        error
      );
      throw error;
    }
  }

  /**
   * Retrieves a session with all its events (for historical context)
   */
  static async getSessionWithEvents(
    userId: string,
    sessionId: string
  ): Promise<AdkSessionWithEvents | null> {
    try {
      // Local backend - fetch session only (backend includes events in session detail)
      const session = await AdkSessionService.getSession(userId, sessionId);

      if (!session) {
        return null;
      }

      // Use events directly from session detail (backend includes them)
      const events = session.events || [];

      return {
        ...session,
        events,
      };
    } catch (error) {
      console.error(
        "❌ [ADK SESSION SERVICE] Error fetching session with events:",
        error
      );
      throw error;
    }
  }
}

/**
 * Convenience functions that use the AdkSessionService
 */
export async function getSessionWithEvents(
  userId: string,
  sessionId: string
): Promise<AdkSessionWithEvents | null> {
  return await AdkSessionService.getSessionWithEvents(userId, sessionId);
}

export async function listUserSessions(
  userId: string
): Promise<ListSessionsResponse> {
  return await AdkSessionService.listSessions(userId);
}
