import React, { useEffect, useState } from "react";
import useWebSocket from "react-use-websocket";
import { toast } from "react-hot-toast";
import { Card, Badge, Button, Input } from "@/components/ui";
import { Link } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import {
  getAuctionData,
  simulateBid,
  simulateCompletedAuction,
} from "@/lib/data/mock-auction-data";

const AuctionPage: React.FC = () => {
  const [auctionState, setAuctionState] = useState({
    currentPlayer: {
      basePrice: 0,
      stats: {
        average: 0,
        economy: 0,
      },
      name: "",
      team: "",
      role: "",
      status: "AVAILABLE",
    },
    currentBid: 0,
    timeLeft: 30,
    highestBidderId: null,
  });

  // WebSocket connection for real-time updates
  const {
    lastMessage,
    error: wsError,
    isConnected,
    reconnect,
  } = useWebSocket(`/ws/auction/${resolvedParams.id}`);

  // Display WebSocket connection error notification
  useEffect(() => {
    if (wsError) {
      toast.error("Connection error: Unable to connect to live auction server");
      console.warn("WebSocket connection error:", wsError);
    }
  }, [wsError]);

  // Retry WebSocket connection every 5 seconds if not connected
  useEffect(() => {
    let retryInterval: NodeJS.Timeout | null = null;
    if (!isConnected && !loading) {
      retryInterval = setInterval(() => {
        console.log("Attempting to reconnect WebSocket...");
        reconnect();
      }, 5000);
    }
    return () => {
      if (retryInterval) clearInterval(retryInterval);
    };
  }, [isConnected, loading, reconnect]);

  // Load initial mock data for fallback
  useEffect(() => {
    if (wsError || !isConnected) {
      const mockData = getAuctionData(resolvedParams.id);
      setAuctionState(mockData);
      console.log("Using mock auction data due to WebSocket connection issue");
    }
  }, [wsError, isConnected, resolvedParams.id]);

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
      } catch (error) {
        console.warn("Error parsing WebSocket message:", error);
      }
    }
  }, [lastMessage, handleNewBid, handleTimerUpdate]);

  const renderConnectionStatus = () => {
    if (wsError) {
      return (
        <Card className="p-4 bg-red-900 mb-4">
          <div className="flex items-center">
            <div className="mr-2 text-red-300">
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
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-white">Connection Error</h3>
              <p className="text-sm text-red-300">
                Unable to connect to the auction server. Using cached data.
              </p>
            </div>
            <Button
              variant="outline"
              className="ml-auto border-red-300 text-red-300 hover:bg-red-800"
              onClick={() => reconnect()}
            >
              Retry
            </Button>
          </div>
        </Card>
      );
    }

    if (!isConnected) {
      return (
        <Card className="p-4 bg-yellow-900 mb-4">
          <div className="flex items-center">
            <div className="mr-2 text-yellow-300">
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
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-white">Connecting...</h3>
              <p className="text-sm text-yellow-300">
                Attempting to connect to the auction server.
              </p>
            </div>
          </div>
        </Card>
      );
    }

    return null;
  };

  const renderCurrentPlayer = () => {
    if (!auctionState.currentPlayer)
      return (
        <Card className="p-6 mb-6 bg-gray-900">
          <div className="text-center p-8">
            <p className="text-gray-400">
              No active player auction at the moment
            </p>
          </div>
        </Card>
      );

    const { name, status, team, role, basePrice, stats } =
      auctionState.currentPlayer;
    const playerStats = stats || { average: null, economy: null };

    return (
      <Card className="p-6 mb-6 bg-gray-900">
        <div className="flex justify-between items-start mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold text-white">
                {name || "Player Name"}
              </h2>
              <Badge variant="outline">{status || "AVAILABLE"}</Badge>
            </div>
            <div className="flex gap-2 mb-2">
              <Badge className={teamColors[team as TeamCode] || "bg-gray-500"}>
                {team || "Team"}
              </Badge>
              <Badge className={getRoleColor(role || "")}>
                {role || "Role"}
              </Badge>
            </div>
            <p className="text-sm text-gray-300">
              Base Price: ₹{basePrice || 0}
            </p>
            {playerStats.average && (
              <p className="text-sm text-gray-300">
                Average: {playerStats.average}
              </p>
            )}
            {playerStats.economy && (
              <p className="text-sm text-gray-300">
                Economy: {playerStats.economy}
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
              placeholder={`Minimum ₹${auctionState.currentBid + 1 || 0}`}
              min={auctionState.currentBid + 1 || 0}
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

  const handleBid = async () => {
    if (!currentParticipant) {
      toast.error("Please wait while we set up your participation");
      return;
    }

    if (!auctionState.currentPlayer) {
      toast.error("No active player auction at the moment");
      return;
    }

    const amount = parseInt(bidAmount);
    if (isNaN(amount) || amount <= auctionState.currentBid) {
      toast.error(
        `Bid must be higher than current bid (₹${auctionState.currentBid || 0})`
      );
      return;
    }

    setLoading(true);
    try {
      if (isConnected) {
        // If WebSocket is connected, use it to place the bid
        await auctionApi.placeBid({
          auction_queue_id: auctionState.currentPlayer.id,
          gully_participant_id: currentParticipant.id,
          bid_amount: amount,
        });
      } else {
        // Fallback to mock implementation if WebSocket is not available
        try {
          const updatedState = simulateBid(
            auctionState,
            amount,
            currentParticipant.id
          );
          setAuctionState(updatedState);
          toast.success(`Bid placed successfully: ₹${amount}`);
        } catch (error) {
          toast.error(
            error instanceof Error ? error.message : "Failed to place bid"
          );
          throw error;
        }
      }
      setBidAmount("");
    } catch (error) {
      console.error("Error placing bid:", error);
      toast.error("Failed to place bid. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center mb-6">
        <Link href={`/dashboard/gullies/${resolvedParams.id}`} className="mr-4">
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
            {/* ...rest of the content... */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuctionPage;
