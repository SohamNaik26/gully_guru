"use client";

import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  ChevronRight,
  Share2,
  Trophy,
  Users,
  Check,
} from "lucide-react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useState, useEffect } from "react";

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
  firstPrize: 25000,
  status: "open",
};

export default function TeamCreatedPage() {
  const params = useParams();
  const router = useRouter();
  const contestId = params.contestId as string;
  const [countdown, setCountdown] = useState<number>(3);

  // For demo purposes: show a mock team
  const mockTeam = {
    name: "Cricket Champions",
    captain: "Virat Kohli",
    viceCaptain: "MS Dhoni",
    totalCredits: 97.5,
    players: [
      "Virat Kohli (C)",
      "MS Dhoni (VC)",
      "Rohit Sharma",
      "Jasprit Bumrah",
      "Hardik Pandya",
      "Ravindra Jadeja",
      "KL Rahul",
      "Rishabh Pant",
      "Mohammed Shami",
      "Yuzvendra Chahal",
      "Shikhar Dhawan",
    ],
  };

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

  // Automatically redirect to view all teams after countdown
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);

      return () => clearTimeout(timer);
    } else {
      router.push(`/dashboard/contests/${contestId}`);
    }
  }, [countdown, contestId, router]);

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6 max-w-3xl mx-auto">
        {/* Success message */}
        <div className="bg-green-50 rounded-lg p-6 border border-green-200 text-center">
          <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
            <Check className="h-8 w-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-green-800 mb-2">
            Team Created Successfully!
          </h1>
          <p className="text-green-700">
            Your team has been entered into the contest. Good luck!
          </p>
          <p className="text-sm text-muted-foreground mt-4">
            Redirecting to contest page in {countdown} seconds...
          </p>
        </div>

        {/* Contest Card */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex justify-between items-center">
              <span>{CONTEST.title}</span>
              <Badge>{CONTEST.matchup}</Badge>
            </CardTitle>
            <div className="mt-1">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Entry: ₹{CONTEST.entryFee}</span>
                <span>Prize Pool: ₹{CONTEST.totalPrize.toLocaleString()}</span>
                <span>Starts: {formatDate(CONTEST.startDate)}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pb-2">
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2 flex items-center">
                  <Users className="h-4 w-4 mr-2" />
                  Your Team: {mockTeam.name}
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-2 gap-x-4">
                  {mockTeam.players.map((player, index) => (
                    <div key={index} className="text-sm flex items-center">
                      <span
                        className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold mr-2 ${
                          player.includes("(C)")
                            ? "bg-green-600 text-white"
                            : player.includes("(VC)")
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {player.includes("(C)")
                          ? "C"
                          : player.includes("(VC)")
                          ? "VC"
                          : index + 1}
                      </span>
                      {player.replace(" (C)", "").replace(" (VC)", "")}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">
                  Total Credits Used:
                </span>
                <span className="font-medium">
                  {mockTeam.totalCredits} / 100
                </span>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                // In a real app, implement sharing functionality
                navigator.clipboard.writeText(
                  `Check out my team ${mockTeam.name} for ${CONTEST.title}!`
                );
                alert("Team details copied to clipboard");
              }}
            >
              <Share2 className="h-4 w-4 mr-1.5" />
              Share Team
            </Button>

            <Button size="sm" asChild>
              <Link href={`/dashboard/contests/${contestId}`}>
                View Contest
                <ChevronRight className="h-4 w-4 ml-1.5" />
              </Link>
            </Button>
          </CardFooter>
        </Card>

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Button variant="outline" className="flex-1" asChild>
            <Link href={`/dashboard/contests/${contestId}/create-team`}>
              <ArrowLeft className="h-4 w-4 mr-1.5" />
              Edit Team
            </Link>
          </Button>

          <Button variant="default" className="flex-1" asChild>
            <Link href="/dashboard/contests">
              <Trophy className="h-4 w-4 mr-1.5" />
              Browse More Contests
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
