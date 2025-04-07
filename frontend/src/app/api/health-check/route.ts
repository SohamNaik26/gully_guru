import { NextResponse } from "next/server";

// The URL to your backend API
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Simple health check endpoint that checks if the backend API is accessible
 * This is used to provide better error messages when authentication fails
 */
export async function GET() {
  try {
    // Use a short timeout to avoid waiting too long
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    // Try to fetch the backend health endpoint
    const response = await fetch(`${API_URL}/health`, {
      method: "GET",
      signal: controller.signal,
      cache: "no-store",
      headers: {
        "Cache-Control": "no-cache",
      },
    });

    clearTimeout(timeoutId);

    // If we're in development mode with mock data enabled, consider the backend "up"
    if (
      process.env.NODE_ENV === "development" &&
      process.env.NEXT_PUBLIC_USE_MOCK_DATA === "true"
    ) {
      return NextResponse.json({
        status: "ok",
        message: "Using mock data in development mode",
      });
    }

    if (response.ok) {
      return NextResponse.json({
        status: "ok",
        message: "Backend server is accessible",
      });
    } else {
      return NextResponse.json(
        {
          status: "error",
          message: `Backend server returned status ${response.status}`,
        },
        { status: 200 } // Still return 200 to the frontend since this is diagnostic info
      );
    }
  } catch (error) {
    // Handle connection errors
    let errorMessage = "Unknown error";
    if (error instanceof Error) {
      errorMessage = error.message;
    }

    // If using mock data in development, still return success
    if (
      process.env.NODE_ENV === "development" &&
      process.env.NEXT_PUBLIC_USE_MOCK_DATA === "true"
    ) {
      return NextResponse.json({
        status: "ok",
        message: "Using mock data in development mode",
        error: errorMessage,
      });
    }

    return NextResponse.json(
      {
        status: "error",
        message: "Could not connect to backend server",
        error: errorMessage,
      },
      { status: 200 } // Still return 200 so frontend can use the information
    );
  }
}
