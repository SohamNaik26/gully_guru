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
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { IPL_PLAYERS, Player } from "@/lib/data/players";

export default function SquadPage() {
  const { activeGully, currentUser } = useAppStore();
  const [mySquad, setMySquad] = useState<Player[]>([]);

  useEffect(() => {
    // TODO: Fetch actual squad data from API
    // For now, using mock data
    if (activeGully) {
      const mockSquad = IPL_PLAYERS.slice(0, 11); // Just taking first 11 players as mock data
      setMySquad(mockSquad);
    }
  }, [activeGully]);

  if (!activeGully) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardContent className="py-6">
            <p className="text-center text-muted-foreground">
              Please select a gully first to view your squad.
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
          <h1 className="text-3xl font-bold tracking-tight">My Squad</h1>
          <p className="text-muted-foreground">
            Manage your team for {activeGully.name}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Squad Overview</CardTitle>
            <CardDescription>
              Your current team composition and statistics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mySquad.map((player) => (
                <div
                  key={player.id}
                  className="flex items-center justify-between border-b pb-4"
                >
                  <div>
                    <p className="font-medium">{player.name}</p>
                    <div className="flex gap-2 mt-1">
                      <Badge variant="outline">{player.team}</Badge>
                      <Badge>{player.role}</Badge>
                    </div>
                  </div>
                  <div className="text-sm text-right">
                    <p>Base Price: ₹{player.basePrice}</p>
                    {player.role === "Bowler" ? (
                      <p>Economy: {player.stats.economy}</p>
                    ) : (
                      <p>Avg: {player.stats.average}</p>
                    )}
                  </div>
                </div>
              ))}

              {mySquad.length === 0 && (
                <p className="text-center text-muted-foreground py-4">
                  You haven't selected any players yet.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
