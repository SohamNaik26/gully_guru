"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Clock, MapPin, ChevronRight } from "lucide-react";
import { toast } from "sonner";

interface Match {
  id: number;
  team1: string;
  team2: string;
  startTime: string;
  venue: string;
  status: "upcoming" | "live" | "completed";
  team1Score?: string;
  team2Score?: string;
  result?: string;
}

const MatchesPage = () => {
  const router = useRouter();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("upcoming");

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        setLoading(true);
        // In development, use mock data
        const mockMatches: Match[] = [
          {
            id: 1,
            team1: "Royal Challengers Bangalore",
            team2: "Chennai Super Kings",
            startTime: "2024-03-25T14:00:00Z",
            venue: "M. Chinnaswamy Stadium, Bangalore",
            status: "upcoming",
          },
          {
            id: 2,
            team1: "Mumbai Indians",
            team2: "Delhi Capitals",
            startTime: "2024-03-24T14:00:00Z",
            venue: "Wankhede Stadium, Mumbai",
            status: "live",
            team1Score: "186/4 (18.2)",
            team2Score: "165/6 (20.0)",
          },
          {
            id: 3,
            team1: "Kolkata Knight Riders",
            team2: "Rajasthan Royals",
            startTime: "2024-03-23T14:00:00Z",
            venue: "Eden Gardens, Kolkata",
            status: "completed",
            team1Score: "204/8 (20.0)",
            team2Score: "205/3 (19.1)",
            result: "Rajasthan Royals won by 7 wickets",
          },
        ];
        setMatches(mockMatches);
      } catch (error) {
        console.error("Error fetching matches:", error);
        toast.error("Failed to load matches");
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, []);

  const filteredMatches = matches.filter((match) => match.status === activeTab);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold">Matches</h1>
          <p className="text-sm text-muted-foreground">
            View all IPL 2024 matches and their details
          </p>
        </div>

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="upcoming" className="flex items-center gap-2">
              Upcoming
              <Badge variant="secondary" className="ml-2">
                {matches.filter((m) => m.status === "upcoming").length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="live" className="flex items-center gap-2">
              Live
              <Badge variant="destructive" className="ml-2">
                {matches.filter((m) => m.status === "live").length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="completed" className="flex items-center gap-2">
              Completed
              <Badge variant="secondary" className="ml-2">
                {matches.filter((m) => m.status === "completed").length}
              </Badge>
            </TabsTrigger>
          </TabsList>

          <div className="space-y-4">
            {filteredMatches.length === 0 ? (
              <Card className="p-6 text-center">
                <p className="text-muted-foreground">
                  No {activeTab} matches found
                </p>
              </Card>
            ) : (
              filteredMatches.map((match) => (
                <Card key={match.id} className="p-4">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground">
                            {new Date(match.startTime).toLocaleString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground">
                            {match.venue}
                          </span>
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
                        className="capitalize"
                      >
                        {match.status}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-2">
                        <div>
                          <p className="font-semibold">{match.team1}</p>
                          {match.team1Score && (
                            <p className="text-sm text-muted-foreground">
                              {match.team1Score}
                            </p>
                          )}
                        </div>
                        <div>
                          <p className="font-semibold">{match.team2}</p>
                          {match.team2Score && (
                            <p className="text-sm text-muted-foreground">
                              {match.team2Score}
                            </p>
                          )}
                        </div>
                        {match.result && (
                          <p className="text-sm text-primary">{match.result}</p>
                        )}
                      </div>
                      <Link href={`/matches/${match.id}`}>
                        <Button variant="outline" size="sm">
                          View Details
                          <ChevronRight className="h-4 w-4 ml-2" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </Tabs>
      </div>
    </div>
  );
};

export default MatchesPage;
