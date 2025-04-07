"use client";

import { signIn } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export const SignInButton = () => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = async () => {
    try {
      setIsLoading(true);
      await signIn("google", { callbackUrl: "/dashboard" });
    } catch (error) {
      console.error("Error signing in with Google", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="outline"
      className="w-full py-6 relative"
      disabled={isLoading}
      onClick={handleSignIn}
    >
      <div className="absolute left-4 flex h-5 w-5 items-center">
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M18.1711 8.36788H9.73333V11.6434H14.5223C14.0488 13.8244 12.1066 15.2637 9.73333 15.2637C6.83555 15.2637 4.48888 12.9171 4.48888 10.0193C4.48888 7.12143 6.83555 4.77476 9.73333 4.77476C11.0444 4.77476 12.2355 5.27071 13.1312 6.08232L15.5645 3.64899C14.0311 2.22455 11.9933 1.34454 9.73333 1.34454C4.93777 1.34454 1.05866 5.22365 1.05866 9.99921C1.05866 14.7748 4.93777 18.6744 9.73333 18.6744C14.1023 18.6744 18.1066 15.5304 18.1066 10.0193C18.1066 9.47476 18.1504 8.91232 18.1711 8.36788Z"
            fill="#4285F4"
          />
        </svg>
      </div>
      <span className="text-base font-medium">Continue with Google</span>
      {isLoading && (
        <div className="absolute right-4 flex h-5 w-5 items-center">
          <svg
            className="animate-spin h-5 w-5 text-primary"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        </div>
      )}
    </Button>
  );
};
