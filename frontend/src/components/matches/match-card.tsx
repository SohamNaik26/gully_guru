"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { formatDistanceToNow } from "date-fns";
import { Trophy, Users, Clock, ChevronRight } from "lucide-react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface MatchCardProps {
  match: {
    id: string;
    team1: {
      name: string;
      shortName: string;
      logo: string;
    };
    team2: {
      name: string;
      shortName: string;
      logo: string;
    };
    startTime: Date;
    status: "upcoming" | "live" | "completed";
    contests: {
      totalCount: number;
      prizePool: number;
      entryFee: number;
      maxTeams: number;
      joinedTeams: number;
    };
    scores?: {
      team1: {
        runs: number;
        wickets: number;
        overs: number;
      };
      team2: {
        runs: number;
        wickets: number;
        overs: number;
      };
    };
  };
}

export function MatchCard({ match }: MatchCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getStatusBadge = () => {
    switch (match.status) {
      case "live":
        return <Badge variant="live">LIVE</Badge>;
      case "completed":
        return <Badge variant="secondary">Completed</Badge>;
      default:
        return (
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span className="text-xs">
              {formatDistanceToNow(match.startTime, { addSuffix: true })}
            </span>
          </div>
        );
    }
  };

  const joinedPercentage =
    (match.contests.joinedTeams / match.contests.maxTeams) * 100;

  return (
    <Link href={`/matches/${match.id}`}>
      <Card
        className="group cursor-pointer"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <Badge variant="outline">T20</Badge>
          </div>
          <ChevronRight
            className={`h-5 w-5 transition-transform duration-200 ${
              isHovered ? "translate-x-1" : ""
            }`}
          />
        </CardHeader>

        <CardContent>
          <div className="flex items-center justify-between py-4">
            <div className="flex flex-1 flex-col items-center">
              <Image
                src={match.team1.logo}
                alt={match.team1.name}
                width={50}
                height={50}
                className="mb-2"
              />
              <span className="font-semibold">{match.team1.shortName}</span>
              {match.status !== "upcoming" && match.scores && (
                <span className="text-sm">
                  {match.scores.team1.runs}/{match.scores.team1.wickets}
                  <span className="text-xs text-muted-foreground">
                    ({match.scores.team1.overs})
                  </span>
                </span>
              )}
            </div>

            <div className="flex flex-col items-center px-4">
              <span className="text-sm font-medium text-muted-foreground">
                VS
              </span>
            </div>

            <div className="flex flex-1 flex-col items-center">
              <Image
                src={match.team2.logo}
                alt={match.team2.name}
                width={50}
                height={50}
                className="mb-2"
              />
              <span className="font-semibold">{match.team2.shortName}</span>
              {match.status !== "upcoming" && match.scores && (
                <span className="text-sm">
                  {match.scores.team2.runs}/{match.scores.team2.wickets}
                  <span className="text-xs text-muted-foreground">
                    ({match.scores.team2.overs})
                  </span>
                </span>
              )}
            </div>
          </div>
        </CardContent>

        <CardFooter className="border-t pt-4">
          <div className="grid w-full grid-cols-3 gap-4">
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-1 text-orange-500">
                <Trophy className="h-4 w-4" />
                <span className="font-semibold">
                  ₹{match.contests.prizePool.toLocaleString()}
                </span>
              </div>
              <span className="text-xs text-muted-foreground">Prize Pool</span>
            </div>

            <div className="flex flex-col items-center border-x px-2">
              <div className="flex items-center gap-1 text-green-500">
                <span className="font-semibold">
                  ₹{match.contests.entryFee}
                </span>
              </div>
              <span className="text-xs text-muted-foreground">Entry</span>
            </div>

            <div className="flex flex-col items-center">
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                <span className="font-semibold">
                  {match.contests.totalCount}
                </span>
              </div>
              <span className="text-xs text-muted-foreground">Contests</span>
            </div>
          </div>
        </CardFooter>

        {match.status === "upcoming" && (
          <div className="px-6 pb-4">
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
              <span>{match.contests.joinedTeams} teams</span>
              <span>{match.contests.maxTeams} spots</span>
            </div>
            <Progress value={joinedPercentage} className="h-1" />
          </div>
        )}
      </Card>
    </Link>
  );
}
