"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { reinitializeAuthClient } from "@/lib/auth-error-handler";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: string;
}

/**
 * Error boundary component specifically for handling NextAuth errors
 * This helps recover from client-side auth errors without reloading the entire page
 */
class AuthErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: "",
  };

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error, errorInfo: error.message };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to the console
    console.error("Auth Error Boundary caught error:", error, errorInfo);

    // Update state with error details
    this.setState({
      error,
      errorInfo: errorInfo.componentStack,
    });
  }

  // Method to reset the error state and retry
  resetError = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: "" });
  };

  // Handle a more severe error that requires clearing session
  handleClearSession = (): void => {
    reinitializeAuthClient();
    this.resetError();
  };

  render(): ReactNode {
    // If there was an error, show the fallback UI
    if (this.state.hasError) {
      // Check if it's a NextAuth error
      const isAuthError =
        this.state.error?.message.includes("next-auth") ||
        this.state.error?.message.includes("CLIENT_FETCH_ERROR");

      // If a custom fallback is provided, use it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="p-6 rounded-lg border border-amber-200 bg-amber-50 text-amber-800 my-4">
          <h3 className="text-lg font-semibold mb-2">
            {isAuthError ? "Authentication Error" : "Something went wrong"}
          </h3>

          <p className="mb-4 text-sm">
            {isAuthError
              ? "There was a problem with the authentication service. Please try again."
              : "An unexpected error occurred. Please try again."}
          </p>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={this.resetError}
              className="text-sm"
            >
              Try Again
            </Button>

            {isAuthError && (
              <Button
                variant="destructive"
                onClick={this.handleClearSession}
                className="text-sm"
              >
                Clear Session & Reload
              </Button>
            )}
          </div>
        </div>
      );
    }

    // Otherwise, render children normally
    return this.props.children;
  }
}

export default AuthErrorBoundary;
