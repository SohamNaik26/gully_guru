"use client";

import { useSearchParams } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import Navbar from "@/components/layout/navbar";
import { AlertTriangle, RefreshCw, ArrowLeft } from "lucide-react";
import { useState, useEffect } from "react";

export default function AuthErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");
  const [isBackendRunning, setIsBackendRunning] = useState<boolean | null>(
    null
  );

  // Check if the backend is running
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch("/api/health-check", {
          method: "GET",
          cache: "no-store",
          headers: { "Cache-Control": "no-cache" },
        });
        setIsBackendRunning(response.ok);
      } catch (error) {
        setIsBackendRunning(false);
      }
    };

    if (error === "CLIENT_FETCH_ERROR") {
      checkBackendStatus();
    }
  }, [error]);

  let title = "Authentication Error";
  let message = "An error occurred during the authentication process.";
  let icon = null;
  let additionalInfo = null;

  // Customize error messages based on error types
  if (error === "AccessDenied") {
    title = "Access Denied";
    message = "You don't have permission to sign in to this application.";
    icon = <AlertTriangle className="h-12 w-12 text-destructive mb-4" />;
  } else if (error === "Configuration") {
    title = "Configuration Error";
    message = "There is a problem with the server configuration.";
    icon = <AlertTriangle className="h-12 w-12 text-destructive mb-4" />;
  } else if (error === "Verification") {
    title = "Verification Error";
    message = "The verification link may have expired or already been used.";
    icon = <AlertTriangle className="h-12 w-12 text-amber-500 mb-4" />;
  } else if (error === "CLIENT_FETCH_ERROR") {
    title = "Connection Error";
    message = "Unable to connect to the authentication server.";
    icon = <RefreshCw className="h-12 w-12 text-amber-500 mb-4 animate-spin" />;

    if (isBackendRunning === false) {
      additionalInfo = (
        <div className="mt-4 p-4 bg-amber-50 rounded-md border border-amber-200 text-amber-800">
          <h3 className="font-semibold mb-1">Possible solutions:</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>Ensure your backend server is running</li>
            <li>Check your network connection</li>
            <li>Verify the API URL in your environment variables</li>
            <li>
              You may still be able to access parts of the app that don't
              require authentication
            </li>
          </ul>
        </div>
      );
    } else if (isBackendRunning === true) {
      additionalInfo = (
        <div className="mt-4 p-4 bg-amber-50 rounded-md border border-amber-200 text-amber-800">
          <h3 className="font-semibold mb-1">
            Backend is running but authentication failed
          </h3>
          <p className="text-sm mb-2">This could be due to:</p>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>Temporary authentication service disruption</li>
            <li>Configuration mismatch between frontend and backend</li>
            <li>Google OAuth issues</li>
          </ul>
        </div>
      );
    }
  } else if (error === "JWT_SESSION_ERROR") {
    title = "Session Error";
    message = "There was a problem with your session.";
    icon = <AlertTriangle className="h-12 w-12 text-amber-500 mb-4" />;

    additionalInfo = (
      <div className="mt-4 p-4 bg-amber-50 rounded-md border border-amber-200 text-amber-800">
        <h3 className="font-semibold mb-1">This is likely due to:</h3>
        <ul className="list-disc list-inside space-y-1 text-sm">
          <li>Your session token is invalid or expired</li>
          <li>The NEXTAUTH_SECRET environment variable has changed</li>
          <li>Your browser cookies may be corrupted</li>
        </ul>
        <div className="mt-3 text-sm">
          <p className="font-semibold">Recommended actions:</p>
          <ol className="list-decimal list-inside space-y-1">
            <li>Clear your browser cookies for this site</li>
            <li>Try signing in again</li>
            <li>If the problem persists, contact the administrator</li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <main className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-muted/50 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1 text-center">
            {icon && <div className="flex justify-center">{icon}</div>}
            <CardTitle className="text-2xl font-bold text-destructive">
              {title}
            </CardTitle>
            <CardDescription>{message}</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div className="text-sm text-muted-foreground">
              Error code: {error || "unknown"}
            </div>
            {additionalInfo}
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" asChild>
              <Link href="/" className="flex items-center gap-1">
                <ArrowLeft className="h-4 w-4" />
                Home
              </Link>
            </Button>
            <Button asChild>
              <Link href="/auth/signin" className="flex items-center gap-1">
                <RefreshCw className="h-4 w-4 mr-1" />
                Try Again
              </Link>
            </Button>
          </CardFooter>
        </Card>
      </main>
    </>
  );
}
