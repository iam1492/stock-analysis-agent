import {
  getEndpointForPath,
  getAuthHeaders,
} from "@/lib/config";

/**
 * Gets the ADK app name from environment or defaults
 */
function getAdkAppName(): string {
  return process.env.ADK_APP_NAME || "app";
}

/**
 * Session creation result with success status and session details
 */
export interface SessionCreationResult {
  success: boolean;
  sessionId?: string;
  created?: boolean;
  error?: string;
  deploymentType?: string;
}

/**
 * Local Backend session service implementation
 * Handles session creation using local backend API
 */
export class LocalBackendSessionService {
  async createSession(userId: string): Promise<SessionCreationResult> {
    const appName = getAdkAppName();
    const sessionEndpoint = getEndpointForPath(
      `/apps/${appName}/users/${userId}/sessions`
    );

    try {
      const sessionAuthHeaders = await getAuthHeaders();
      const sessionResponse = await fetch(sessionEndpoint, {
        method: "POST",
        headers: {
          ...sessionAuthHeaders,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      if (!sessionResponse.ok) {
        const errorText = await sessionResponse.text();
        console.error(
          "Local backend session creation failed:",
          sessionResponse.status,
          errorText
        );
        return {
          success: false,
          error: `Local backend session creation failed: ${sessionResponse.status} ${errorText}`,
          deploymentType: "local_backend",
        };
      }

      const sessionData = await sessionResponse.json();
      const sessionId = sessionData.id;

      if (!sessionId) {
        return {
          success: false,
          error: "Local backend did not return a session ID",
          deploymentType: "local_backend",
        };
      }

      console.log("Local backend session created successfully:", sessionId);
      return {
        success: true,
        sessionId,
        created: true,
        deploymentType: "local_backend",
      };
    } catch (sessionError) {
      console.error("Local backend session creation error:", sessionError);
      return {
        success: false,
        error: `Local backend session creation error: ${
          sessionError instanceof Error
            ? sessionError.message
            : String(sessionError)
        }`,
        deploymentType: "local_backend",
      };
    }
  }
}

/**
 * Convenience function to create a session using the local backend service
 */
export async function createSessionWithService(
  userId: string
): Promise<SessionCreationResult> {
  const service = new LocalBackendSessionService();
  return await service.createSession(userId);
}
