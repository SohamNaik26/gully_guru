"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Trophy,
  Calendar,
  Users,
  Clock,
  ChevronRight,
  CircleDollarSign,
} from "lucide-react";
import Link from "next/link";

// Sample contest data
const upcomingContests = [
  {
    id: "c1",
    title: "IPL T20 Mega Contest",
    entryFee: 100,
    totalPrize: 100000,
    startDate: "2025-04-10T14:00:00",
    endDate: "2025-04-10T23:00:00",
    maxEntries: 10000,
    currentEntries: 7851,
    matchup: "MI vs CSK",
    firstPrize: 25000,
  },
  {
    id: "c2",
    title: "T20 World Cup Special",
    entryFee: 50,
    totalPrize: 50000,
    startDate: "2025-05-15T18:30:00",
    endDate: "2025-05-15T22:30:00",
    maxEntries: 5000,
    currentEntries: 2319,
    matchup: "IND vs AUS",
    firstPrize: 10000,
  },
  {
    id: "c3",
    title: "Rookie Challenge",
    entryFee: 20,
    totalPrize: 10000,
    startDate: "2025-04-12T16:00:00",
    endDate: "2025-04-12T20:00:00",
    maxEntries: 1000,
    currentEntries: 456,
    matchup: "RCB vs KKR",
    firstPrize: 2000,
  },
];

const activeContests = [
  {
    id: "a1",
    title: "Weekend Showdown",
    entryFee: 75,
    totalPrize: 75000,
    startDate: "2025-04-05T14:00:00",
    endDate: "2025-04-05T23:00:00",
    maxEntries: 5000,
    currentEntries: 4892,
    matchup: "DC vs SRH",
    firstPrize: 15000,
    joined: true,
    myTeams: 2,
  },
];

const completedContests = [
  {
    id: "p1",
    title: "Season Opener",
    entryFee: 100,
    totalPrize: 100000,
    startDate: "2025-03-20T14:00:00",
    endDate: "2025-03-20T23:00:00",
    maxEntries: 10000,
    currentEntries: 9547,
    matchup: "CSK vs RCB",
    firstPrize: 25000,
    joined: true,
    myTeams: 1,
    myBestRank: 156,
    myWinnings: 500,
  },
  {
    id: "p2",
    title: "Friday Night Clash",
    entryFee: 50,
    totalPrize: 50000,
    startDate: "2025-03-25T18:30:00",
    endDate: "2025-03-25T22:30:00",
    maxEntries: 5000,
    currentEntries: 4738,
    matchup: "MI vs LSG",
    firstPrize: 10000,
    joined: true,
    myTeams: 3,
    myBestRank: 1256,
    myWinnings: 0,
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

export default function ContestsPage() {
  const [activeTab, setActiveTab] = useState("upcoming");

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contests</h1>
          <p className="text-muted-foreground">
            Join contests, create teams, and win prizes based on real cricket
            matches
          </p>
        </div>

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-4"
        >
          <TabsList className="w-full justify-start">
            <TabsTrigger value="upcoming" className="flex-1">
              Upcoming
            </TabsTrigger>
            <TabsTrigger value="active" className="flex-1">
              Active
            </TabsTrigger>
            <TabsTrigger value="completed" className="flex-1">
              Completed
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upcoming" className="space-y-4">
            {upcomingContests.map((contest) => (
              <Card key={contest.id}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between">
                    <div>
                      <CardTitle>{contest.title}</CardTitle>
                      <CardDescription className="flex items-center mt-1">
                        <Calendar className="h-4 w-4 mr-1" />
                        {formatDate(contest.startDate)}
                      </CardDescription>
                    </div>
                    <Badge>{contest.matchup}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Entry Fee</p>
                      <p className="font-medium">₹{contest.entryFee}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Prize Pool
                      </p>
                      <p className="font-medium">
                        ₹{contest.totalPrize.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        First Prize
                      </p>
                      <p className="font-medium">
                        ₹{contest.firstPrize.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Entries</p>
                      <div className="flex items-center">
                        <Users className="h-4 w-4 mr-1 text-muted-foreground" />
                        <p className="font-medium">
                          {contest.currentEntries}/{contest.maxEntries}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between items-center pt-2">
                  <Badge variant="outline" className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {getTimeRemaining(contest.startDate)}
                  </Badge>

                  <Button asChild>
                    <Link href={`/dashboard/contests/${contest.id}`}>
                      Join Contest
                      <ChevronRight className="h-4 w-4 ml-1.5" />
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="active" className="space-y-4">
            {activeContests.length > 0 ? (
              activeContests.map((contest) => (
                <Card key={contest.id}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between">
                      <div>
                        <CardTitle>{contest.title}</CardTitle>
                        <CardDescription className="flex items-center mt-1">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(contest.startDate)}
                        </CardDescription>
                      </div>
                      <Badge className="bg-green-100 text-green-800 border-0">
                        <span className="flex items-center">
                          <span className="animate-pulse w-2 h-2 rounded-full bg-green-600 mr-1.5"></span>
                          LIVE
                        </span>
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pb-2">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Matchup</p>
                        <p className="font-medium">{contest.matchup}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Prize Pool
                        </p>
                        <p className="font-medium">
                          ₹{contest.totalPrize.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Your Teams
                        </p>
                        <p className="font-medium">{contest.myTeams} teams</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Entries</p>
                        <div className="flex items-center">
                          <Users className="h-4 w-4 mr-1 text-muted-foreground" />
                          <p className="font-medium">
                            {contest.currentEntries}/{contest.maxEntries}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between items-center pt-2">
                    <Badge variant="outline">In Progress</Badge>

                    <Button asChild>
                      <Link href={`/dashboard/contests/${contest.id}`}>
                        View Live
                        <ChevronRight className="h-4 w-4 ml-1.5" />
                      </Link>
                    </Button>
                  </CardFooter>
                </Card>
              ))
            ) : (
              <div className="text-center py-8">
                <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                  <Trophy className="h-6 w-6 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-medium mb-2">No Active Contests</h3>
                <p className="text-muted-foreground mb-4">
                  You don&apos;t have any active contests right now. Join an
                  upcoming contest to get started!
                </p>
                <Button onClick={() => setActiveTab("upcoming")}>
                  View Upcoming Contests
                </Button>
              </div>
            )}
          </TabsContent>

          <TabsContent value="completed" className="space-y-4">
            {completedContests.map((contest) => (
              <Card key={contest.id}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between">
                    <div>
                      <CardTitle>{contest.title}</CardTitle>
                      <CardDescription className="flex items-center mt-1">
                        <Calendar className="h-4 w-4 mr-1" />
                        {formatDate(contest.startDate)}
                      </CardDescription>
                    </div>
                    <Badge variant="secondary">{contest.matchup}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Your Teams
                      </p>
                      <p className="font-medium">{contest.myTeams} teams</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Best Rank</p>
                      <p className="font-medium">#{contest.myBestRank}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Your Winnings
                      </p>
                      <p className="font-medium flex items-center">
                        <CircleDollarSign className="h-4 w-4 mr-1 text-green-600" />
                        ₹{contest.myWinnings}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Total Prize
                      </p>
                      <p className="font-medium">
                        ₹{contest.totalPrize.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between items-center pt-2">
                  <Badge variant="outline">Completed</Badge>

                  <Button variant="outline" asChild>
                    <Link href={`/dashboard/contests/${contest.id}`}>
                      View Results
                      <ChevronRight className="h-4 w-4 ml-1.5" />
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
