"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MatchCard } from "@/components/matches/match-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Link from "next/link";
import { format } from "date-fns";
import Image from "next/image";
import { teamLogos, teamNames, TeamCode } from "@/lib/data/teamLogos";

// Mock data - replace with real API data
const mockMatches = {
  upcoming: [
    {
      id: "4",
      team1: {
        name: "Gujarat Titans",
        shortName: "GT" as TeamCode,
        logo: teamLogos.GT,
      },
      team2: {
        name: "Lucknow Super Giants",
        shortName: "LSG" as TeamCode,
        logo: teamLogos.LSG,
      },
      startTime: new Date("2025-03-28T14:00:00Z"),
      status: "upcoming",
      contests: {
        totalCount: 50,
        prizePool: 250000,
        entryFee: 49,
        maxTeams: 2000,
        joinedTeams: 1200,
      },
    },
    {
      id: "5",
      team1: {
        name: "Punjab Kings",
        shortName: "PBKS" as TeamCode,
        logo: teamLogos.PBKS,
      },
      team2: {
        name: "Sunrisers Hyderabad",
        shortName: "SRH" as TeamCode,
        logo: teamLogos.SRH,
      },
      startTime: new Date("2025-03-30T14:00:00Z"),
      status: "upcoming",
      contests: {
        totalCount: 45,
        prizePool: 220000,
        entryFee: 39,
        maxTeams: 1800,
        joinedTeams: 900,
      },
    },
  ],
  live: [
    {
      id: "1",
      team1: {
        name: "Mumbai Indians",
        shortName: "MI" as TeamCode,
        logo: teamLogos.MI,
      },
      team2: {
        name: "Royal Challengers Bengaluru",
        shortName: "RCB" as TeamCode,
        logo: teamLogos.RCB,
      },
      startTime: new Date("2025-03-22T14:00:00Z"),
      status: "live",
      contests: {
        totalCount: 100,
        prizePool: 500000,
        entryFee: 49,
        maxTeams: 5000,
        joinedTeams: 4800,
      },
      scores: {
        team1: {
          runs: 128,
          wickets: 2,
          overs: 12.4,
        },
        team2: {
          runs: 0,
          wickets: 0,
          overs: 0,
        },
      },
      liveStats: {
        currentBatsman: [
          {
            name: "Rohit Sharma",
            runs: 65,
            balls: 32,
            fours: 6,
            sixes: 4,
            strikeRate: 203.13,
          },
          {
            name: "Tilak Varma",
            runs: 14,
            balls: 6,
            fours: 1,
            sixes: 1,
            strikeRate: 233.33,
          },
        ],
        currentBowler: {
          name: "Cameron Green",
          overs: 2.4,
          maidens: 0,
          runs: 29,
          wickets: 1,
          economy: 10.88,
        },
        recentBalls: ["4", "W", "0", "6", "0", "1", "4", "1"],
        matchStatus: "MI: 128/2 (12.4) | CRR: 10.11 | Target: -",
      },
    },
    {
      id: "2",
      team1: {
        name: "Chennai Super Kings",
        shortName: "CSK" as TeamCode,
        logo: teamLogos.CSK,
      },
      team2: {
        name: "Kolkata Knight Riders",
        shortName: "KKR" as TeamCode,
        logo: teamLogos.KKR,
      },
      startTime: new Date("2025-03-24T14:00:00Z"),
      status: "live",
      contests: {
        totalCount: 85,
        prizePool: 350000,
        entryFee: 59,
        maxTeams: 3000,
        joinedTeams: 2950,
      },
      scores: {
        team1: {
          runs: 198,
          wickets: 8,
          overs: 20,
        },
        team2: {
          runs: 62,
          wickets: 3,
          overs: 6.4,
        },
      },
      liveStats: {
        currentBatsman: [
          {
            name: "Venkatesh Iyer",
            runs: 14,
            balls: 12,
            fours: 1,
            sixes: 1,
            strikeRate: 116.67,
          },
          {
            name: "Nitish Rana",
            runs: 2,
            balls: 2,
            fours: 0,
            sixes: 0,
            strikeRate: 100.0,
          },
        ],
        currentBowler: {
          name: "Maheesh Theekshana",
          overs: 1.4,
          maidens: 0,
          runs: 9,
          wickets: 1,
          economy: 5.4,
        },
        recentBalls: ["0", "W", "2", "1", "1", "4", "1", "0"],
        matchStatus:
          "KKR: 62/3 (6.4) | CRR: 9.30 | Target: 199 (13.2 overs remaining)",
      },
    },
  ],
  completed: [
    {
      id: "3",
      team1: {
        name: "Delhi Capitals",
        shortName: "DC" as TeamCode,
        logo: teamLogos.DC,
      },
      team2: {
        name: "Punjab Kings",
        shortName: "PBKS" as TeamCode,
        logo: teamLogos.PBKS,
      },
      startTime: new Date("2025-03-26T14:00:00Z"),
      status: "completed",
      contests: {
        totalCount: 40,
        prizePool: 200000,
        entryFee: 39,
        maxTeams: 1500,
        joinedTeams: 1500,
      },
      scores: {
        team1: {
          runs: 204,
          wickets: 7,
          overs: 20,
        },
        team2: {
          runs: 172,
          wickets: 10,
          overs: 18.4,
        },
      },
      result: "DC won by 32 runs",
    },
  ],
} as const;

export default function MatchesPage() {
  const [activeTab, setActiveTab] = useState("upcoming");

  // Add a function to format match details including live scores
  const formatMatchDetails = (match) => {
    if (match.status === "live") {
      const { team1, team2, scores, liveStats } = match;
      return (
        <div className="mt-2">
          <div className="flex justify-between items-center text-sm">
            <div className="font-semibold">
              {team1.shortName}: {scores.team1.runs}/{scores.team1.wickets} (
              {scores.team1.overs})
            </div>
            <div className="px-2 py-1 bg-red-600 text-white text-xs rounded-full animate-pulse">
              LIVE
            </div>
          </div>
          {scores.team2.overs > 0 && (
            <div className="text-sm">
              {team2.shortName}: {scores.team2.runs}/{scores.team2.wickets} (
              {scores.team2.overs})
            </div>
          )}
          <div className="mt-2 text-xs text-gray-400">
            {liveStats.matchStatus}
          </div>
          <div className="mt-2 flex justify-between items-center bg-gray-800 p-2 rounded">
            <div className="text-xs">
              <div className="font-semibold">Batting</div>
              {liveStats.currentBatsman.map((batsman, idx) => (
                <div key={idx} className="flex justify-between">
                  <span>{batsman.name}</span>
                  <span className="ml-2">
                    {batsman.runs} ({batsman.balls})
                  </span>
                </div>
              ))}
            </div>
            <div className="text-xs">
              <div className="font-semibold">Bowling</div>
              <div>{liveStats.currentBowler.name}</div>
              <div>
                {liveStats.currentBowler.overs}-
                {liveStats.currentBowler.maidens}-{liveStats.currentBowler.runs}
                -{liveStats.currentBowler.wickets}
              </div>
            </div>
          </div>
          <div className="mt-2 flex space-x-1">
            {liveStats.recentBalls.map((ball, idx) => (
              <span
                key={idx}
                className={`w-6 h-6 flex items-center justify-center rounded-full text-xs
                  ${
                    ball === "W"
                      ? "bg-red-600 text-white"
                      : ball === "6"
                      ? "bg-purple-600 text-white"
                      : ball === "4"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-700"
                  }`}
              >
                {ball}
              </span>
            ))}
          </div>
        </div>
      );
    } else if (match.status === "completed" && match.scores) {
      const { team1, team2, scores, result } = match;
      return (
        <div className="mt-2">
          <div className="text-sm">
            {team1.shortName}: {scores.team1.runs}/{scores.team1.wickets} (
            {scores.team1.overs})
          </div>
          <div className="text-sm">
            {team2.shortName}: {scores.team2.runs}/{scores.team2.wickets} (
            {scores.team2.overs})
          </div>
          <div className="mt-1 text-xs text-green-400">{result}</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6 text-white">Matches</h1>

      <div className="flex space-x-2 mb-6">
        <Button
          variant={activeTab === "upcoming" ? "default" : "outline"}
          onClick={() => setActiveTab("upcoming")}
          className={
            activeTab === "upcoming"
              ? "bg-blue-600 hover:bg-blue-700"
              : "text-white border-gray-600"
          }
        >
          Upcoming
        </Button>
        <Button
          variant={activeTab === "live" ? "default" : "outline"}
          onClick={() => setActiveTab("live")}
          className={
            activeTab === "live"
              ? "bg-red-600 hover:bg-red-700"
              : "text-white border-gray-600"
          }
        >
          Live
        </Button>
        <Button
          variant={activeTab === "completed" ? "default" : "outline"}
          onClick={() => setActiveTab("completed")}
          className={
            activeTab === "completed"
              ? "bg-green-600 hover:bg-green-700"
              : "text-white border-gray-600"
          }
        >
          Completed
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockMatches[activeTab].map((match) => (
          <Link key={match.id} href={`/matches/${match.id}`}>
            <Card className="hover:border-blue-500 cursor-pointer transition-all bg-gray-900 text-white overflow-hidden">
              <CardContent className="pt-6">
                <div className="flex justify-between items-center">
                  <div className="flex flex-col items-center">
                    <div className="w-16 h-16 bg-white rounded-full p-1">
                      <Image
                        src={match.team1.logo}
                        alt={match.team1.name}
                        width={64}
                        height={64}
                      />
                    </div>
                    <p className="mt-2 text-sm font-medium">
                      {match.team1.shortName}
                    </p>
                  </div>
                  <div className="flex flex-col items-center">
                    <p className="text-xs text-gray-400 mb-1">
                      {format(match.startTime, "MMM d, yyyy")}
                    </p>
                    <p className="text-lg font-bold">VS</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {format(match.startTime, "h:mm a")}
                    </p>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="w-16 h-16 bg-white rounded-full p-1">
                      <Image
                        src={match.team2.logo}
                        alt={match.team2.name}
                        width={64}
                        height={64}
                      />
                    </div>
                    <p className="mt-2 text-sm font-medium">
                      {match.team2.shortName}
                    </p>
                  </div>
                </div>

                {formatMatchDetails(match)}

                <div className="bg-gray-800 rounded p-3 mt-4">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Prize Pool</span>
                    <span>Entry</span>
                    <span>Teams</span>
                  </div>
                  <div className="flex justify-between text-sm mt-1">
                    <span>₹{match.contests.prizePool.toLocaleString()}</span>
                    <span>₹{match.contests.entryFee}</span>
                    <span>
                      {match.contests.joinedTeams}/{match.contests.maxTeams}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
