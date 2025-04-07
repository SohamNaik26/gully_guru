import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";

export async function middleware(request: NextRequest) {
  // Get the pathname of the request
  const path = request.nextUrl.pathname;

  // Public paths that don't require authentication
  const publicPaths = [
    "/",
    "/auth/signin",
    "/auth/error",
    "/api/auth",
    "/api/health-check",
  ];

  // Static files and api routes don't need to be handled by this middleware
  const isStaticFile =
    path.startsWith("/_next") ||
    path.includes("/static/") ||
    path.endsWith(".ico") ||
    path.endsWith(".png") ||
    path.endsWith(".jpg") ||
    path.endsWith(".svg");

  // Skip middleware for public paths and static files
  if (publicPaths.some((p) => path.startsWith(p)) || isStaticFile) {
    return NextResponse.next();
  }

  // Try to get the NextAuth token
  try {
    const token = await getToken({
      req: request,
      secret: process.env.NEXTAUTH_SECRET,
    });

    // Redirect to sign in if not authenticated
    if (!token) {
      const url = new URL("/auth/signin", request.url);
      url.searchParams.set("callbackUrl", request.url);
      return NextResponse.redirect(url);
    }

    // User is authenticated, allow access
    return NextResponse.next();
  } catch (error) {
    // If there's an error with the JWT or token, redirect to error page
    console.error("NextAuth middleware error:", error);

    const errorUrl = new URL("/auth/error", request.url);
    errorUrl.searchParams.set("error", "JWT_SESSION_ERROR");
    return NextResponse.redirect(errorUrl);
  }
}

// Only run middleware on these paths
export const config = {
  matcher: [
    /*
     * Match all paths except:
     * 1. /api routes that don't require auth
     * 2. /_next (static files)
     * 3. /static files
     * 4. All files in the public folder
     */
    "/((?!_next|static|favicon.ico|public).*)",
  ],
};
