"use client";

import { SessionProvider } from "next-auth/react";
import { ThemeProvider } from "next-themes";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useEffect, useState } from "react";
import { handleAuthClientError } from "@/lib/auth-error-handler";

export function Providers({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  // This is needed to prevent hydration mismatch
  // The app will only render after the client-side hydration is complete
  useEffect(() => {
    setMounted(true);
  }, []);

  // Add global error handling for auth errors
  useEffect(() => {
    const originalOnError = window.onerror;

    window.onerror = function (message, source, lineno, colno, error) {
      // Check if the error is from NextAuth
      if (
        message &&
        (message.toString().includes("next-auth") ||
          message.toString().includes("CLIENT_FETCH_ERROR"))
      ) {
        const result = handleAuthClientError(error);

        if (result.handled) {
          console.log("Auth error handled:", result.message);
          // Return true to prevent default error handling
          return true;
        }
      }

      // Pass to original handler
      if (originalOnError) {
        return originalOnError(message, source, lineno, colno, error);
      }

      return false;
    };

    return () => {
      window.onerror = originalOnError;
    };
  }, []);

  return (
    <SessionProvider
      refetchInterval={0}
      refetchOnWindowFocus={false}
      // Add simple client-side error handling
      onError={(error) => {
        console.error("NextAuth session error:", error);
        handleAuthClientError(error);
        return false; // Don't rethrow
      }}
    >
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <TooltipProvider>{mounted ? children : null}</TooltipProvider>
      </ThemeProvider>
    </SessionProvider>
  );
}
