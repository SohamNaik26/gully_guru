import { Trophy, Users, TrendingUp, Crown } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";

interface ContestCardProps {
  contest: {
    id: string;
    prizePool: number;
    entryFee: number;
    maxSpots: number;
    spotsLeft: number;
    isGuaranteed: boolean;
    isFlexible: boolean;
    winnerCount: number;
    winningPercentage: number;
    maxTeams: number;
    firstPrize?: number;
    isSpecial?: boolean;
    specialText?: string;
    specialImage?: string;
  };
  onJoin: (contestId: string) => void;
}

export function ContestCard({ contest, onJoin }: ContestCardProps) {
  const filledPercentage =
    ((contest.maxSpots - contest.spotsLeft) / contest.maxSpots) * 100;
  const spotsLeftPercentage = (contest.spotsLeft / contest.maxSpots) * 100;

  const formatCurrency = (amount: number) => {
    if (amount >= 10000000) {
      // 1 Crore
      return `₹${(amount / 10000000).toFixed(0)} Crores`;
    } else if (amount >= 100000) {
      // 1 Lakh
      return `₹${(amount / 100000).toFixed(amount >= 1000000 ? 0 : 2)} Lakhs`;
    } else {
      return `₹${amount}`;
    }
  };

  return (
    <Card className="overflow-hidden">
      {contest.isSpecial && contest.specialImage && (
        <div className="relative h-24 w-full bg-gradient-to-r from-primary/10 to-primary/5">
          <img
            src={contest.specialImage}
            alt={contest.specialText || "Contest banner"}
            className="absolute inset-0 h-full w-full object-cover"
          />
          {contest.specialText && (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-lg font-bold text-white shadow-sm">
                {contest.specialText}
              </p>
            </div>
          )}
        </div>
      )}

      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            {contest.isGuaranteed && (
              <Badge variant="success" className="gap-1">
                <Crown className="h-3 w-3" />
                Guaranteed
              </Badge>
            )}
            {contest.isFlexible && (
              <Badge variant="secondary" className="gap-1">
                <TrendingUp className="h-3 w-3" />
                Flexible
              </Badge>
            )}
          </div>
          <Button
            onClick={() => onJoin(contest.id)}
            className="bg-green-500 hover:bg-green-600 text-white"
          >
            ₹{contest.entryFee}
          </Button>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-orange-500" />
            <span className="text-xl font-bold">
              {formatCurrency(contest.prizePool)}
            </span>
          </div>
          {contest.firstPrize && (
            <div className="text-sm text-muted-foreground">
              ₹{contest.firstPrize.toLocaleString()} for Rank 1
            </div>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-red-500 font-medium">
              {contest.spotsLeft.toLocaleString()} spots left
            </span>
            <span className="text-muted-foreground">
              {contest.maxSpots.toLocaleString()} spots
            </span>
          </div>
          <Progress value={filledPercentage} className="h-2" />
        </div>

        <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Trophy className="h-4 w-4" />
            <span>{contest.winningPercentage}% Winners</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span>Upto {contest.maxTeams} Teams</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
