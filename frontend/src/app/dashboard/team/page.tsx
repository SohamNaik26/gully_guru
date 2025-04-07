"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { IPL_PLAYERS, IPL_TEAMS, Player } from "@/lib/data/players";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function TeamPage() {
  const [selectedTeam, setSelectedTeam] = useState<string>("all");
  const [selectedPlayers, setSelectedPlayers] = useState<Player[]>([]);
  const { activeGully } = useAppStore();

  const handlePlayerSelect = (player: Player) => {
    if (
      selectedPlayers.length >= 11 &&
      !selectedPlayers.find((p) => p.id === player.id)
    ) {
      alert("You can't select more than 11 players!");
      return;
    }

    const isSelected = selectedPlayers.find((p) => p.id === player.id);
    if (isSelected) {
      setSelectedPlayers(selectedPlayers.filter((p) => p.id !== player.id));
    } else {
      // Check team composition rules
      const newTeam = [...selectedPlayers, player];
      const wicketKeepers = newTeam.filter(
        (p) => p.role === "Wicket-keeper"
      ).length;
      const batsmen = newTeam.filter((p) => p.role === "Batsman").length;
      const bowlers = newTeam.filter((p) => p.role === "Bowler").length;
      const allRounders = newTeam.filter(
        (p) => p.role === "All-rounder"
      ).length;

      if (wicketKeepers > 1) {
        alert("You can't select more than 1 wicket-keeper!");
        return;
      }
      if (batsmen > 5) {
        alert("You can't select more than 5 batsmen!");
        return;
      }
      if (bowlers > 5) {
        alert("You can't select more than 5 bowlers!");
        return;
      }
      if (allRounders > 3) {
        alert("You can't select more than 3 all-rounders!");
        return;
      }

      setSelectedPlayers(newTeam);
    }
  };

  const getTeamValue = () => {
    return selectedPlayers.reduce(
      (total, player) => total + player.basePrice,
      0
    );
  };

  const getTeamStats = () => {
    return {
      wicketKeepers: selectedPlayers.filter((p) => p.role === "Wicket-keeper")
        .length,
      batsmen: selectedPlayers.filter((p) => p.role === "Batsman").length,
      bowlers: selectedPlayers.filter((p) => p.role === "Bowler").length,
      allRounders: selectedPlayers.filter((p) => p.role === "All-rounder")
        .length,
    };
  };

  const teamStats = getTeamStats();

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team Management</h1>
          <p className="text-muted-foreground">
            Build and manage your fantasy cricket team
          </p>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Team Composition</CardTitle>
              <CardDescription>
                Select players for your team (Max 11 players)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="flex flex-col items-center justify-center border rounded-lg p-4">
                  <span className="text-3xl font-bold">
                    {teamStats.wicketKeepers}/1
                  </span>
                  <span className="text-sm text-muted-foreground">
                    Wicket-Keepers
                  </span>
                </div>
                <div className="flex flex-col items-center justify-center border rounded-lg p-4">
                  <span className="text-3xl font-bold">
                    {teamStats.batsmen}/5
                  </span>
                  <span className="text-sm text-muted-foreground">Batsmen</span>
                </div>
                <div className="flex flex-col items-center justify-center border rounded-lg p-4">
                  <span className="text-3xl font-bold">
                    {teamStats.bowlers}/5
                  </span>
                  <span className="text-sm text-muted-foreground">Bowlers</span>
                </div>
                <div className="flex flex-col items-center justify-center border rounded-lg p-4">
                  <span className="text-3xl font-bold">
                    {teamStats.allRounders}/3
                  </span>
                  <span className="text-sm text-muted-foreground">
                    All-Rounders
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Label>Filter by Team</Label>
                    <Select
                      value={selectedTeam}
                      onValueChange={setSelectedTeam}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a team" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Teams</SelectItem>
                        {Object.entries(IPL_TEAMS).map(([key, value]) => (
                          <SelectItem key={key} value={key}>
                            {value}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="text-right">
                    <Label>Team Value</Label>
                    <p className="text-2xl font-bold">₹{getTeamValue()}</p>
                  </div>
                </div>

                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Team</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Base Price</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {IPL_PLAYERS.filter(
                      (player) =>
                        selectedTeam === "all" || player.team === selectedTeam
                    ).map((player) => (
                      <TableRow key={player.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{player.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {player.nationality}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{player.team}</Badge>
                        </TableCell>
                        <TableCell>{player.role}</TableCell>
                        <TableCell>₹{player.basePrice}</TableCell>
                        <TableCell>
                          <Button
                            variant={
                              selectedPlayers.find((p) => p.id === player.id)
                                ? "destructive"
                                : "default"
                            }
                            onClick={() => handlePlayerSelect(player)}
                          >
                            {selectedPlayers.find((p) => p.id === player.id)
                              ? "Remove"
                              : "Add"}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          {selectedPlayers.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Selected Players</CardTitle>
                <CardDescription>
                  Your team composition ({selectedPlayers.length}/11 players)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Team</TableHead>
                      <TableHead>Stats</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedPlayers.map((player) => (
                      <TableRow key={player.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{player.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {player.nationality}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>{player.role}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{player.team}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {player.role === "Bowler" ? (
                              <>
                                <p>Wickets: {player.stats.wickets}</p>
                                <p>Economy: {player.stats.economy}</p>
                              </>
                            ) : (
                              <>
                                <p>Runs: {player.stats.runs}</p>
                                <p>Avg: {player.stats.average}</p>
                              </>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="destructive"
                            onClick={() => handlePlayerSelect(player)}
                          >
                            Remove
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
