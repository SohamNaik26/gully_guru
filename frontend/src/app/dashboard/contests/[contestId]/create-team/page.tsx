"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { IPL_PLAYERS, IPL_TEAMS, TeamName, Player } from "@/lib/data/players";
import {
  AlertCircle,
  ArrowLeft,
  Trophy,
  Search,
  Filter,
  Info,
  Users,
  Plus,
  Trash2,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { Progress } from "@/components/ui/progress";

// Contest details
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
  rules: {
    maxPlayers: 11,
    maxPlayersPerTeam: 7,
    captainPoints: 2,
    viceCaptainPoints: 1.5,
    maxCredits: 100,
    minBatsmen: 3,
    maxBatsmen: 5,
    minBowlers: 3,
    maxBowlers: 5,
    minAllRounders: 1,
    maxAllRounders: 4,
    minWicketKeepers: 1,
    maxWicketKeepers: 2,
  },
};

// Mock credits for players (typically based on recent performance)
const getPlayerCredits = (player: Player): number => {
  // For this demo, we'll use a simplified calculation based on existing stats
  const basePrice = player.basePrice;
  if (basePrice > 10000000) return 10;
  if (basePrice > 5000000) return 9;
  if (basePrice > 1000000) return 8;
  if (basePrice > 500000) return 7;
  if (basePrice > 100000) return 6;
  if (basePrice > 10000) return 5;
  if (basePrice > 1000) return 4;
  if (basePrice > 100) return 3;
  return 2;
};

// Function to get the team/matchup specific players
const getMatchPlayers = (matchup: string): Player[] => {
  // Extract team abbreviations directly from the matchup
  // The format is expected to be like "MI vs CSK"
  const teamAbbreviations = matchup.split(" vs ");

  // Filter players based on these team abbreviations
  return IPL_PLAYERS.filter((player) =>
    teamAbbreviations.includes(player.team)
  );
};

// For team selection, we'll track roles and teams
type PlayerRole = "Batsman" | "Bowler" | "All-rounder" | "Wicket-keeper";

interface TeamCounts {
  batsmen: number;
  bowlers: number;
  allRounders: number;
  wicketKeepers: number;
  totalPlayers: number;
  totalCredits: number;
}

const initialTeamCounts: TeamCounts = {
  batsmen: 0,
  bowlers: 0,
  allRounders: 0,
  wicketKeepers: 0,
  totalPlayers: 0,
  totalCredits: 0,
};

interface SelectedPlayer extends Player {
  isCaptain: boolean;
  isViceCaptain: boolean;
  credits: number;
}

export default function CreateTeamPage() {
  const params = useParams();
  const router = useRouter();
  const contestId = params.contestId as string;

  const [activeTab, setActiveTab] = useState<string>("BAT");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [teamFilter, setTeamFilter] = useState<string>("all");
  const [showSelected, setShowSelected] = useState<boolean>(false);
  const [selectedPlayers, setSelectedPlayers] = useState<SelectedPlayer[]>([]);
  const [teamCounts, setTeamCounts] = useState<TeamCounts>(initialTeamCounts);
  const [teamName, setTeamName] = useState<string>("");

  // Get the players from both teams in the matchup
  const matchPlayers = getMatchPlayers(CONTEST.matchup);

  // Update team counts whenever selected players change
  useEffect(() => {
    const counts: TeamCounts = selectedPlayers.reduce(
      (acc, player) => {
        if (player.role === "Batsman") acc.batsmen += 1;
        else if (player.role === "Bowler") acc.bowlers += 1;
        else if (player.role === "All-rounder") acc.allRounders += 1;
        else if (player.role === "Wicket-keeper") acc.wicketKeepers += 1;

        acc.totalPlayers += 1;
        acc.totalCredits += player.credits;

        return acc;
      },
      { ...initialTeamCounts }
    );

    setTeamCounts(counts);
  }, [selectedPlayers]);

  // Filtered players based on active tab, search query, and team filter
  const filteredPlayers = matchPlayers.filter((player) => {
    const roleMatch =
      activeTab === "ALL" ||
      (activeTab === "BAT" && player.role === "Batsman") ||
      (activeTab === "BWL" && player.role === "Bowler") ||
      (activeTab === "AR" && player.role === "All-rounder") ||
      (activeTab === "WK" && player.role === "Wicket-keeper");

    const searchMatch =
      !searchQuery ||
      player.name.toLowerCase().includes(searchQuery.toLowerCase());

    const teamMatch = teamFilter === "all" || player.team === teamFilter;

    // If showing only selected players, filter accordingly
    const selectionMatch =
      !showSelected || selectedPlayers.some((sp) => sp.id === player.id);

    return (
      roleMatch &&
      searchMatch &&
      teamMatch &&
      (showSelected ? selectionMatch : true)
    );
  });

  // Check if a player can be selected
  const canSelectPlayer = (
    player: Player
  ): { canSelect: boolean; reason: string } => {
    // Check if already selected
    if (selectedPlayers.some((p) => p.id === player.id)) {
      return { canSelect: false, reason: "Already selected" };
    }

    // Check if team is full
    if (teamCounts.totalPlayers >= CONTEST.rules.maxPlayers) {
      return { canSelect: false, reason: "Team full (11/11)" };
    }

    // Check role limits
    if (
      player.role === "Batsman" &&
      teamCounts.batsmen >= CONTEST.rules.maxBatsmen
    ) {
      return {
        canSelect: false,
        reason: `Max ${CONTEST.rules.maxBatsmen} batsmen allowed`,
      };
    }
    if (
      player.role === "Bowler" &&
      teamCounts.bowlers >= CONTEST.rules.maxBowlers
    ) {
      return {
        canSelect: false,
        reason: `Max ${CONTEST.rules.maxBowlers} bowlers allowed`,
      };
    }
    if (
      player.role === "All-rounder" &&
      teamCounts.allRounders >= CONTEST.rules.maxAllRounders
    ) {
      return {
        canSelect: false,
        reason: `Max ${CONTEST.rules.maxAllRounders} all-rounders allowed`,
      };
    }
    if (
      player.role === "Wicket-keeper" &&
      teamCounts.wicketKeepers >= CONTEST.rules.maxWicketKeepers
    ) {
      return {
        canSelect: false,
        reason: `Max ${CONTEST.rules.maxWicketKeepers} wicket-keepers allowed`,
      };
    }

    // Check if adding this player would exceed credit limit
    const playerCredits = getPlayerCredits(player);
    if (teamCounts.totalCredits + playerCredits > CONTEST.rules.maxCredits) {
      return { canSelect: false, reason: "Not enough credits" };
    }

    // Check team limit (max 7 from one team)
    const playerTeam = player.team;
    const teamPlayerCount = selectedPlayers.filter(
      (p) => p.team === playerTeam
    ).length;
    if (teamPlayerCount >= CONTEST.rules.maxPlayersPerTeam) {
      return {
        canSelect: false,
        reason: `Max ${CONTEST.rules.maxPlayersPerTeam} players from ${IPL_TEAMS[playerTeam]}`,
      };
    }

    return { canSelect: true, reason: "" };
  };

  // Handle player selection/deselection
  const togglePlayerSelection = (player: Player) => {
    const isSelected = selectedPlayers.some((p) => p.id === player.id);

    if (isSelected) {
      // Remove player
      setSelectedPlayers(selectedPlayers.filter((p) => p.id !== player.id));
    } else {
      // Check if player can be added
      const { canSelect, reason } = canSelectPlayer(player);

      if (!canSelect) {
        alert(reason);
        return;
      }

      // Add player
      const credits = getPlayerCredits(player);
      setSelectedPlayers([
        ...selectedPlayers,
        { ...player, isCaptain: false, isViceCaptain: false, credits },
      ]);
    }
  };

  // Handle captain/vice-captain selection
  const setPlayerRole = (playerId: number, role: "captain" | "viceCaptain") => {
    setSelectedPlayers(
      selectedPlayers.map((player) => {
        // If setting captain, remove any existing captain
        if (role === "captain") {
          if (player.id === playerId) {
            return { ...player, isCaptain: true, isViceCaptain: false };
          }
          return { ...player, isCaptain: false };
        }

        // If setting vice-captain, remove any existing vice-captain
        if (role === "viceCaptain") {
          if (player.id === playerId) {
            return { ...player, isViceCaptain: true, isCaptain: false };
          }
          return { ...player, isViceCaptain: false };
        }

        return player;
      })
    );
  };

  // Check if team is valid and ready to submit
  const isTeamValid = () => {
    return (
      teamCounts.totalPlayers === CONTEST.rules.maxPlayers &&
      teamCounts.batsmen >= CONTEST.rules.minBatsmen &&
      teamCounts.bowlers >= CONTEST.rules.minBowlers &&
      teamCounts.allRounders >= CONTEST.rules.minAllRounders &&
      teamCounts.wicketKeepers >= CONTEST.rules.minWicketKeepers &&
      teamCounts.totalCredits <= CONTEST.rules.maxCredits &&
      selectedPlayers.some((p) => p.isCaptain) &&
      selectedPlayers.some((p) => p.isViceCaptain) &&
      teamName.trim().length > 0
    );
  };

  // Submit team
  const handleSubmitTeam = () => {
    if (!isTeamValid()) {
      alert("Please complete your team selection");
      return;
    }

    // In a real app, you would send this to your backend
    console.log("Submitting team:", {
      contestId,
      teamName,
      players: selectedPlayers,
      captain: selectedPlayers.find((p) => p.isCaptain)?.id,
      viceCaptain: selectedPlayers.find((p) => p.isViceCaptain)?.id,
    });

    // Navigate to a confirmation page
    router.push(`/dashboard/contests/${contestId}/team-created`);
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        {/* Header with back button */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" asChild>
              <Link href="/dashboard/contests">
                <ArrowLeft className="h-5 w-5" />
              </Link>
            </Button>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Create Team</h1>
              <p className="text-muted-foreground">
                {CONTEST.title} - {CONTEST.matchup}
              </p>
            </div>
          </div>
          <Badge variant="outline" className="bg-blue-50 text-blue-700">
            Credits Left: {CONTEST.rules.maxCredits - teamCounts.totalCredits}
          </Badge>
        </div>

        {/* Team Progress */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row md:justify-between gap-6">
              <div className="space-y-4 flex-1">
                <div>
                  <Label htmlFor="team-name">Team Name</Label>
                  <Input
                    id="team-name"
                    placeholder="Enter your team name"
                    value={teamName}
                    onChange={(e) => setTeamName(e.target.value)}
                    className="max-w-xs"
                  />
                </div>

                <h3 className="font-semibold flex items-center">
                  <Users className="mr-2 h-5 w-5" />
                  Players Selection ({teamCounts.totalPlayers}/
                  {CONTEST.rules.maxPlayers})
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex flex-col bg-card border rounded-lg p-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">BAT</span>
                      <span
                        className={`text-sm font-medium ${
                          teamCounts.batsmen < CONTEST.rules.minBatsmen
                            ? "text-red-500"
                            : ""
                        }`}
                      >
                        {teamCounts.batsmen}/{CONTEST.rules.maxBatsmen}
                      </span>
                    </div>
                    <Progress
                      value={
                        (teamCounts.batsmen / CONTEST.rules.maxBatsmen) * 100
                      }
                      className="h-1.5 mt-2"
                    />
                  </div>

                  <div className="flex flex-col bg-card border rounded-lg p-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">BWL</span>
                      <span
                        className={`text-sm font-medium ${
                          teamCounts.bowlers < CONTEST.rules.minBowlers
                            ? "text-red-500"
                            : ""
                        }`}
                      >
                        {teamCounts.bowlers}/{CONTEST.rules.maxBowlers}
                      </span>
                    </div>
                    <Progress
                      value={
                        (teamCounts.bowlers / CONTEST.rules.maxBowlers) * 100
                      }
                      className="h-1.5 mt-2"
                    />
                  </div>

                  <div className="flex flex-col bg-card border rounded-lg p-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">AR</span>
                      <span
                        className={`text-sm font-medium ${
                          teamCounts.allRounders < CONTEST.rules.minAllRounders
                            ? "text-red-500"
                            : ""
                        }`}
                      >
                        {teamCounts.allRounders}/{CONTEST.rules.maxAllRounders}
                      </span>
                    </div>
                    <Progress
                      value={
                        (teamCounts.allRounders /
                          CONTEST.rules.maxAllRounders) *
                        100
                      }
                      className="h-1.5 mt-2"
                    />
                  </div>

                  <div className="flex flex-col bg-card border rounded-lg p-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">WK</span>
                      <span
                        className={`text-sm font-medium ${
                          teamCounts.wicketKeepers <
                          CONTEST.rules.minWicketKeepers
                            ? "text-red-500"
                            : ""
                        }`}
                      >
                        {teamCounts.wicketKeepers}/
                        {CONTEST.rules.maxWicketKeepers}
                      </span>
                    </div>
                    <Progress
                      value={
                        (teamCounts.wicketKeepers /
                          CONTEST.rules.maxWicketKeepers) *
                        100
                      }
                      className="h-1.5 mt-2"
                    />
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-3 md:items-end">
                <p className="text-sm text-muted-foreground flex items-center">
                  <Info className="mr-1 h-4 w-4" />
                  Choose C and VC to earn extra points
                </p>
                <div className="flex gap-2">
                  <Badge className="bg-green-100 text-green-800 border-0">
                    C: 2x Points
                  </Badge>
                  <Badge className="bg-blue-100 text-blue-800 border-0">
                    VC: 1.5x Points
                  </Badge>
                </div>
                <Button
                  className="mt-auto"
                  disabled={!isTeamValid()}
                  onClick={handleSubmitTeam}
                >
                  Submit Team
                </Button>
                <Button
                  className="mt-2"
                  variant="outline"
                  onClick={() => {
                    const hasCaptain = selectedPlayers.some((p) => p.isCaptain);
                    const hasViceCaptain = selectedPlayers.some(
                      (p) => p.isViceCaptain
                    );

                    // Display detailed validation status
                    alert(
                      `Team Validation Status:
                      Players: ${teamCounts.totalPlayers}/${
                        CONTEST.rules.maxPlayers
                      }
                      Batsmen: ${teamCounts.batsmen}/${
                        CONTEST.rules.minBatsmen
                      }-${CONTEST.rules.maxBatsmen}
                      Bowlers: ${teamCounts.bowlers}/${
                        CONTEST.rules.minBowlers
                      }-${CONTEST.rules.maxBowlers}
                      All-Rounders: ${teamCounts.allRounders}/${
                        CONTEST.rules.minAllRounders
                      }-${CONTEST.rules.maxAllRounders}
                      Wicket-Keepers: ${teamCounts.wicketKeepers}/${
                        CONTEST.rules.minWicketKeepers
                      }-${CONTEST.rules.maxWicketKeepers}
                      Credits: ${teamCounts.totalCredits}/${
                        CONTEST.rules.maxCredits
                      }
                      Captain Selected: ${hasCaptain ? "Yes" : "No"}
                      Vice-Captain Selected: ${hasViceCaptain ? "Yes" : "No"}
                      Team Name: ${
                        teamName.trim().length > 0 ? "Valid" : "Missing"
                      }`
                    );

                    // Force submit regardless of validation
                    if (!hasCaptain || !hasViceCaptain) {
                      alert(
                        "IMPORTANT: You must select a Captain (C) and Vice-Captain (VC) by clicking the C and VC buttons under any two players in your selected team."
                      );
                    }
                  }}
                >
                  Check Team Status
                </Button>
                <Button
                  className="mt-2"
                  variant="destructive"
                  onClick={() => {
                    if (teamCounts.totalPlayers !== CONTEST.rules.maxPlayers) {
                      alert(
                        `You need exactly ${CONTEST.rules.maxPlayers} players in your team.`
                      );
                      return;
                    }

                    // Check for unfilled captain/vice-captain
                    const hasCaptain = selectedPlayers.some((p) => p.isCaptain);
                    const hasViceCaptain = selectedPlayers.some(
                      (p) => p.isViceCaptain
                    );

                    if (!hasCaptain && !hasViceCaptain) {
                      // Auto-select first two players as C and VC if none selected
                      const updatedPlayers = [...selectedPlayers];
                      if (updatedPlayers.length >= 2) {
                        updatedPlayers[0].isCaptain = true;
                        updatedPlayers[1].isViceCaptain = true;
                        setSelectedPlayers(updatedPlayers);
                        alert(
                          "Auto-selected first player as Captain and second player as Vice-Captain"
                        );
                      }
                    } else if (!hasCaptain) {
                      // Find first non-VC player and make captain
                      const updatedPlayers = selectedPlayers.map(
                        (player, index) => {
                          if (index === 0 && !player.isViceCaptain) {
                            return { ...player, isCaptain: true };
                          }
                          return player;
                        }
                      );
                      setSelectedPlayers(updatedPlayers);
                      alert("Auto-selected first player as Captain");
                    } else if (!hasViceCaptain) {
                      // Find first non-Captain player and make VC
                      const updatedPlayers = selectedPlayers.map(
                        (player, index) => {
                          if (index === 1 && !player.isCaptain) {
                            return { ...player, isViceCaptain: true };
                          }
                          return player;
                        }
                      );
                      setSelectedPlayers(updatedPlayers);
                      alert("Auto-selected second player as Vice-Captain");
                    }

                    // Force navigation to the confirmation page
                    router.push(
                      `/dashboard/contests/${contestId}/team-created`
                    );
                  }}
                >
                  Force Submit Team
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Selected Players Preview */}
        {selectedPlayers.length > 0 && (
          <div className="grid grid-cols-5 md:grid-cols-11 gap-2">
            {selectedPlayers.map((player) => (
              <div
                key={player.id}
                className="relative flex flex-col items-center p-2 border rounded-lg bg-card"
              >
                <button
                  onClick={() => togglePlayerSelection(player)}
                  className="absolute top-1 right-1 text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>

                {/* Display player image - in a real app, use actual player images */}
                <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-1">
                  {player.name.charAt(0)}
                </div>

                <p className="text-xs font-medium truncate w-full text-center">
                  {player.name.split(" ").pop()}
                </p>
                <p className="text-xs text-muted-foreground">
                  {player.credits} Cr
                </p>

                {/* Captain/VC selection */}
                <div className="flex gap-1 mt-1">
                  <button
                    className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold ${
                      player.isCaptain
                        ? "bg-green-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                    onClick={() => setPlayerRole(player.id, "captain")}
                  >
                    C
                  </button>
                  <button
                    className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold ${
                      player.isViceCaptain
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                    onClick={() => setPlayerRole(player.id, "viceCaptain")}
                  >
                    VC
                  </button>
                </div>
              </div>
            ))}

            {/* Placeholders for remaining slots */}
            {Array.from({
              length: CONTEST.rules.maxPlayers - selectedPlayers.length,
            }).map((_, idx) => (
              <div
                key={`placeholder-${idx}`}
                className="flex flex-col items-center p-2 border rounded-lg bg-muted/30 border-dashed"
              >
                <div className="w-12 h-12 rounded-full bg-muted/50 flex items-center justify-center mb-1">
                  <Plus className="h-6 w-6 text-muted-foreground/50" />
                </div>
                <p className="text-xs text-muted-foreground">Add Player</p>
              </div>
            ))}
          </div>
        )}

        {/* Player Selection Interface */}
        <Card>
          <CardHeader className="pb-0">
            <div className="flex flex-col md:flex-row md:justify-between gap-4">
              <div className="relative w-full md:w-64">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search players..."
                  className="pl-8"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="show-selected"
                    checked={showSelected}
                    onCheckedChange={setShowSelected}
                  />
                  <Label htmlFor="show-selected">Show selected only</Label>
                </div>

                <select
                  className="h-10 w-full md:w-auto rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={teamFilter}
                  onChange={(e) => setTeamFilter(e.target.value)}
                >
                  <option value="all">All Teams</option>
                  {CONTEST.matchup.split(" vs ").map((team, idx) => {
                    const teamKey = Object.keys(IPL_TEAMS).find((key) =>
                      IPL_TEAMS[key as TeamName].includes(team)
                    );
                    if (teamKey) {
                      return (
                        <option key={idx} value={teamKey}>
                          {team}
                        </option>
                      );
                    }
                    return null;
                  })}
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0 pt-4">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="w-full justify-start px-6">
                <TabsTrigger value="BAT">Batsmen</TabsTrigger>
                <TabsTrigger value="BWL">Bowlers</TabsTrigger>
                <TabsTrigger value="AR">All-Rounders</TabsTrigger>
                <TabsTrigger value="WK">Wicket-Keepers</TabsTrigger>
                <TabsTrigger value="ALL">All</TabsTrigger>
              </TabsList>

              <div className="pt-2 divide-y">
                {filteredPlayers.map((player) => {
                  const isSelected = selectedPlayers.some(
                    (p) => p.id === player.id
                  );
                  const { canSelect, reason } = canSelectPlayer(player);
                  const playerCredits = getPlayerCredits(player);

                  return (
                    <div
                      key={player.id}
                      className="flex items-center justify-between px-6 py-3 hover:bg-muted/30"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                          {player.name.charAt(0)}
                        </div>

                        <div>
                          <p className="font-medium">{player.name}</p>
                          <div className="flex items-center text-xs text-muted-foreground gap-2">
                            <span>{IPL_TEAMS[player.team]}</span>
                            <span>•</span>
                            <span>{player.role}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="flex items-center px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
                          <Trophy className="h-3 w-3 mr-1" />
                          {playerCredits} Cr
                        </div>

                        <Button
                          size="sm"
                          variant={isSelected ? "destructive" : "default"}
                          onClick={() => togglePlayerSelection(player)}
                          disabled={!isSelected && !canSelect}
                          title={!isSelected && !canSelect ? reason : ""}
                        >
                          {isSelected ? "Remove" : "Add"}
                        </Button>
                      </div>
                    </div>
                  );
                })}

                {filteredPlayers.length === 0 && (
                  <div className="py-10 text-center text-muted-foreground">
                    No players found matching your filters.
                  </div>
                )}
              </div>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
