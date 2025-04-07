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
import PlayerViewModal from "@/components/player/PlayerViewModal";
import { toast } from "sonner";

// Mock data for testing
const mockPlayers = [
  {
    id: 1,
    name: "Virat Kohli",
    team: "RCB",
    role: "Batsman",
    basePrice: 200,
    stats: {
      matches: 250,
      runs: 12000,
      wickets: 0,
      average: 52.3,
    },
  },
  {
    id: 2,
    name: "Rohit Sharma",
    team: "MI",
    role: "Batsman",
    basePrice: 200,
    stats: {
      matches: 230,
      runs: 10000,
      wickets: 0,
      average: 48.5,
    },
  },
  {
    id: 3,
    name: "Jasprit Bumrah",
    team: "MI",
    role: "Bowler",
    basePrice: 150,
    stats: {
      matches: 180,
      runs: 200,
      wickets: 250,
      average: 22.1,
    },
  },
];

export default function AuctionPage() {
  const { activeGully } = useAppStore();
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
  const [currentBid, setCurrentBid] = useState(0);
  const [timeLeft, setTimeLeft] = useState(30);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [auctionStatus, setAuctionStatus] = useState<
    "not_started" | "in_progress" | "completed"
  >("not_started");
  const [highestBidder, setHighestBidder] = useState<string | null>(null);
  const [biddingHistory, setBiddingHistory] = useState<
    Array<{ player: string; amount: number; bidder: string }>
  >([]);

  const currentPlayer = mockPlayers[currentPlayerIndex];

  useEffect(() => {
    let timer: NodeJS.Timeout;

    if (auctionStatus === "in_progress" && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handlePlayerSold();
            return 30;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [auctionStatus, timeLeft]);

  const startAuction = () => {
    setAuctionStatus("in_progress");
    setCurrentPlayerIndex(0);
    setCurrentBid(mockPlayers[0].basePrice);
    setTimeLeft(30);
    setHighestBidder(null);
    setBiddingHistory([]);
  };

  const handleBid = (amount: number) => {
    if (amount <= currentBid) {
      toast.error("Bid amount must be higher than current bid");
      return;
    }

    setCurrentBid(amount);
    setTimeLeft(30); // Reset timer
    setHighestBidder("You"); // In a real app, use actual user name
    toast.success(`Bid placed: ₹${amount}`);
  };

  const handleSkip = () => {
    if (currentPlayerIndex < mockPlayers.length - 1) {
      moveToNextPlayer();
    } else {
      completeAuction();
    }
  };

  const handlePlayerSold = () => {
    if (highestBidder) {
      setBiddingHistory((prev) => [
        ...prev,
        {
          player: currentPlayer.name,
          amount: currentBid,
          bidder: highestBidder,
        },
      ]);
      toast.success(
        `${currentPlayer.name} sold to ${highestBidder} for ₹${currentBid}`
      );
    }

    if (currentPlayerIndex < mockPlayers.length - 1) {
      moveToNextPlayer();
    } else {
      completeAuction();
    }
  };

  const moveToNextPlayer = () => {
    setCurrentPlayerIndex((prev) => prev + 1);
    setCurrentBid(mockPlayers[currentPlayerIndex + 1].basePrice);
    setTimeLeft(30);
    setHighestBidder(null);
    setIsModalOpen(false);
  };

  const completeAuction = () => {
    setAuctionStatus("completed");
    setIsModalOpen(false);
    toast.success("Auction completed!");
  };

  if (!activeGully) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardHeader>
            <CardTitle>No Active Gully</CardTitle>
            <CardDescription>
              Please select a gully to participate in the auction
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">
            {activeGully.name} - Auction
          </h1>
          <p className="text-muted-foreground capitalize">
            Status: {auctionStatus.replace("_", " ")}
          </p>
        </div>

        {auctionStatus === "not_started" ? (
          <Card>
            <CardHeader>
              <CardTitle>Start Auction</CardTitle>
              <CardDescription>
                Begin the player auction process for your gully
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={startAuction}>Start Auction</Button>
            </CardContent>
          </Card>
        ) : auctionStatus === "in_progress" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Current Player</CardTitle>
                <CardDescription>Time Left: {timeLeft} seconds</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-medium">
                      {currentPlayer.name}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {currentPlayer.team} - {currentPlayer.role}
                    </p>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">
                      Current Bid
                    </div>
                    <div className="text-2xl font-bold">₹{currentBid}</div>
                    {highestBidder && (
                      <div className="text-sm text-muted-foreground">
                        Highest Bidder: {highestBidder}
                      </div>
                    )}
                  </div>
                  <div className="space-x-2">
                    <Button onClick={() => setIsModalOpen(true)}>
                      View Details & Bid
                    </Button>
                    <Button variant="outline" onClick={handleSkip}>
                      Skip Player
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Auction History</CardTitle>
                <CardDescription>
                  Recent transactions in this auction
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {biddingHistory.map((bid, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center border-b pb-2"
                    >
                      <div>
                        <p className="font-medium">{bid.player}</p>
                        <p className="text-sm text-muted-foreground">
                          Sold to: {bid.bidder}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">₹{bid.amount}</p>
                      </div>
                    </div>
                  ))}
                  {biddingHistory.length === 0 && (
                    <p className="text-muted-foreground">No players sold yet</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Auction Completed</CardTitle>
              <CardDescription>Summary of all transactions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {biddingHistory.map((bid, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center border-b pb-2"
                  >
                    <div>
                      <p className="font-medium">{bid.player}</p>
                      <p className="text-sm text-muted-foreground">
                        Sold to: {bid.bidder}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">₹{bid.amount}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <PlayerViewModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        player={currentPlayer}
        onBid={handleBid}
        onSkip={handleSkip}
        currentBid={currentBid}
        timeLeft={timeLeft}
      />
    </div>
  );
}
