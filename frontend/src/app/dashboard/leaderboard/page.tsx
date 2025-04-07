"use client";

import { useEffect, useState } from "react";
import { useAppStore } from "@/lib/store";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Award } from "lucide-react";

interface LeaderboardEntry {
  id: number;
  team_name: string;
  points: number;
  rank: number;
  matches_played: number;
  wins: number;
}

export default function LeaderboardPage() {
  const { activeGully } = useAppStore();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);

  useEffect(() => {
    // TODO: Fetch actual leaderboard data from API
    // For now, using mock data
    if (activeGully) {
      const mockLeaderboard: LeaderboardEntry[] = [
        {
          id: 1,
          team_name: "Super Kings",
          points: 450,
          rank: 1,
          matches_played: 10,
          wins: 8,
        },
        {
          id: 2,
          team_name: "Royal Challengers",
          points: 420,
          rank: 2,
          matches_played: 10,
          wins: 7,
        },
        {
          id: 3,
          team_name: "Mumbai Indians",
          points: 380,
          rank: 3,
          matches_played: 10,
          wins: 6,
        },
        {
          id: 4,
          team_name: "Knight Riders",
          points: 320,
          rank: 4,
          matches_played: 10,
          wins: 5,
        },
        {
          id: 5,
          team_name: "Capitals",
          points: 300,
          rank: 5,
          matches_played: 10,
          wins: 4,
        },
      ];
      setLeaderboard(mockLeaderboard);
    }
  }, [activeGully]);

  if (!activeGully) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardContent className="py-6">
            <p className="text-center text-muted-foreground">
              Please select a gully first to view the leaderboard.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Leaderboard</h1>
          <p className="text-muted-foreground">
            Current standings for {activeGully.name}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Overall Rankings</CardTitle>
            <CardDescription>
              Team rankings based on total points
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {leaderboard.map((entry) => (
                <div
                  key={entry.id}
                  className={`flex items-center justify-between p-4 rounded-lg ${
                    entry.rank === 1
                      ? "bg-yellow-50 dark:bg-yellow-950/20"
                      : entry.rank === 2
                      ? "bg-gray-50 dark:bg-gray-950/20"
                      : entry.rank === 3
                      ? "bg-orange-50 dark:bg-orange-950/20"
                      : "bg-background"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                        entry.rank === 1
                          ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300"
                          : entry.rank === 2
                          ? "bg-gray-100 text-gray-700 dark:bg-gray-900/50 dark:text-gray-300"
                          : entry.rank === 3
                          ? "bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {entry.rank}
                    </div>
                    <div>
                      <p className="font-medium">{entry.team_name}</p>
                      <p className="text-sm text-muted-foreground">
                        Matches: {entry.matches_played} | Wins: {entry.wins}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-2xl font-bold">{entry.points}</p>
                      <p className="text-sm text-muted-foreground">Points</p>
                    </div>
                    {entry.rank <= 3 && (
                      <Award
                        className={`h-6 w-6 ${
                          entry.rank === 1
                            ? "text-yellow-500"
                            : entry.rank === 2
                            ? "text-gray-400"
                            : "text-orange-600"
                        }`}
                      />
                    )}
                  </div>
                </div>
              ))}

              {leaderboard.length === 0 && (
                <p className="text-center text-muted-foreground py-4">
                  No leaderboard data available yet.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
