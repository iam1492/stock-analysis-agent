/**
 * Simplified configuration for Next.js API endpoints
 * Uses local backend for all environments (development and production)
 */

export interface EndpointConfig {
  backendUrl: string;
  environment: "local" | "cloud";
}

/**
 * Gets the backend URL from environment variables
 */
function getBackendUrl(): string {
  // Use configured backend URL or default to local development
  return process.env.BACKEND_URL || "http://127.0.0.1:8000";
}

/**
 * Creates the endpoint configuration based on current environment
 */
export function createEndpointConfig(): EndpointConfig {
  const environment = process.env.GOOGLE_CLOUD_PROJECT ||
    process.env.K_SERVICE ||
    process.env.FUNCTION_NAME
    ? "cloud"
    : "local";

  const config: EndpointConfig = {
    backendUrl: getBackendUrl(),
    environment,
  };

  // Log configuration in development
  if (process.env.NODE_ENV === "development") {
    console.log("🔧 Endpoint Configuration:", {
      environment: config.environment,
      backendUrl: config.backendUrl,
    });
  }

  return config;
}

/**
 * Get the current endpoint configuration
 */
export const endpointConfig = createEndpointConfig();

/**
 * Utility function to get authentication headers
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  return headers;
}

/**
 * Gets the appropriate endpoint for a given API path
 */
export function getEndpointForPath(path: string): string {
  // Always use local backend for all environments
  return `${endpointConfig.backendUrl}${path}`;
}
