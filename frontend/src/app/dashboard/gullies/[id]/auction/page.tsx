"use client";

import { useState, use, useEffect, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Clock, Users, DollarSign } from "lucide-react";
import { participantApi, auctionApi } from "@/lib/api-client";
import { useAppStore } from "@/lib/store";
import { useWebSocket } from "@/lib/hooks/useWebSocket";
import { teamLogos, teamColors, TeamCode } from "@/lib/data/teamLogos";

type PlayerStatus = {
  id: number;
  name: string;
  team: string;
  role: string;
  basePrice: number;
  stats: { average: number | null; economy: number | null };
  finalPrice?: number;
  status: "AVAILABLE" | "SOLD" | "SKIPPED";
  timestamp?: number;
  highestBidder?: string;
  timeLeft?: number;
};

type AuctionState = {
  status: "not_started" | "in_progress" | "completed";
  currentPlayer: PlayerStatus | null;
  auctionedPlayers: PlayerStatus[];
  skippedPlayers: PlayerStatus[];
  participants: {
    id: number;
    name: string;
    budget: number;
    players: PlayerStatus[];
  }[];
  timeLeft: number;
  currentBid: number;
  highestBidderId: number | null;
};

type BidData = {
  amount: number;
  participantId: number;
};

type TimerData = {
  timeLeft: number;
};

type Participant = {
  id: number;
  user_id: number;
  gully_id: number;
  team_name: string;
  players?: PlayerStatus[];
  budget?: number;
};

export default function AuctionPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { currentUser } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [currentParticipant, setCurrentParticipant] =
    useState<Participant | null>(null);
  const [auctionState, setAuctionState] = useState<AuctionState>({
    status: "not_started",
    currentPlayer: null,
    auctionedPlayers: [],
    skippedPlayers: [],
    participants: [],
    timeLeft: 30,
    currentBid: 0,
    highestBidderId: null,
  });
  const [bidAmount, setBidAmount] = useState("");
  const [wsError, setWsError] = useState<Error | null>(null);
  const [pollingEnabled, setPollingEnabled] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket connection for real-time updates
  const { lastMessage, readyState } = useWebSocket(
    `/ws/auction/${resolvedParams.id}`
  );

  // Use WebSocket readyState to detect connection issues
  useEffect(() => {
    if (readyState === WebSocket.CLOSED) {
      setWsError(new Error("WebSocket connection closed"));
      // Enable polling when WebSocket fails
      setPollingEnabled(true);

      // Show error notification only once when connection fails
      toast.error(
        "Live auction connection unavailable. Using fallback mode with limited updates.",
        {
          id: "websocket-connection-error",
          duration: 5000,
        }
      );
    } else if (readyState === WebSocket.OPEN) {
      setWsError(null);
      setPollingEnabled(false);

      // Clear any existing error notifications
      toast.dismiss("websocket-connection-error");
    }
  }, [readyState]);

  // Fallback polling mechanism when WebSocket fails
  useEffect(() => {
    if (pollingEnabled) {
      // Clear any existing polling interval
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      // Start polling every 3 seconds
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const auctionQueue = await auctionApi.getAuctionQueue(
            Number(resolvedParams.id)
          );

          if (auctionQueue && auctionQueue.length > 0) {
            // Update auction state based on polled data
            setAuctionState((prev) => ({
              ...prev,
              currentPlayer: auctionQueue[0] || null,
              status: auctionQueue.length > 0 ? "in_progress" : "not_started",
              // Simulate timer decreasing
              timeLeft: prev.timeLeft > 0 ? prev.timeLeft - 1 : 30,
            }));
          }
        } catch (error) {
          console.error("Polling error:", error);
        }
      }, 3000);
    }

    // Cleanup polling on component unmount or when WebSocket reconnects
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [pollingEnabled, resolvedParams.id]);

  const handleNewBid = useCallback(
    (bidData: BidData) => {
      setAuctionState((prev) => ({
        ...prev,
        currentBid: bidData.amount,
        highestBidderId: bidData.participantId,
        timeLeft: 30, // Reset timer on new bid
      }));

      if (bidData.participantId === currentParticipant?.id) {
        toast.success(`Your bid of ₹${bidData.amount} is currently winning!`);
      }
    },
    [currentParticipant]
  );

  const handleTimerUpdate = useCallback((timerData: TimerData) => {
    setAuctionState((prev) => ({
      ...prev,
      timeLeft: timerData.timeLeft,
    }));

    if (timerData.timeLeft <= 5) {
      toast.warning(`${timerData.timeLeft} seconds remaining!`);
    }
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data);
        switch (data.type) {
          case "auction_update":
            setAuctionState((prev) => ({
              ...prev,
              ...data.payload,
            }));
            break;
          case "new_bid":
            handleNewBid(data.payload);
            break;
          case "timer_update":
            handleTimerUpdate(data.payload);
            break;
        }
      } catch (err) {
        console.warn("Error parsing WebSocket message:", err);
      }
    }
  }, [lastMessage, handleNewBid, handleTimerUpdate]);

  // Check and join gully if needed
  useEffect(() => {
    const checkAndJoinGully = async () => {
      if (!currentUser) {
        toast.error("Please log in to participate in auctions");
        router.push("/auth/login");
        return;
      }

      try {
        const participants = await participantApi.getParticipants(
          Number(resolvedParams.id)
        );
        const foundParticipant = participants.find(
          (p: Participant) => p.user_id === currentUser.id
        );

        if (!foundParticipant) {
          const newParticipant = await participantApi.joinGully({
            gully_id: Number(resolvedParams.id),
            user_id: currentUser.id,
            team_name: `${currentUser.username}'s Team`,
          });
          setCurrentParticipant(newParticipant);
          toast.success("Successfully joined the gully!");
        } else {
          setCurrentParticipant(foundParticipant);
        }

        // Fetch initial auction state
        const auctionQueue = await auctionApi.getAuctionQueue(
          Number(resolvedParams.id)
        );
        // Update auction state based on queue
        setAuctionState((prev) => ({
          ...prev,
          currentPlayer: auctionQueue[0] || null,
          status: auctionQueue.length > 0 ? "in_progress" : "not_started",
        }));
      } catch (error) {
        console.error("Error checking/joining gully:", error);
        toast.error("Failed to join the gully. Please try again.");
        router.push(`/dashboard/gullies/${resolvedParams.id}`);
      }
    };

    checkAndJoinGully();
  }, [currentUser, resolvedParams.id, router]);

  const handleBid = async () => {
    if (!currentParticipant) {
      toast.error("Please wait while we set up your participation");
      return;
    }

    const amount = parseInt(bidAmount);
    if (isNaN(amount) || amount <= auctionState.currentBid) {
      toast.error(
        `Bid must be higher than current bid (₹${auctionState.currentBid})`
      );
      return;
    }

    setLoading(true);
    try {
      await auctionApi.placeBid({
        auction_queue_id: auctionState.currentPlayer!.id,
        gully_participant_id: currentParticipant.id,
        bid_amount: amount,
      });
      setBidAmount("");
    } catch (error) {
      console.error("Error placing bid:", error);
      toast.error("Failed to place bid. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const renderAuctionStatus = () => {
    return (
      <div className="flex items-center gap-4 mb-6">
        <Card className="p-4 flex-1 bg-gray-900">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-blue-400" />
            <div>
              <p className="text-sm text-gray-400">Time Left</p>
              <p className="text-xl font-bold text-white">
                {auctionState.timeLeft}s
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4 flex-1 bg-gray-900">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-green-400" />
            <div>
              <p className="text-sm text-gray-400">Participants</p>
              <p className="text-xl font-bold text-white">
                {auctionState.participants.length}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4 flex-1 bg-gray-900">
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-yellow-400" />
            <div>
              <p className="text-sm text-gray-400">Current Bid</p>
              <p className="text-xl font-bold text-white">
                ₹{auctionState.currentBid}
              </p>
            </div>
          </div>
        </Card>
      </div>
    );
  };

  const renderCurrentPlayer = () => {
    if (!auctionState.currentPlayer) return null;

    return (
      <Card className="p-6 mb-6 bg-gray-900">
        <div className="flex justify-between items-start mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold text-white">
                {auctionState.currentPlayer.name}
              </h2>
              <Badge variant="outline">
                {auctionState.currentPlayer.status}
              </Badge>
            </div>
            <div className="flex gap-2 mb-2">
              <Badge
                className={
                  teamColors[auctionState.currentPlayer.team as TeamCode] ||
                  "bg-gray-500"
                }
              >
                {auctionState.currentPlayer.team}
              </Badge>
              <Badge className={getRoleColor(auctionState.currentPlayer.role)}>
                {auctionState.currentPlayer.role}
              </Badge>
            </div>
            <p className="text-sm text-gray-300">
              Base Price: ₹{auctionState.currentPlayer.basePrice}
            </p>
            {auctionState.currentPlayer.stats?.average && (
              <p className="text-sm text-gray-300">
                Average: {auctionState.currentPlayer.stats.average}
              </p>
            )}
            {auctionState.currentPlayer.stats?.economy && (
              <p className="text-sm text-gray-300">
                Economy: {auctionState.currentPlayer.stats.economy}
              </p>
            )}
          </div>
        </div>

        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1 text-white">
              Your Bid
            </label>
            <Input
              type="number"
              value={bidAmount}
              onChange={(e) => setBidAmount(e.target.value)}
              placeholder={`Minimum ₹${auctionState.currentBid + 1}`}
              min={auctionState.currentBid + 1}
              className="bg-gray-800 text-white placeholder-gray-400"
              disabled={loading}
            />
          </div>
          <Button
            onClick={handleBid}
            className="bg-green-600 hover:bg-green-700"
            disabled={loading}
          >
            {loading ? "Placing Bid..." : "Place Bid"}
          </Button>
        </div>
      </Card>
    );
  };

  const renderParticipants = () => {
    return (
      <Card className="p-4 bg-gray-900">
        <h3 className="text-lg font-semibold mb-4 text-white">Participants</h3>
        <div className="space-y-2">
          {auctionState.participants.map((participant) => (
            <div
              key={participant.id}
              className="flex justify-between items-center p-2 bg-gray-800 rounded"
            >
              <div className="flex items-center gap-2">
                <span className="text-white">{participant.name}</span>
                {participant.id === auctionState.highestBidderId && (
                  <Badge variant="success" className="text-xs">
                    Highest Bidder
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline">₹{participant.budget}</Badge>
                <Badge>{participant.players.length} Players</Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  };

  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      Batsman: "bg-blue-500",
      Bowler: "bg-green-500",
      "All-rounder": "bg-purple-500",
      "Wicket-keeper": "bg-yellow-500",
    };
    return colors[role] || "bg-gray-500";
  };

  // Function to get team logo
  const getTeamLogo = (teamCode: string): string => {
    return teamLogos[teamCode as TeamCode] || "";
  };

  // Add connection status indicator
  const renderConnectionStatus = () => {
    if (wsError) {
      return (
        <Card className="p-4 bg-amber-900 mb-4 border border-amber-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="mr-3 text-amber-300">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-white">
                  Limited Connectivity
                </h3>
                <p className="text-sm text-amber-300">
                  Using polling fallback. Refresh for most recent data.
                </p>
              </div>
            </div>
            <Button
              onClick={() => window.location.reload()}
              variant="outline"
              size="sm"
              className="border-amber-400 text-amber-200 hover:bg-amber-800"
            >
              Refresh
            </Button>
          </div>
        </Card>
      );
    }
    return null;
  };

  return (
    <>
      <style jsx global>{`
        button,
        [role="button"],
        a,
        .cursor-pointer {
          cursor: pointer !important;
        }
      `}</style>
      <div className="container mx-auto p-4">
        <div className="flex items-center mb-6">
          <Link
            href={`/dashboard/gullies/${resolvedParams.id}`}
            className="mr-4"
          >
            <Button variant="ghost" size="icon">
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold text-white">Live Auction</h1>
        </div>

        {renderConnectionStatus()}

        {renderAuctionStatus()}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {renderCurrentPlayer()}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-4 bg-gray-900">
                <h3 className="text-lg font-semibold mb-4 text-white">
                  Auctioned Players ({auctionState.auctionedPlayers.length})
                </h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {auctionState.auctionedPlayers.map((player) => (
                    <div
                      key={`${player.id}-${player.timestamp}`}
                      className="flex justify-between items-center p-2 bg-gray-800 rounded"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-white">{player.name}</span>
                        <Badge variant="success" className="text-xs">
                          SOLD
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          className={
                            teamColors[player.team as TeamCode] || "bg-gray-500"
                          }
                        >
                          {player.team}
                        </Badge>
                        <span className="text-green-400">
                          ₹{player.finalPrice}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-4 bg-gray-900">
                <h3 className="text-lg font-semibold mb-4 text-white">
                  Skipped Players ({auctionState.skippedPlayers.length})
                </h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {auctionState.skippedPlayers.map((player) => (
                    <div
                      key={`${player.id}-${player.timestamp}`}
                      className="flex justify-between items-center p-2 bg-gray-800 rounded"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-white">{player.name}</span>
                        <Badge variant="secondary" className="text-xs">
                          SKIPPED
                        </Badge>
                      </div>
                      <Badge
                        className={
                          teamColors[player.team as TeamCode] || "bg-gray-500"
                        }
                      >
                        {player.team}
                      </Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>

          <div className="lg:col-span-1">{renderParticipants()}</div>
        </div>
      </div>
    </>
  );
}
