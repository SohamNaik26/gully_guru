"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useAppStore } from "@/lib/store";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { gullyApi, userApi } from "@/lib/api-client";
import {
  ChevronRight,
  Plus,
  TrendingUp,
  Users,
  Award,
  Trophy,
  ArrowRight,
  Calendar,
  Clock,
  AlertCircle,
  Activity,
  BarChart,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

export default function DashboardPage() {
  const { data: session } = useSession();
  const {
    currentUser,
    setCurrentUser,
    userGullies,
    setUserGullies,
    setActiveGully,
  } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);
  const [animationPlayed, setAnimationPlayed] = useState(false);

  // Fetch user data and gullies on component mount
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setIsLoading(true);

        // Fetch current user details
        const user = await userApi.getCurrentUser();
        if (user) {
          setCurrentUser(user);

          try {
            // Fetch user's gullies
            const gullies = await gullyApi.getUserGullies(user.id);
            if (Array.isArray(gullies)) {
              setUserGullies(gullies);

              // Set active gully if exists
              if (gullies.length > 0) {
                setActiveGully(gullies[0]);
              }
            } else {
              console.warn("Received invalid gullies data:", gullies);
              setUserGullies([]);
            }
          } catch (gullyError) {
            console.error("Error fetching gullies:", gullyError);
            toast.error("Failed to load your gullies data.");
            setUserGullies([]);
          }
        } else {
          // If no user was found/returned
          console.warn("No user data retrieved");
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
        toast.error("Failed to load your data. Please try again.");
      } finally {
        setIsLoading(false);
        // Set animation played state after a short delay
        setTimeout(() => setAnimationPlayed(true), 100);
      }
    };

    if (session?.user?.email) {
      fetchUserData();
    } else {
      setIsLoading(false);
      // Set animation played state after a short delay
      setTimeout(() => setAnimationPlayed(true), 100);
    }
  }, [session, setCurrentUser, setUserGullies, setActiveGully]);

  // Generate greeting based on time of day
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  // Customize badge based on gully status
  const getBadgeVariant = (status: string) => {
    if (status === "active" || status === "draft") return "success";
    if (status === "completed") return "secondary";
    return "secondary";
  };

  if (isLoading) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <div className="text-center">
          <div className="relative h-16 w-16 mx-auto mb-4">
            <div className="animate-ping absolute h-16 w-16 rounded-full bg-primary/10"></div>
            <div className="animate-spin relative h-16 w-16 border-b-4 border-primary rounded-full"></div>
          </div>
          <p className="text-xl text-muted-foreground">
            Loading your dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className={`space-y-8 ${animationPlayed ? "" : "animate-fade-in"}`}>
        {/* Dashboard Header with Summary Stats */}
        <div className="p-6 rounded-xl bg-gradient-to-r from-primary/10 via-background to-blue-500/10">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
            <div>
              <h1 className="text-3xl font-bold tracking-tight mb-1">
                {getGreeting()},{" "}
                {currentUser?.full_name ||
                  session?.user?.name?.split(" ")[0] ||
                  "Cricket Fan"}
                !
              </h1>
              <p className="text-muted-foreground">
                Manage your fantasy cricket leagues and view your performance
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                asChild
                variant="secondary"
                size="sm"
                className="flex items-center gap-1"
              >
                <Link href="/dashboard/team">
                  <Trophy className="h-4 w-4 mr-1 text-primary" />
                  My Team
                </Link>
              </Button>
              <Button asChild className="flex items-center gap-1">
                <Link href="/dashboard/gullies/create">
                  <Plus className="h-4 w-4 mr-1" />
                  Create Gully
                </Link>
              </Button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
            <Card className="bg-background/60 border border-border/30 backdrop-blur-sm">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Gullies</p>
                  <p className="text-2xl font-bold">
                    {userGullies?.length || 0}
                  </p>
                </div>
                <Users className="h-8 w-8 text-primary opacity-70" />
              </CardContent>
            </Card>
            <Card className="bg-background/60 border border-border/30 backdrop-blur-sm">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Players</p>
                  <p className="text-2xl font-bold">15</p>
                </div>
                <TrendingUp className="h-8 w-8 text-blue-500 opacity-70" />
              </CardContent>
            </Card>
            <Card className="bg-background/60 border border-border/30 backdrop-blur-sm">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Won Auctions</p>
                  <p className="text-2xl font-bold">3</p>
                </div>
                <Award className="h-8 w-8 text-amber-500 opacity-70" />
              </CardContent>
            </Card>
            <Card className="bg-background/60 border border-border/30 backdrop-blur-sm">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Total Points</p>
                  <p className="text-2xl font-bold">550</p>
                </div>
                <BarChart className="h-8 w-8 text-green-500 opacity-70" />
              </CardContent>
            </Card>
          </div>
        </div>

        <Tabs defaultValue="gullies" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 rounded-lg">
            <TabsTrigger value="gullies" className="rounded-md">
              My Gullies
            </TabsTrigger>
            <TabsTrigger value="stats" className="rounded-md">
              Stats & Performance
            </TabsTrigger>
            <TabsTrigger value="activity" className="rounded-md">
              Recent Activity
            </TabsTrigger>
          </TabsList>

          <TabsContent value="gullies" className="space-y-6 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {userGullies && userGullies.length > 0 ? (
                userGullies.map((gully, index) => (
                  <Card
                    key={gully.id}
                    className={`overflow-hidden transition hover:shadow-md bg-background ${
                      animationPlayed ? "" : "animate-fade-in-up"
                    }`}
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="flex flex-row items-center justify-between pb-2 border-b">
                      <div>
                        <div className="flex items-center">
                          <CardTitle>{gully.name}</CardTitle>
                          <Badge
                            variant={getBadgeVariant(gully.status)}
                            className="ml-2"
                          >
                            {gully.status}
                          </Badge>
                        </div>
                        <CardDescription className="mt-1">
                          Cricket league with friends
                        </CardDescription>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4">
                      <div className="grid grid-cols-3 gap-2 text-center text-sm">
                        <div className="flex flex-col items-center p-2 bg-muted/50 rounded-lg">
                          <Users className="h-4 w-4 mb-1 text-primary/70" />
                          <span className="text-xs text-muted-foreground">
                            Participants
                          </span>
                          <span className="font-bold">12</span>
                        </div>
                        <div className="flex flex-col items-center p-2 bg-muted/50 rounded-lg">
                          <Trophy className="h-4 w-4 mb-1 text-amber-500/70" />
                          <span className="text-xs text-muted-foreground">
                            Your Rank
                          </span>
                          <span className="font-bold">4th</span>
                        </div>
                        <div className="flex flex-col items-center p-2 bg-muted/50 rounded-lg">
                          <Activity className="h-4 w-4 mb-1 text-blue-500/70" />
                          <span className="text-xs text-muted-foreground">
                            Points
                          </span>
                          <span className="font-bold">320</span>
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter className="border-t pt-3 pb-3 flex justify-between items-center">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-muted-foreground mr-1" />
                        <span className="text-xs text-muted-foreground">
                          Next match in 2 days
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="group"
                        asChild
                        onClick={() => setActiveGully(gully)}
                      >
                        <Link
                          href={`/dashboard/gullies/${gully.id}`}
                          className="flex items-center"
                        >
                          View Details
                          <ChevronRight className="h-4 w-4 ml-1 transition-transform group-hover:translate-x-1" />
                        </Link>
                      </Button>
                    </CardFooter>
                  </Card>
                ))
              ) : (
                <Card className="col-span-full bg-muted/20 animate-fade-in">
                  <CardHeader>
                    <CardTitle>No Gullies Yet</CardTitle>
                    <CardDescription>
                      Create a new Gully or join an existing one to get started
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col items-center text-center py-8">
                    <div className="rounded-full p-4 bg-muted mb-4">
                      <Users className="h-10 w-10 text-muted-foreground" />
                    </div>
                    <p className="text-muted-foreground mb-6">
                      You haven&apos;t joined any cricket leagues yet. Create
                      your first Gully to start competing with friends!
                    </p>
                    <Button size="lg" className="px-6" asChild>
                      <Link
                        href="/dashboard/gullies/create"
                        className="flex items-center gap-2"
                      >
                        <Plus className="h-4 w-4" />
                        Create Your First Gully
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              )}

              <Card
                className={`bg-gradient-to-br from-primary/5 to-blue-500/5 hover:shadow-md transition border-dashed animate-fade-in`}
                style={{ animationDelay: "300ms" }}
              >
                <CardHeader>
                  <CardTitle>Create a New Gully</CardTitle>
                  <CardDescription>
                    Start a new fantasy cricket league with your friends
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center p-6 text-center">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                    <Plus className="h-8 w-8 text-primary" />
                  </div>
                  <p className="text-muted-foreground mb-4">
                    Invite friends, draft players, and compete for glory!
                  </p>
                  <Button asChild className="group">
                    <Link
                      href="/dashboard/gullies/create"
                      className="flex items-center gap-1"
                    >
                      Get Started
                      <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="stats" className="space-y-6 animate-fade-in">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Trophy className="mr-2 h-5 w-5 text-primary" />
                  Your Cricket Performance
                </CardTitle>
                <CardDescription>
                  Summary of your performance across all leagues
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex flex-col items-center justify-center bg-muted/30 rounded-lg p-4">
                    <span className="text-4xl font-bold text-primary">
                      {userGullies?.length || 0}
                    </span>
                    <span className="text-sm text-muted-foreground mt-1">
                      Gullies Joined
                    </span>
                  </div>
                  <div className="flex flex-col items-center justify-center bg-muted/30 rounded-lg p-4">
                    <span className="text-4xl font-bold text-blue-500">15</span>
                    <span className="text-sm text-muted-foreground mt-1">
                      Players Owned
                    </span>
                  </div>
                  <div className="flex flex-col items-center justify-center bg-muted/30 rounded-lg p-4">
                    <span className="text-4xl font-bold text-amber-500">3</span>
                    <span className="text-sm text-muted-foreground mt-1">
                      Auctions Won
                    </span>
                  </div>
                  <div className="flex flex-col items-center justify-center bg-muted/30 rounded-lg p-4">
                    <span className="text-4xl font-bold text-green-500">
                      550
                    </span>
                    <span className="text-sm text-muted-foreground mt-1">
                      Total Points
                    </span>
                  </div>
                </div>

                {/* Player Type Breakdown */}
                <div className="rounded-lg border p-4">
                  <h3 className="font-medium mb-3">Your Squad Composition</h3>
                  <div className="space-y-3">
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Batsmen</span>
                        <span className="font-medium">6 players</span>
                      </div>
                      <Progress value={40} className="h-2" />
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Bowlers</span>
                        <span className="font-medium">5 players</span>
                      </div>
                      <Progress value={33} className="h-2" />
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">
                          All-rounders
                        </span>
                        <span className="font-medium">3 players</span>
                      </div>
                      <Progress value={20} className="h-2" />
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">
                          Wicket-keepers
                        </span>
                        <span className="font-medium">1 player</span>
                      </div>
                      <Progress value={7} className="h-2" />
                    </div>
                  </div>
                </div>

                <div className="flex justify-center">
                  <Button variant="outline" asChild>
                    <Link
                      href="/dashboard/stats"
                      className="flex items-center gap-1"
                    >
                      View Detailed Stats
                      <ArrowRight className="ml-1 h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="activity" className="space-y-4 animate-fade-in">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Activity className="mr-2 h-5 w-5 text-primary" />
                    Recent Activities
                  </CardTitle>
                  <CardDescription>
                    Latest updates from your gullies
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  View All
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-5">
                  <ActivityItem
                    icon={<Calendar className="h-5 w-5 text-blue-500" />}
                    title="IPL 2023 Auction Scheduled"
                    description="The auction for IPL 2023 has been scheduled for May 15th, 2023."
                    timestamp="2 hours ago"
                    className="animate-fade-in-up"
                    style={{ animationDelay: "0ms" }}
                  />

                  <ActivityItem
                    icon={<Trophy className="h-5 w-5 text-amber-500" />}
                    title="You won a bidding war!"
                    description="You successfully acquired Virat Kohli for ₹12,500,000"
                    timestamp="Yesterday"
                    className="animate-fade-in-up"
                    style={{ animationDelay: "100ms" }}
                  />

                  <ActivityItem
                    icon={<Users className="h-5 w-5 text-green-500" />}
                    title="New Member Joined"
                    description="Rohit Sharma joined IPL Fantasy League 2023"
                    timestamp="2 days ago"
                    className="animate-fade-in-up"
                    style={{ animationDelay: "200ms" }}
                  />

                  <ActivityItem
                    icon={<AlertCircle className="h-5 w-5 text-red-500" />}
                    title="Player Injury Update"
                    description="Jasprit Bumrah is injured and might miss the next 2 matches"
                    timestamp="3 days ago"
                    className="animate-fade-in-up"
                    style={{ animationDelay: "300ms" }}
                  />

                  <ActivityItem
                    icon={<Award className="h-5 w-5 text-primary" />}
                    title="Points Updated"
                    description="You earned 45 points from yesterday's match"
                    timestamp="4 days ago"
                    className="animate-fade-in-up"
                    style={{ animationDelay: "400ms" }}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Add reusable animations */}
      <style jsx global>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fadeIn 0.5s ease-out forwards;
        }

        .animate-fade-in-up {
          animation: fadeInUp 0.5s ease-out forwards;
        }
      `}</style>
    </div>
  );
}

// Activity Item component with proper TypeScript types
interface ActivityItemProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  timestamp: string;
  className?: string;
  style?: React.CSSProperties;
}

function ActivityItem({
  icon,
  title,
  description,
  timestamp,
  className = "",
  style = {},
}: ActivityItemProps) {
  return (
    <div
      className={`flex items-start gap-4 border-b pb-4 last:border-0 last:pb-0 ${className}`}
      style={style}
    >
      <div className="rounded-full bg-muted p-2 mt-0.5">{icon}</div>
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <p className="font-medium">{title}</p>
          <span className="text-xs text-muted-foreground">{timestamp}</span>
        </div>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}
