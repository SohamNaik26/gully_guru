"use client";

import { TeamCode, teamLogos, teamNames } from "@/lib/data/teamLogos";
import { IPL_TEAMS } from "@/lib/data/players";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Image from "next/image";

export interface MatchDetailsDialogProps {
  isOpen: boolean;
  onClose: () => void;
  match: any;
}

export function MatchDetailsDialog({
  isOpen,
  onClose,
  match,
}: MatchDetailsDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Match Details</DialogTitle>
          <DialogDescription>
            {match.date} - {match.time} | {match.venue}
          </DialogDescription>
        </DialogHeader>

        <div className="flex justify-between items-center my-4">
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-white rounded-full p-1">
              <Image
                src={teamLogos[match.team1 as TeamCode]}
                alt={teamNames[match.team1 as TeamCode]}
                width={64}
                height={64}
              />
            </div>
            <h3 className="mt-2 font-medium">{IPL_TEAMS[match.team1]}</h3>
          </div>

          <div className="text-center">
            <div className="text-xl font-bold">VS</div>
            {match.liveScore && (
              <div className="mt-2">
                <Badge variant="outline" className="text-xs animate-pulse">
                  LIVE
                </Badge>
              </div>
            )}
          </div>

          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-white rounded-full p-1">
              <Image
                src={teamLogos[match.team2 as TeamCode]}
                alt={teamNames[match.team2 as TeamCode]}
                width={64}
                height={64}
              />
            </div>
            <h3 className="mt-2 font-medium">{IPL_TEAMS[match.team2]}</h3>
          </div>
        </div>

        {match.liveScore && (
          <div className="border rounded-lg p-4 mb-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="font-medium">{IPL_TEAMS[match.team1]}</div>
                <div className="text-xl font-bold">
                  {match.liveScore.team1.runs}/{match.liveScore.team1.wickets}
                  <span className="text-sm font-normal">
                    ({match.liveScore.team1.overs} ov)
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  CRR: {match.liveScore.team1.runRate}
                </div>
              </div>
              <div>
                <div className="font-medium">{IPL_TEAMS[match.team2]}</div>
                <div className="text-xl font-bold">
                  {match.liveScore.team2.runs}/{match.liveScore.team2.wickets}
                  <span className="text-sm font-normal">
                    ({match.liveScore.team2.overs} ov)
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  CRR: {match.liveScore.team2.runRate}
                </div>
              </div>
            </div>
            <div className="mt-2 text-sm">
              <Badge variant="outline">{match.liveScore.matchStatus}</Badge>
            </div>
          </div>
        )}

        <Tabs defaultValue="lineup">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="lineup">Teams</TabsTrigger>
            <TabsTrigger value="stats">Stats</TabsTrigger>
            <TabsTrigger value="h2h">Head to Head</TabsTrigger>
          </TabsList>

          <TabsContent value="lineup" className="space-y-4">
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <h3 className="font-medium mb-2">{IPL_TEAMS[match.team1]}</h3>
                <ul className="space-y-1">
                  {match.probablePlayers?.team1.map(
                    (player: string, index: number) => (
                      <li key={index} className="text-sm">
                        {player}
                      </li>
                    )
                  )}
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2">{IPL_TEAMS[match.team2]}</h3>
                <ul className="space-y-1">
                  {match.probablePlayers?.team2.map(
                    (player: string, index: number) => (
                      <li key={index} className="text-sm">
                        {player}
                      </li>
                    )
                  )}
                </ul>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="stats">
            {match.liveScore ? (
              <div className="grid grid-cols-2 gap-6 mt-4">
                <div>
                  <h3 className="font-medium mb-2">Batting</h3>
                  <div className="space-y-2">
                    {match.liveScore.team1.battingStats.map(
                      (batsman: any, index: number) => (
                        <div
                          key={index}
                          className="text-sm flex justify-between border-b pb-1"
                        >
                          <div>{batsman.player}</div>
                          <div>
                            {batsman.runs} ({batsman.balls})
                            <span className="text-xs ml-1">
                              SR: {batsman.strikeRate}
                            </span>
                          </div>
                        </div>
                      )
                    )}
                    {match.liveScore.team2.battingStats.map(
                      (batsman: any, index: number) => (
                        <div
                          key={index}
                          className="text-sm flex justify-between border-b pb-1"
                        >
                          <div>{batsman.player}</div>
                          <div>
                            {batsman.runs} ({batsman.balls})
                            <span className="text-xs ml-1">
                              SR: {batsman.strikeRate}
                            </span>
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>
                <div>
                  <h3 className="font-medium mb-2">Bowling</h3>
                  <div className="space-y-2">
                    {match.liveScore.team1.bowlingStats.map(
                      (bowler: any, index: number) => (
                        <div
                          key={index}
                          className="text-sm flex justify-between border-b pb-1"
                        >
                          <div>{bowler.player}</div>
                          <div>
                            {bowler.wickets}/{bowler.runs} ({bowler.overs})
                            <span className="text-xs ml-1">
                              Econ: {bowler.economy}
                            </span>
                          </div>
                        </div>
                      )
                    )}
                    {match.liveScore.team2.bowlingStats.map(
                      (bowler: any, index: number) => (
                        <div
                          key={index}
                          className="text-sm flex justify-between border-b pb-1"
                        >
                          <div>{bowler.player}</div>
                          <div>
                            {bowler.wickets}/{bowler.runs} ({bowler.overs})
                            <span className="text-xs ml-1">
                              Econ: {bowler.economy}
                            </span>
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center">
                <p className="text-muted-foreground">
                  Match has not started yet
                </p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="h2h">
            {match.headToHead ? (
              <div className="mt-4 space-y-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-3xl font-bold">
                      {match.headToHead.team1Wins}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {IPL_TEAMS[match.team1]} Wins
                    </div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {match.headToHead.draws}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Draws/NR
                    </div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {match.headToHead.team2Wins}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {IPL_TEAMS[match.team2]} Wins
                    </div>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-muted-foreground">
                    Total Matches: {match.headToHead.total}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center">
                <p className="text-muted-foreground">
                  No head to head data available
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
