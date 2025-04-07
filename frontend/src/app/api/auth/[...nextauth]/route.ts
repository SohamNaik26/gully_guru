import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import axios from "axios";
import crypto from "crypto";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Make sure NextAuth secret is set
if (!process.env.NEXTAUTH_SECRET) {
  throw new Error("NEXTAUTH_SECRET is not set in environment variables");
}

// Extend the JWT and Session types
declare module "next-auth" {
  interface Session {
    user?: {
      id?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string;
  }
}

// Generate a stable integer from an email
const generateStableTelegramId = (email: string): number => {
  const hash = crypto.createHash("md5").update(email).digest("hex");
  // Take the first 8 characters of the hash and convert to a number
  // This will be within safe integer range
  return parseInt(hash.substring(0, 8), 16) % 2147483647; // Ensure it's within INT range
};

const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    }),
  ],
  callbacks: {
    async signIn({ user, account }) {
      if (account?.provider === "google" && user.email) {
        try {
          // For development, you can bypass the backend check completely
          // or when NEXT_PUBLIC_USE_MOCK_DATA is true
          if (
            process.env.NODE_ENV === "development" &&
            (process.env.NEXT_PUBLIC_USE_MOCK_DATA === "true" ||
              !process.env.REQUIRE_BACKEND_CHECK)
          ) {
            console.log("Development mode: Bypassing backend check");
            return true;
          }

          // Check if the backend is accessible
          try {
            // Use a timeout to avoid long wait times
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout

            // Check if user exists in our backend by email
            const response = await axios.get(
              `${API_URL}/api/users?email=${encodeURIComponent(user.email)}`,
              { signal: controller.signal }
            );

            clearTimeout(timeoutId);

            // If user doesn't exist, create a new user with a deterministic telegram_id
            if (response.data.length === 0) {
              const telegram_id = generateStableTelegramId(user.email);

              await axios.post(`${API_URL}/api/users`, {
                telegram_id,
                username:
                  user.name?.replace(/\s+/g, "_").toLowerCase() || "user",
                full_name: user.name || "Unknown User",
                email: user.email,
              });
            }

            return true;
          } catch (fetchError: Error | unknown) {
            // Handle timeout or connection error
            const errorMessage =
              typeof fetchError === "object" &&
              fetchError !== null &&
              "message" in fetchError
                ? (fetchError as { message: string }).message
                : "Unknown error connecting to backend";

            console.error("Backend connection error:", errorMessage);

            // For development, allow sign in even if backend is not available
            if (process.env.NODE_ENV === "development") {
              console.warn(
                "Backend connection failed but allowing sign in for development"
              );
              return true;
            }
            throw fetchError; // Re-throw to be caught by the outer catch
          }
        } catch (error) {
          console.error("Error during sign in:", error);

          // For development, allow sign in even if there's any error
          if (process.env.NODE_ENV === "development") {
            console.warn(
              "Sign-in error occurred but allowing sign in for development"
            );
            return true;
          }
          return false;
        }
      }
      return true;
    },
    async session({ session, token }) {
      if (token.sub && session.user) {
        session.user.id = token.sub;
      }
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
  },
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },
  // JWT configuration
  jwt: {
    // Use the NEXTAUTH_SECRET for JWT encryption
    // No need to specify secret here as it's taken from the environment variable
    maxAge: 60 * 60 * 24 * 30, // 30 days
  },
  // Session configuration
  session: {
    strategy: "jwt",
    maxAge: 60 * 60 * 24 * 7, // 1 week
  },
  // Add a debug flag for development
  debug: process.env.NODE_ENV === "development",
  // Use the NEXTAUTH_SECRET for secure cookies
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST, authOptions };
