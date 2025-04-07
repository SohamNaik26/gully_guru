"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, Trophy, Users, Clock, Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAppStore } from "@/lib/store";
import { toast } from "sonner";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

interface Player {
  id: number;
  name: string;
  team: string;
  role: string;
  points: number;
  image: string;
  stats: {
    runs?: number;
    wickets?: number;
    catches?: number;
    stumpings?: number;
    ballsFaced?: number;
    strikeRate?: number;
    overs?: number;
    economy?: number;
  };
}

interface Team {
  id: number;
  name: string;
  points: number;
  logo: string;
  players: Player[];
}

interface Match {
  id: number;
  status: "upcoming" | "live" | "completed";
  team1: Team;
  team2: Team;
  startTime: string;
  venue: string;
}

export default function MatchDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { currentUser } = useAppStore();
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatchDetails = async () => {
      try {
        setLoading(true);
        // In development, use mock data
        const mockMatch = {
          id: Number(params.id),
          status: "completed",
          startTime: "2024-03-25T14:00:00Z",
          venue: "M. Chinnaswamy Stadium, Bangalore",
          team1: {
            id: 1,
            name: "Royal Challengers Bangalore",
            points: 120,
            logo: "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RCB/Logo/RCBlogo.png",
            players: [
              {
                id: 1,
                name: "Virat Kohli",
                team: "RCB",
                role: "Batsman",
                points: 45,
                image:
                  "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/2.png",
                stats: {
                  runs: 82,
                  ballsFaced: 54,
                  strikeRate: 151.85,
                  catches: 1,
                },
              },
              {
                id: 2,
                name: "Glenn Maxwell",
                team: "RCB",
                role: "All-rounder",
                points: 35,
                image:
                  "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/210.png",
                stats: {
                  runs: 28,
                  ballsFaced: 15,
                  strikeRate: 186.67,
                  wickets: 2,
                  overs: 4,
                  economy: 7.5,
                },
              },
              {
                id: 3,
                name: "Mohammed Siraj",
                team: "RCB",
                role: "Bowler",
                points: 40,
                image:
                  "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/63.png",
                stats: {
                  wickets: 3,
                  overs: 4,
                  economy: 6.75,
                },
              },
            ],
          },
          team2: {
            id: 2,
            name: "Chennai Super Kings",
            points: 85,
            logo: "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/CSK/logos/CSKlogo.png",
            players: [
              {
                id: 4,
                name: "MS Dhoni",
                team: "CSK",
                role: "Wicket-keeper",
                points: 30,
                image:
                  "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/57.png",
                stats: {
                  runs: 24,
                  ballsFaced: 12,
                  strikeRate: 200.0,
                  stumpings: 1,
                },
              },
              {
                id: 5,
                name: "Ravindra Jadeja",
                team: "CSK",
                role: "All-rounder",
                points: 25,
                image:
                  "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/46.png",
                stats: {
                  runs: 18,
                  ballsFaced: 15,
                  strikeRate: 120.0,
                  wickets: 1,
                  overs: 4,
                  economy: 8.25,
                },
              },
              {
                id: 6,
                name: "Deepak Chahar",
                team: "CSK",
                role: "Bowler",
                points: 30,
                image:
                  "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/91.png",
                stats: {
                  wickets: 2,
                  overs: 4,
                  economy: 7.75,
                },
              },
            ],
          },
        };
        setMatch(mockMatch);
      } catch (error) {
        console.error("Error fetching match details:", error);
        toast.error("Failed to load match details");
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchMatchDetails();
    }
  }, [params.id]);

  const renderPlayerStats = (player: Player) => {
    const stats = [];

    if (player.stats.runs !== undefined) {
      stats.push(
        `${player.stats.runs} runs (${player.stats.ballsFaced} balls, SR: ${player.stats.strikeRate})`
      );
    }

    if (player.stats.wickets !== undefined) {
      stats.push(
        `${player.stats.wickets} wickets (${player.stats.overs} overs, Eco: ${player.stats.economy})`
      );
    }

    if (player.stats.catches) {
      stats.push(
        `${player.stats.catches} catch${player.stats.catches > 1 ? "es" : ""}`
      );
    }

    if (player.stats.stumpings) {
      stats.push(
        `${player.stats.stumpings} stumping${
          player.stats.stumpings > 1 ? "s" : ""
        }`
      );
    }

    return stats.join(", ");
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <h2 className="text-xl font-semibold mb-2">Match Not Found</h2>
          <p className="text-muted-foreground mb-4">
            The match you are looking for could not be found.
          </p>
          <Link href="/matches">
            <Button variant="outline">View All Matches</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 max-w-6xl">
      <div className="flex flex-col gap-8">
        <div className="flex items-center justify-between bg-card p-4 rounded-lg shadow-sm">
          <div className="flex items-center gap-6">
            <Link href="/matches">
              <Button variant="ghost" size="icon" className="hover:bg-accent">
                <ChevronLeft className="h-5 w-5 text-muted-foreground" />
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-semibold text-foreground mb-2">
                Match Details
              </h1>
              <div className="flex items-center gap-3 text-base text-muted-foreground bg-background/50 p-2 rounded-md">
                <Image
                  src={match.team1.logo}
                  alt={match.team1.name}
                  width={28}
                  height={28}
                  className="rounded-full"
                />
                <span className="font-medium">{match.team1.name}</span>
                <span className="text-muted-foreground/60">vs</span>
                <Image
                  src={match.team2.logo}
                  alt={match.team2.name}
                  width={28}
                  height={28}
                  className="rounded-full"
                />
                <span className="font-medium">{match.team2.name}</span>
              </div>
            </div>
          </div>
          <Badge
            variant={
              match.status === "live"
                ? "destructive"
                : match.status === "completed"
                ? "secondary"
                : "outline"
            }
            className="capitalize text-base px-4 py-1"
          >
            {match.status}
          </Badge>
        </div>

        <Card className="p-8 shadow-sm bg-card/50">
          <div className="space-y-8">
            <div className="flex items-center justify-between bg-background/50 p-4 rounded-lg">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-primary/70" />
                  <span className="text-base text-muted-foreground">
                    {new Date(match.startTime).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Trophy className="h-5 w-5 text-primary/70" />
                  <span className="text-base text-muted-foreground">
                    {match.venue}
                  </span>
                </div>
              </div>
            </div>

            <Tabs defaultValue="teams" className="space-y-6">
              <TabsList className="grid w-full grid-cols-3 p-1 bg-muted/30">
                <TabsTrigger value="teams" className="text-base py-3">
                  Teams
                </TabsTrigger>
                <TabsTrigger value="points" className="text-base py-3">
                  Points
                </TabsTrigger>
                <TabsTrigger value="stats" className="text-base py-3">
                  Player Stats
                </TabsTrigger>
              </TabsList>

              <TabsContent value="teams" className="space-y-6">
                {[match.team1, match.team2].map((team) => (
                  <Card key={team.id} className="p-6 bg-card/50 shadow-sm">
                    <div className="flex items-center gap-6 mb-8 bg-background/50 p-4 rounded-lg">
                      <Image
                        src={team.logo}
                        alt={team.name}
                        width={56}
                        height={56}
                        className="rounded-full"
                      />
                      <div>
                        <h3 className="text-xl font-semibold text-foreground">
                          {team.name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <Users className="h-4 w-4 text-primary/70" />
                          <span className="text-base text-muted-foreground">
                            {team.players.length} Players
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {team.players.map((player) => (
                        <div
                          key={player.id}
                          className="flex items-center gap-4 p-5 rounded-lg bg-background/50 hover:bg-background/70 transition-colors border border-border/50"
                        >
                          <Avatar className="h-14 w-14 border-2 border-primary/20">
                            <AvatarImage src={player.image} alt={player.name} />
                            <AvatarFallback className="text-lg">
                              {player.name
                                .split(" ")
                                .map((n) => n[0])
                                .join("")}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <p className="font-medium text-base text-foreground mb-1">
                              {player.name}
                            </p>
                            <div className="flex items-center gap-3">
                              <Badge
                                variant="outline"
                                className="text-sm px-2 py-0.5 bg-primary/5"
                              >
                                {player.role}
                              </Badge>
                              <span className="text-sm text-muted-foreground">
                                {player.team}
                              </span>
                            </div>
                          </div>
                          <Badge
                            variant="secondary"
                            className="ml-auto text-base px-3 py-1"
                          >
                            {player.points} pts
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </Card>
                ))}
              </TabsContent>

              <TabsContent value="points">
                <Card className="p-8 bg-card/50 shadow-sm">
                  <div className="space-y-6">
                    {[match.team1, match.team2].map((team) => (
                      <div
                        key={team.id}
                        className="flex items-center gap-6 p-5 rounded-lg bg-background/50 border border-border/50"
                      >
                        <Image
                          src={team.logo}
                          alt={team.name}
                          width={48}
                          height={48}
                          className="rounded-full"
                        />
                        <span className="font-medium text-lg flex-1">
                          {team.name}
                        </span>
                        <Badge
                          variant="secondary"
                          className="text-lg px-6 py-2"
                        >
                          {team.points} points
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              </TabsContent>

              <TabsContent value="stats">
                <Card className="p-8 bg-card/50 shadow-sm">
                  <div className="space-y-10">
                    {[match.team1, match.team2].map((team) => (
                      <div key={team.id} className="space-y-6">
                        <div className="flex items-center gap-4 bg-background/50 p-4 rounded-lg">
                          <Image
                            src={team.logo}
                            alt={team.name}
                            width={40}
                            height={40}
                            className="rounded-full"
                          />
                          <h3 className="text-xl font-semibold">{team.name}</h3>
                        </div>
                        <div className="grid grid-cols-1 gap-5">
                          {team.players.map((player) => (
                            <div
                              key={player.id}
                              className="flex items-center gap-6 p-5 rounded-lg bg-background/50 border border-border/50"
                            >
                              <Avatar className="h-14 w-14 border-2 border-primary/20">
                                <AvatarImage
                                  src={player.image}
                                  alt={player.name}
                                />
                                <AvatarFallback className="text-lg">
                                  {player.name
                                    .split(" ")
                                    .map((n) => n[0])
                                    .join("")}
                                </AvatarFallback>
                              </Avatar>
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <p className="font-medium text-lg">
                                    {player.name}
                                  </p>
                                  <Badge
                                    variant="outline"
                                    className="text-sm px-2 py-0.5 bg-primary/5"
                                  >
                                    {player.role}
                                  </Badge>
                                </div>
                                <p className="text-base text-muted-foreground leading-relaxed">
                                  {renderPlayerStats(player)}
                                </p>
                              </div>
                              <Badge
                                variant="secondary"
                                className="ml-auto text-base px-3 py-1"
                              >
                                {player.points} pts
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </Card>
      </div>
    </div>
  );
}
