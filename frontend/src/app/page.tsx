"use client";

import Link from "next/link";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/layout/navbar";
import { ArrowRight, Trophy, Users, BarChart3 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function Home() {
  const { data: session, status } = useSession();

  return (
    <>
      <Navbar />
      <div className="flex min-h-[calc(100vh-4rem)] flex-col bg-gradient-to-b from-muted/50 to-muted">
        {/* Hero Section */}
        <div className="relative overflow-hidden">
          {/* Decorative background elements */}
          <div className="absolute inset-0 z-0">
            <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl"></div>
            <div className="absolute bottom-10 right-10 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl"></div>
          </div>

          <div className="container mx-auto max-w-5xl px-4 py-20 relative z-10">
            <div className="text-center mb-12">
              <h1 className="mb-6 text-5xl font-bold tracking-tight text-foreground md:text-6xl lg:text-7xl">
                <span className="inline-block animate-fade-in-up">
                  GullyGuru
                </span>{" "}
                <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent inline-block animate-fade-in-up animation-delay-150">
                  Fantasy Cricket
                </span>
              </h1>
              <p className="mb-8 text-xl text-muted-foreground max-w-3xl mx-auto animate-fade-in-up animation-delay-300">
                Create your fantasy cricket team, compete with friends, and
                climb the leaderboards in this ultimate cricket management
                experience.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-8 animate-fade-in-up animation-delay-450">
                {status === "loading" ? (
                  <Skeleton className="h-12 w-48" />
                ) : status === "authenticated" ? (
                  <Button
                    size="lg"
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium group w-full sm:w-auto shadow-sm btn-dashboard"
                    asChild
                  >
                    <Link href="/dashboard" className="flex items-center gap-2">
                      Go to Dashboard
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Link>
                  </Button>
                ) : (
                  <Button
                    size="lg"
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium group w-full sm:w-auto shadow-sm btn-primary-enhanced"
                    asChild
                  >
                    <Link
                      href="/auth/signin"
                      className="flex items-center gap-2"
                    >
                      Sign in with Google
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Link>
                  </Button>
                )}

                <Button
                  size="lg"
                  variant="outline"
                  className="w-full sm:w-auto"
                  asChild
                >
                  <Link href="#features">Learn More</Link>
                </Button>
              </div>

              {status === "unauthenticated" && (
                <p className="mt-4 text-sm text-muted-foreground animate-fade-in-up animation-delay-600">
                  New to GullyGuru? Sign in to create your account.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="py-20 bg-background">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
              Play Like a Pro, Manage Like a Guru
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <FeatureCard
                title="Create Gullies"
                description="Create fantasy leagues and invite your friends to compete in private competitions."
                icon={
                  <Users className="h-10 w-10 p-2 bg-primary/10 text-primary rounded-xl" />
                }
                delay={0}
              />
              <FeatureCard
                title="Draft Squad"
                description="Select your dream team of players within your budget through exciting auction drafts."
                icon={
                  <Trophy className="h-10 w-10 p-2 bg-primary/10 text-primary rounded-xl" />
                }
                delay={150}
              />
              <FeatureCard
                title="Real-time Scoring"
                description="Watch your team earn points as matches happen with our live scoring system."
                icon={
                  <BarChart3 className="h-10 w-10 p-2 bg-primary/10 text-primary rounded-xl" />
                }
                delay={300}
              />
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-primary/10 to-blue-500/10 py-16">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              Ready to start your cricket journey?
            </h2>
            <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join thousands of cricket fans managing their fantasy teams and
              competing for glory.
            </p>

            {status === "loading" ? (
              <Skeleton className="h-12 w-48 mx-auto" />
            ) : (
              <Button
                size="lg"
                className={
                  status === "authenticated"
                    ? "btn-dashboard"
                    : "btn-primary-enhanced"
                }
                asChild
              >
                <Link
                  href={
                    status === "authenticated" ? "/dashboard" : "/auth/signin"
                  }
                  className="flex items-center gap-2"
                >
                  {status === "authenticated" ? (
                    <>
                      Go to Dashboard
                      <ArrowRight className="h-4 w-4" />
                    </>
                  ) : (
                    "Get Started Now"
                  )}
                </Link>
              </Button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  delay: number;
}

function FeatureCard({ title, description, icon, delay }: FeatureCardProps) {
  return (
    <div
      className={`flex flex-col items-center rounded-xl border bg-card p-6 text-card-foreground shadow-sm transition-all hover:shadow-md hover:scale-105 animate-fade-in-up`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="mb-4">{icon}</div>
      <h3 className="mb-2 text-xl font-semibold">{title}</h3>
      <p className="text-center text-muted-foreground">{description}</p>
    </div>
  );
}
