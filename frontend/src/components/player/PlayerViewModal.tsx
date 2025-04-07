"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

interface PlayerViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  player: any;
  onBid: (amount: number) => void;
  onSkip: () => void;
  currentBid: number;
  timeLeft: number;
}

export default function PlayerViewModal({
  isOpen,
  onClose,
  player,
  onBid,
  onSkip,
  currentBid,
  timeLeft,
}: PlayerViewModalProps) {
  const [bidAmount, setBidAmount] = useState<number>(currentBid + 5);

  const handleBid = () => {
    if (bidAmount <= currentBid) {
      toast.error("Bid amount must be higher than current bid");
      return;
    }
    onBid(bidAmount);
  };

  if (!player) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{player.name}</DialogTitle>
          <DialogDescription>Player Details and Bidding</DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Player Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="font-medium">Team: </span>
                  <span>{player.team}</span>
                </div>
                <div>
                  <span className="font-medium">Role: </span>
                  <span>{player.role}</span>
                </div>
                <div>
                  <span className="font-medium">Base Price: </span>
                  <span>₹{player.basePrice}</span>
                </div>
                <div>
                  <span className="font-medium">Stats: </span>
                  <div className="mt-1 space-y-1 text-sm">
                    <div>Matches: {player.stats?.matches || 0}</div>
                    <div>Runs: {player.stats?.runs || 0}</div>
                    <div>Wickets: {player.stats?.wickets || 0}</div>
                    <div>Average: {player.stats?.average || 0}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Current Auction</CardTitle>
              <CardDescription>Time Left: {timeLeft}s</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground">
                    Current Bid
                  </div>
                  <div className="text-2xl font-bold">₹{currentBid}</div>
                </div>

                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      value={bidAmount}
                      onChange={(e) => setBidAmount(Number(e.target.value))}
                      min={currentBid + 5}
                      step={5}
                    />
                    <Button onClick={handleBid}>Bid</Button>
                  </div>
                  <Button variant="outline" className="w-full" onClick={onSkip}>
                    Skip Player
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
}
