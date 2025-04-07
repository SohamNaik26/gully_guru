import { getServerSession } from "next-auth/next";
import { redirect } from "next/navigation";
import { authOptions } from "../../api/auth/[...nextauth]/route";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { SignInButton } from "@/components/auth/signin-button";
import Navbar from "@/components/layout/navbar";

export default async function SignInPage() {
  const session = await getServerSession(authOptions);

  // Redirect to dashboard if already signed in
  if (session) {
    redirect("/dashboard");
  }

  return (
    <>
      <Navbar />
      <main className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-muted/50 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">Sign in to GullyGuru</CardTitle>
            <CardDescription>
              Continue with Google to access your fantasy cricket leagues
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <SignInButton />
          </CardContent>
          <CardFooter className="flex flex-col gap-2">
            <div className="text-center text-sm text-muted-foreground">
              By signing in, you agree to our{" "}
              <Link href="/terms" className="underline underline-offset-4 hover:text-primary">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href="/privacy" className="underline underline-offset-4 hover:text-primary">
                Privacy Policy
              </Link>
              .
            </div>
          </CardFooter>
        </Card>
      </main>
    </>
  );
} 