import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Filter, Users } from "lucide-react";
import { Player } from "@/lib/data/players";

interface TeamEditorProps {
  players: Player[];
  selectedPlayers: Player[];
  onSave: (players: Player[]) => void;
  onCancel: () => void;
}

export function TeamEditor({
  players,
  selectedPlayers,
  onSave,
  onCancel,
}: TeamEditorProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("all");

  // Get unique teams and roles for organization
  const teams = Array.from(new Set(players.map((p) => p.team))).sort();
  const roles = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"];

  // Filter players based on search and active tab
  const filteredPlayers = players.filter((player) => {
    const matchesSearch = player.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === "all" || player.role === activeTab;
    return matchesSearch && matchesTab;
  });

  // Group players by team for better organization
  const groupedPlayers = filteredPlayers.reduce((acc, player) => {
    const team = player.team;
    if (!acc[team]) {
      acc[team] = [];
    }
    acc[team].push(player);
    return acc;
  }, {} as Record<string, Player[]>);

  const isPlayerSelected = (playerId: number) =>
    selectedPlayers.some((p) => p.id === playerId);

  const togglePlayer = (player: Player) => {
    if (isPlayerSelected(player.id)) {
      onSave(selectedPlayers.filter((p) => p.id !== player.id));
    } else {
      onSave([...selectedPlayers, player]);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4">
        <div className="flex-1 space-y-2">
          <Label>Search Players</Label>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by player name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>
        </div>
      </div>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-4"
      >
        <TabsList className="grid grid-cols-5 gap-2">
          <TabsTrigger value="all" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            All
          </TabsTrigger>
          {roles.map((role) => (
            <TabsTrigger key={role} value={role}>
              {role}
            </TabsTrigger>
          ))}
        </TabsList>

        <div className="space-y-6">
          {teams.map((team) => {
            const teamPlayers = groupedPlayers[team];
            if (!teamPlayers?.length) return null;

            return (
              <div key={team} className="space-y-2">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <Badge variant="outline">{team}</Badge>
                  <span className="text-sm text-muted-foreground">
                    ({teamPlayers.length} players)
                  </span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {teamPlayers.map((player) => (
                    <Card
                      key={player.id}
                      className={`p-4 cursor-pointer transition-colors hover:bg-muted/50 ${
                        isPlayerSelected(player.id)
                          ? "bg-primary/10 border-primary"
                          : ""
                      }`}
                      onClick={() => togglePlayer(player)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="space-y-1.5">
                          <p className="font-medium text-base">{player.name}</p>
                          <div className="flex items-center gap-2">
                            <Badge>{player.role}</Badge>
                            {player.stats.average && (
                              <span className="text-sm text-muted-foreground">
                                Avg: {player.stats.average}
                              </span>
                            )}
                            {player.stats.economy && (
                              <span className="text-sm text-muted-foreground">
                                Eco: {player.stats.economy}
                              </span>
                            )}
                          </div>
                        </div>
                        <Button
                          variant={
                            isPlayerSelected(player.id) ? "default" : "outline"
                          }
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            togglePlayer(player);
                          }}
                        >
                          {isPlayerSelected(player.id) ? "Remove" : "Add"}
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </Tabs>

      <div className="flex items-center justify-between border-t pt-4">
        <div className="space-y-1">
          <p className="font-medium">
            Selected Players: {selectedPlayers.length}
          </p>
          <p className="text-sm text-muted-foreground">
            {roles.map((role) => {
              const count = selectedPlayers.filter(
                (p) => p.role === role
              ).length;
              return count > 0 ? `${role}s: ${count}, ` : "";
            })}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={() => onSave(selectedPlayers)}>Save Team</Button>
        </div>
      </div>
    </div>
  );
}
