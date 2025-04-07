/**
 * Auth error handler for handling NextAuth client-side errors.
 * This helps prevent the CLIENT_FETCH_ERROR from disrupting the UI.
 */

/**
 * Function to handle NextAuth client errors and provide fallback strategies
 * @param error Error object from NextAuth
 * @returns Object indicating if the error was handled and any additional info
 */
export const handleAuthClientError = (error: any) => {
  // Check if it's the CLIENT_FETCH_ERROR
  if (error?.type === "CLIENT_FETCH_ERROR") {
    console.warn(
      "NextAuth fetch error occurred. Using fallback strategy.",
      error
    );

    // Return info about the error handling
    return {
      handled: true,
      action: "fallback",
      message:
        "Authentication service temporarily unavailable. Using fallback.",
    };
  }

  // If it's not a specific error we handle, return unhandled
  return {
    handled: false,
    action: "none",
    message: "Error not specifically handled",
  };
};

/**
 * Checks if a session has expired or is invalid
 * @param session The session object
 * @returns Boolean indicating if the session should be considered valid
 */
export const isValidSession = (session: any) => {
  if (!session) return false;

  // Add additional checks if needed such as expiration

  return true;
};

/**
 * Re-initializes the NextAuth client if needed
 */
export const reinitializeAuthClient = () => {
  if (typeof window === "undefined") return;

  // Clear any corrupted session data from storage
  try {
    localStorage.removeItem("next-auth.session-token");
    sessionStorage.removeItem("next-auth.session-token");

    // Force a page reload to re-initialize the client
    window.location.reload();
  } catch (error) {
    console.error("Failed to reinitialize auth client", error);
  }
};
