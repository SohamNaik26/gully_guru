"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { IPL_PLAYERS, IPL_TEAMS, TeamName } from "@/lib/data/players";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const COLORS = [
  "#3b82f6", // blue-500
  "#ef4444", // red-500
  "#10b981", // emerald-500
  "#f59e0b", // amber-500
  "#8b5cf6", // violet-500
  "#ec4899", // pink-500
  "#06b6d4", // cyan-500
  "#f97316", // orange-500
  "#6366f1", // indigo-500
  "#84cc16", // lime-500
];

export default function StatsPage() {
  const [activeTab, setActiveTab] = useState("players");

  // Top Run Scorers
  const topRunScorers = [...IPL_PLAYERS]
    .filter((player) => player.stats.runs)
    .sort((a, b) => (b.stats.runs || 0) - (a.stats.runs || 0))
    .slice(0, 10);

  // Top Wicket Takers
  const topWicketTakers = [...IPL_PLAYERS]
    .filter((player) => player.stats.wickets)
    .sort((a, b) => (b.stats.wickets || 0) - (a.stats.wickets || 0))
    .slice(0, 10);

  // Best Strike Rates (minimum 200 runs)
  const bestStrikeRates = [...IPL_PLAYERS]
    .filter(
      (player) => (player.stats.runs || 0) >= 200 && player.stats.strikeRate
    )
    .sort((a, b) => (b.stats.strikeRate || 0) - (a.stats.strikeRate || 0))
    .slice(0, 10);

  // Best Economy Rates (minimum 10 wickets)
  const bestEconomyRates = [...IPL_PLAYERS]
    .filter(
      (player) => (player.stats.wickets || 0) >= 10 && player.stats.economy
    )
    .sort((a, b) => (a.stats.economy || 10) - (b.stats.economy || 10))
    .slice(0, 10);

  // Team data
  const roleDistribution = [
    {
      name: "Batsmen",
      value: IPL_PLAYERS.filter((p) => p.role === "Batsman").length,
    },
    {
      name: "Bowlers",
      value: IPL_PLAYERS.filter((p) => p.role === "Bowler").length,
    },
    {
      name: "All-rounders",
      value: IPL_PLAYERS.filter((p) => p.role === "All-rounder").length,
    },
    {
      name: "Wicket-keepers",
      value: IPL_PLAYERS.filter((p) => p.role === "Wicket-keeper").length,
    },
  ];

  // Team wise player distribution
  const teamDistribution = Object.entries(IPL_TEAMS).map(([key, name]) => ({
    name: key,
    fullName: name,
    value: IPL_PLAYERS.filter((p) => p.team === (key as TeamName)).length,
  }));

  const batPerformance = Object.entries(IPL_TEAMS)
    .map(([key, name]) => {
      const teamPlayers = IPL_PLAYERS.filter(
        (p) => p.team === (key as TeamName)
      );
      const totalRuns = teamPlayers.reduce(
        (sum, player) => sum + (player.stats.runs || 0),
        0
      );
      return {
        name: key,
        fullName: name,
        runs: totalRuns,
      };
    })
    .sort((a, b) => b.runs - a.runs);

  const bowlPerformance = Object.entries(IPL_TEAMS)
    .map(([key, name]) => {
      const teamPlayers = IPL_PLAYERS.filter(
        (p) => p.team === (key as TeamName)
      );
      const totalWickets = teamPlayers.reduce(
        (sum, player) => sum + (player.stats.wickets || 0),
        0
      );
      return {
        name: key,
        fullName: name,
        wickets: totalWickets,
      };
    })
    .sort((a, b) => b.wickets - a.wickets);

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Statistics</h1>
          <p className="text-muted-foreground">
            Comprehensive statistics of players and teams
          </p>
        </div>

        <Tabs
          defaultValue="players"
          onValueChange={setActiveTab}
          value={activeTab}
        >
          <TabsList className="mb-6">
            <TabsTrigger value="players">Player Stats</TabsTrigger>
            <TabsTrigger value="teams">Team Stats</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
          </TabsList>

          <TabsContent value="players">
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Top Run Scorers</CardTitle>
                  <CardDescription>
                    Players with the most runs in IPL
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Rank</TableHead>
                        <TableHead>Player</TableHead>
                        <TableHead>Team</TableHead>
                        <TableHead className="text-right">Runs</TableHead>
                        <TableHead className="text-right">Average</TableHead>
                        <TableHead className="text-right">
                          Strike Rate
                        </TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {topRunScorers.map((player, index) => (
                        <TableRow key={player.id}>
                          <TableCell className="font-medium">
                            {index + 1}
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-semibold">{player.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {player.nationality}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{player.team}</Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            {player.stats.runs}
                          </TableCell>
                          <TableCell className="text-right">
                            {player.stats.average?.toFixed(2)}
                          </TableCell>
                          <TableCell className="text-right">
                            {player.stats.strikeRate?.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Top Wicket Takers</CardTitle>
                  <CardDescription>
                    Players with the most wickets in IPL
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Rank</TableHead>
                        <TableHead>Player</TableHead>
                        <TableHead>Team</TableHead>
                        <TableHead className="text-right">Wickets</TableHead>
                        <TableHead className="text-right">Economy</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {topWicketTakers.map((player, index) => (
                        <TableRow key={player.id}>
                          <TableCell className="font-medium">
                            {index + 1}
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-semibold">{player.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {player.nationality}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{player.team}</Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            {player.stats.wickets}
                          </TableCell>
                          <TableCell className="text-right">
                            {player.stats.economy?.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="teams">
            <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Batting Performance by Team</CardTitle>
                  <CardDescription>
                    Total runs scored by each team
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Rank</TableHead>
                        <TableHead>Team</TableHead>
                        <TableHead className="text-right">Total Runs</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {batPerformance.map((team, index) => (
                        <TableRow key={team.name}>
                          <TableCell className="font-medium">
                            {index + 1}
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-semibold">{team.fullName}</p>
                              <p className="text-xs text-muted-foreground">
                                {team.name}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            {team.runs}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Bowling Performance by Team</CardTitle>
                  <CardDescription>
                    Total wickets taken by each team
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Rank</TableHead>
                        <TableHead>Team</TableHead>
                        <TableHead className="text-right">
                          Total Wickets
                        </TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {bowlPerformance.map((team, index) => (
                        <TableRow key={team.name}>
                          <TableCell className="font-medium">
                            {index + 1}
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-semibold">{team.fullName}</p>
                              <p className="text-xs text-muted-foreground">
                                {team.name}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            {team.wickets}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="charts">
            <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Player Role Distribution</CardTitle>
                  <CardDescription>
                    Breakdown of player roles in IPL
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={roleDistribution}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) =>
                            `${name} ${(percent * 100).toFixed(0)}%`
                          }
                        >
                          {roleDistribution.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={COLORS[index % COLORS.length]}
                            />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Team Performance Comparison</CardTitle>
                  <CardDescription>Runs scored by each team</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={batPerformance}
                        margin={{
                          top: 5,
                          right: 30,
                          left: 20,
                          bottom: 5,
                        }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="runs" fill="#3b82f6" name="Runs" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Team Distribution</CardTitle>
                  <CardDescription>
                    Number of players in each team
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={teamDistribution}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) =>
                            `${name} ${(percent * 100).toFixed(0)}%`
                          }
                        >
                          {teamDistribution.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={COLORS[index % COLORS.length]}
                            />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Wickets by Team</CardTitle>
                  <CardDescription>Wickets taken by each team</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={bowlPerformance}
                        margin={{
                          top: 5,
                          right: 30,
                          left: 20,
                          bottom: 5,
                        }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="wickets" fill="#ef4444" name="Wickets" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
