"use client";

import { useParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import {
  ArrowLeft,
  Trophy,
  Clock,
  Users,
  PlusCircle,
  ChevronRight,
  Pencil,
  Sparkles,
  Info,
  Calendar,
  LineChart,
  Medal,
  CheckCircle2,
  HelpCircle,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

// Contest details (in a real app, would be fetched from API)
const CONTEST = {
  id: "c1",
  title: "IPL T20 Mega Contest",
  entryFee: 100,
  totalPrize: 100000,
  startDate: "2025-04-10T14:00:00",
  endDate: "2025-04-10T23:00:00",
  maxEntries: 10000,
  currentEntries: 7851,
  matchup: "MI vs CSK",
  status: "open", // 'open', 'live', 'completed'
  firstPrize: 25000,
  participants: 7851,
  prizeBreakdown: [
    { position: "1st", prize: 25000, winners: 1 },
    { position: "2nd", prize: 15000, winners: 1 },
    { position: "3rd", prize: 10000, winners: 1 },
    { position: "4th-10th", prize: 5000, winners: 7 },
    { position: "11th-100th", prize: 500, winners: 90 },
    { position: "101st-500th", prize: 200, winners: 400 },
  ],
  description:
    "Join the biggest IPL fantasy contest of the season and compete against thousands of cricket fans to win big prizes! Pick your dream team of 11 players from MI and CSK, and watch them score points based on their real-life performance.",
};

// Mock user teams for this contest
const USER_TEAMS = [
  {
    id: "t1",
    name: "Cricket Champions",
    captainName: "Virat Kohli",
    viceCaptainName: "MS Dhoni",
    points: 0, // Points will be awarded once the match starts
    rank: "-", // Rank will be determined once the match starts
    isComplete: true, // Whether team selection is complete
  },
  {
    id: "t2",
    name: "IPL Warriors",
    captainName: "",
    viceCaptainName: "",
    points: 0,
    rank: "-",
    isComplete: false, // Team is incomplete
  },
];

// Format date for display
const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  };
  return new Date(dateString).toLocaleString("en-US", options);
};

// Calculate time remaining for contest start
const getTimeRemaining = (dateString: string) => {
  const now = new Date();
  const target = new Date(dateString);
  const diff = target.getTime() - now.getTime();

  if (diff <= 0) return "Started";

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  if (days > 0) return `${days}d ${hours}h left`;
  if (hours > 0) return `${hours}h ${minutes}m left`;
  return `${minutes}m left`;
};

// Get status for display
const getStatusDisplay = (status: string, startDate: string) => {
  if (status === "completed") return "Completed";
  if (status === "live") return "Live";

  const now = new Date();
  const start = new Date(startDate);
  if (now > start) return "In Progress";

  return "Upcoming";
};

export default function ContestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const contestId = params.contestId as string;
  const [activeTab, setActiveTab] = useState<string>("overview");

  const statusDisplay = getStatusDisplay(CONTEST.status, CONTEST.startDate);
  const timeRemaining = getTimeRemaining(CONTEST.startDate);

  return (
    <div className="container mx-auto py-4 sm:py-6 px-0 sm:px-4">
      <div className="flex flex-col gap-6">
        {/* Header with back button */}
        <div className="flex items-center gap-2 px-4 sm:px-0">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard/contests">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {CONTEST.title}
            </h1>
            <p className="text-muted-foreground">{CONTEST.matchup}</p>
          </div>
        </div>

        {/* Contest Status Card */}
        <Card>
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:justify-between gap-4 sm:gap-6">
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2 sm:gap-3">
                  <Badge
                    className={
                      statusDisplay === "Live"
                        ? "bg-red-100 text-red-800 border-0"
                        : statusDisplay === "Upcoming"
                        ? "bg-blue-100 text-blue-800 border-0"
                        : "bg-green-100 text-green-800 border-0"
                    }
                  >
                    {statusDisplay === "Live" ? (
                      <span className="flex items-center">
                        <span className="animate-pulse w-2 h-2 rounded-full bg-red-600 mr-1.5"></span>
                        LIVE
                      </span>
                    ) : (
                      statusDisplay
                    )}
                  </Badge>
                  {statusDisplay === "Upcoming" && (
                    <Badge
                      variant="outline"
                      className="flex items-center gap-1"
                    >
                      <Clock className="h-3 w-3" />
                      {timeRemaining}
                    </Badge>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Entry Fee:</span>
                    <span className="font-medium">₹{CONTEST.entryFee}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Total Prize:</span>
                    <span className="font-medium">
                      ₹{CONTEST.totalPrize.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">First Prize:</span>
                    <span className="font-medium">
                      ₹{CONTEST.firstPrize.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Start Time:</span>
                    <span className="font-medium">
                      {formatDate(CONTEST.startDate)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1 space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        Participants:
                      </span>
                      <span className="font-medium">
                        {CONTEST.currentEntries}/{CONTEST.maxEntries}
                      </span>
                    </div>
                    <Progress
                      value={
                        (CONTEST.currentEntries / CONTEST.maxEntries) * 100
                      }
                      className="h-1.5"
                    />
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-3 sm:items-end justify-end">
                <div className="bg-muted p-3 rounded-lg text-center sm:text-right w-full sm:w-auto">
                  <div className="text-sm text-muted-foreground mb-1">
                    Your Teams
                  </div>
                  <div className="text-xl sm:text-2xl font-bold">
                    {USER_TEAMS.length} / 3
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Max 3 teams allowed
                  </div>
                </div>

                <Button className="w-full sm:w-auto" asChild>
                  <Link href={`/dashboard/contests/${contestId}/create-team`}>
                    <PlusCircle className="h-4 w-4 mr-1.5" />
                    Create Another Team
                  </Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contest Details Tabs */}
        <Card>
          <CardHeader className="p-0">
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full"
            >
              <TabsList className="w-full justify-start p-0 h-12 bg-transparent border-b rounded-none overflow-x-auto flex-nowrap">
                <TabsTrigger
                  value="overview"
                  className="flex-none px-4 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
                >
                  <span className="flex items-center gap-1.5">
                    <Info className="h-4 w-4" />
                    <span>Overview</span>
                  </span>
                </TabsTrigger>
                <TabsTrigger
                  value="my-teams"
                  className="flex-none px-4 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
                >
                  <span className="flex items-center gap-1.5">
                    <Users className="h-4 w-4" />
                    <span>My Teams</span>
                  </span>
                </TabsTrigger>
                <TabsTrigger
                  value="leaderboard"
                  className="flex-none px-4 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
                >
                  <span className="flex items-center gap-1.5">
                    <LineChart className="h-4 w-4" />
                    <span>Leaderboard</span>
                  </span>
                </TabsTrigger>
                <TabsTrigger
                  value="prizes"
                  className="flex-none px-4 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
                >
                  <span className="flex items-center gap-1.5">
                    <Trophy className="h-4 w-4" />
                    <span>Prizes</span>
                  </span>
                </TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="p-6 space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-2 flex items-center">
                    <Info className="h-5 w-5 mr-2 text-muted-foreground" />
                    Contest Details
                  </h3>
                  <p className="text-muted-foreground">{CONTEST.description}</p>
                </div>

                <Separator />

                <div>
                  <h3 className="text-lg font-medium mb-3 flex items-center">
                    <Calendar className="h-5 w-5 mr-2 text-muted-foreground" />
                    Timeline
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center text-green-700 mt-0.5">
                        <CheckCircle2 className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium">Registration Open</p>
                        <p className="text-sm text-muted-foreground">
                          You can join this contest and create up to 3 teams
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 mt-0.5">
                        <Clock className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium">Contest Start</p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(CONTEST.startDate)} • Match begins
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-orange-100 flex items-center justify-center text-orange-700 mt-0.5">
                        <HelpCircle className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium">Live Scoring</p>
                        <p className="text-sm text-muted-foreground">
                          Points update in real-time as the match progresses
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center text-purple-700 mt-0.5">
                        <Medal className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium">Contest End</p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(CONTEST.endDate)} • Final results & prizes
                          distributed
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <Separator />

                <div>
                  <h3 className="text-lg font-medium mb-3 flex items-center">
                    <Sparkles className="h-5 w-5 mr-2 text-muted-foreground" />
                    Scoring System
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="border-dashed bg-card/50">
                      <CardHeader className="py-3">
                        <CardTitle className="text-base">
                          Batting Points
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="py-0">
                        <ul className="space-y-1.5 text-sm">
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              Run Scored
                            </span>
                            <span>1 point</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              Boundary Bonus
                            </span>
                            <span>1 point</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              Six Bonus
                            </span>
                            <span>2 points</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              30+ Run Bonus
                            </span>
                            <span>5 points</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              Half Century
                            </span>
                            <span>10 points</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              Century
                            </span>
                            <span>20 points</span>
                          </li>
                        </ul>
                      </CardContent>
                    </Card>

                    <Card className="border-dashed bg-card/50">
                      <CardHeader className="py-3">
                        <CardTitle className="text-base">
                          Bowling Points
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="py-0">
                        <ul className="space-y-1.5 text-sm">
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              Wicket
                            </span>
                            <span>25 points</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              LBW/Bowled Bonus
                            </span>
                            <span>8 points</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              Maiden Over
                            </span>
                            <span>12 points</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              3+ Wicket Bonus
                            </span>
                            <span>10 points</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">
                              5 Wicket Haul
                            </span>
                            <span>25 points</span>
                          </li>
                        </ul>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </TabsContent>

              {/* My Teams Tab */}
              <TabsContent value="my-teams" className="p-6 space-y-4">
                {USER_TEAMS.length > 0 ? (
                  <div className="space-y-4">
                    {USER_TEAMS.map((team) => (
                      <Card
                        key={team.id}
                        className={!team.isComplete ? "border-dashed" : ""}
                      >
                        <CardContent className="p-4">
                          <div className="flex justify-between items-center">
                            <div>
                              <h3 className="font-medium">{team.name}</h3>
                              {team.isComplete ? (
                                <p className="text-sm text-muted-foreground">
                                  C: {team.captainName} • VC:{" "}
                                  {team.viceCaptainName}
                                </p>
                              ) : (
                                <p className="text-sm text-amber-600 flex items-center">
                                  <AlertCircle className="h-3.5 w-3.5 mr-1" />
                                  Incomplete team
                                </p>
                              )}
                            </div>

                            <div className="flex items-center gap-4">
                              {CONTEST.status === "live" ||
                              CONTEST.status === "completed" ? (
                                <div className="text-center">
                                  <div className="text-sm text-muted-foreground">
                                    Points
                                  </div>
                                  <div className="font-medium">
                                    {team.points}
                                  </div>
                                </div>
                              ) : null}

                              {CONTEST.status === "live" ||
                              CONTEST.status === "completed" ? (
                                <div className="text-center">
                                  <div className="text-sm text-muted-foreground">
                                    Rank
                                  </div>
                                  <div className="font-medium">{team.rank}</div>
                                </div>
                              ) : null}

                              <Button
                                variant={
                                  team.isComplete ? "outline" : "default"
                                }
                                size="sm"
                                asChild
                              >
                                <Link
                                  href={`/dashboard/contests/${contestId}/create-team?team=${team.id}`}
                                >
                                  {team.isComplete ? (
                                    <>
                                      <Pencil className="h-3.5 w-3.5 mr-1.5" />{" "}
                                      Edit
                                    </>
                                  ) : (
                                    <>
                                      <PlusCircle className="h-3.5 w-3.5 mr-1.5" />{" "}
                                      Complete
                                    </>
                                  )}
                                </Link>
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}

                    {USER_TEAMS.length < 3 && (
                      <Button
                        variant="outline"
                        className="w-full h-20 border-dashed"
                        asChild
                      >
                        <Link
                          href={`/dashboard/contests/${contestId}/create-team`}
                        >
                          <PlusCircle className="h-5 w-5 mr-2" />
                          Create Another Team ({USER_TEAMS.length}/3)
                        </Link>
                      </Button>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                      <Users className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-medium mb-2">No Teams Yet</h3>
                    <p className="text-muted-foreground mb-4">
                      You haven&apos;t created any teams for this contest yet.
                    </p>
                    <Button asChild>
                      <Link
                        href={`/dashboard/contests/${contestId}/create-team`}
                      >
                        <PlusCircle className="h-4 w-4 mr-1.5" />
                        Create Your First Team
                      </Link>
                    </Button>
                  </div>
                )}
              </TabsContent>

              {/* Leaderboard Tab */}
              <TabsContent value="leaderboard" className="p-6">
                {CONTEST.status === "open" ? (
                  <div className="text-center py-8">
                    <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                      <LineChart className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-medium mb-2">
                      Leaderboard Not Available
                    </h3>
                    <p className="text-muted-foreground">
                      The leaderboard will be available once the contest begins
                      on {formatDate(CONTEST.startDate)}.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="bg-muted rounded-lg p-4 text-center">
                      <p className="text-muted-foreground">
                        Leaderboard updates in real-time during the match
                      </p>
                    </div>
                    {/* Sample leaderboard would go here */}
                    <div className="text-center py-8">
                      <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                        <Medal className="h-6 w-6 text-muted-foreground" />
                      </div>
                      <h3 className="text-lg font-medium mb-2">
                        Sample Leaderboard
                      </h3>
                      <p className="text-muted-foreground">
                        In a real app, this would display the current rankings
                        of all participants.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              {/* Prizes Tab */}
              <TabsContent value="prizes" className="p-4 sm:p-6">
                <div className="space-y-4 sm:space-y-6">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <h3 className="text-base sm:text-lg font-medium flex items-center">
                      <Trophy className="h-4 sm:h-5 w-4 sm:w-5 mr-2 text-yellow-500" />
                      Prize Pool: ₹{CONTEST.totalPrize.toLocaleString()}
                    </h3>
                    <Badge variant="outline">
                      {CONTEST.prizeBreakdown.reduce(
                        (total, item) => total + item.winners,
                        0
                      )}{" "}
                      Winners
                    </Badge>
                  </div>

                  <div className="space-y-3">
                    {CONTEST.prizeBreakdown.map((prize, index) => (
                      <div
                        key={index}
                        className={`flex flex-col sm:flex-row justify-between gap-3 sm:items-center p-3 sm:p-4 rounded-lg ${
                          index === 0
                            ? "bg-yellow-100 border-2 border-yellow-300"
                            : index === 1
                            ? "bg-slate-100 border-2 border-slate-300"
                            : index === 2
                            ? "bg-orange-100 border-2 border-orange-300"
                            : "bg-card border"
                        }`}
                      >
                        <div className="flex items-center gap-3 sm:gap-4">
                          {index < 3 ? (
                            <div
                              className={`relative w-12 h-12 sm:w-14 sm:h-14 rounded-full flex items-center justify-center text-lg font-bold border-2 ${
                                index === 0
                                  ? "bg-yellow-300 text-yellow-800 border-yellow-500"
                                  : index === 1
                                  ? "bg-slate-300 text-slate-800 border-slate-500"
                                  : "bg-orange-300 text-orange-800 border-orange-500"
                              }`}
                            >
                              {index === 0 ? "1" : index === 1 ? "2" : "3"}
                            </div>
                          ) : (
                            <div className="w-8 h-8 flex items-center justify-center">
                              <span className="text-muted-foreground text-sm font-medium">
                                {prize.position.split("-")[0]}
                              </span>
                            </div>
                          )}
                          <div className="flex-1">
                            <p
                              className={`${
                                index < 3
                                  ? "font-bold text-base sm:text-lg"
                                  : "font-medium"
                              }`}
                            >
                              {prize.position}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {prize.winners > 1
                                ? `${prize.winners} winners`
                                : "1 winner"}
                            </p>
                          </div>
                        </div>

                        {index < 3 ? (
                          <div className="bg-white px-4 sm:px-5 py-2 sm:py-3 rounded-lg shadow-md border border-gray-100 w-full sm:w-auto">
                            <div className="text-xs uppercase text-muted-foreground mb-1 text-center">
                              Prize
                            </div>
                            <div className="text-xl sm:text-2xl font-black text-center">
                              ₹{prize.prize.toLocaleString()}
                            </div>
                          </div>
                        ) : (
                          <div className="font-bold text-base sm:text-lg text-right">
                            ₹{prize.prize.toLocaleString()}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}
