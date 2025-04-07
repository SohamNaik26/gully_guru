"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAppStore } from "@/lib/store";
import { gullyApi, participantApi } from "@/lib/api-client";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import {
  Users,
  Award,
  TrendingUp,
  Clock,
  ChevronLeft,
  Gavel,
  Settings,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { IPL_PLAYERS, IPL_TEAMS, Player, TeamName } from "@/lib/data/players";
import { MatchDetailsDialog } from "@/components/match-details-dialog";
import { useToast } from "@/components/ui/use-toast";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { TelegramService } from "@/lib/services/telegram";
import Link from "next/link";
import { TeamEditor } from "./components/TeamEditor";
import { GullyEditor } from "./components/GullyEditor";

interface GullyParticipant {
  id: number;
  user_id: number;
  team_name: string;
  role: string;
  players?: Player[];
}

interface Match {
  team1: TeamName;
  team2: TeamName;
  date: string;
  venue: string;
  time: string;
  probablePlayers?: {
    team1: string[];
    team2: string[];
  };
  headToHead?: {
    total: number;
    team1Wins: number;
    team2Wins: number;
    draws: number;
  };
  liveScore?: {
    team1: {
      runs: number;
      wickets: number;
      overs: number;
      runRate: number;
      battingStats: {
        player: string;
        runs: number;
        balls: number;
        fours: number;
        sixes: number;
        strikeRate: number;
      }[];
      bowlingStats: {
        player: string;
        overs: number;
        runs: number;
        wickets: number;
        economy: number;
      }[];
    };
    team2: {
      runs: number;
      wickets: number;
      overs: number;
      runRate: number;
      battingStats: {
        player: string;
        runs: number;
        balls: number;
        fours: number;
        sixes: number;
        strikeRate: number;
      }[];
      bowlingStats: {
        player: string;
        overs: number;
        runs: number;
        wickets: number;
        economy: number;
      }[];
    };
    matchStatus: string;
    recentOvers: { over: number; runs: (number | string)[] }[];
    commentary: string[];
  };
}

interface EditGullyFormData {
  name: string;
  telegram_group_id?: string;
}

const MOCK_MATCHES: Match[] = [
  {
    team1: "MI",
    team2: "RCB",
    date: "Mar 22, 2025",
    time: "7:30 PM",
    venue: "Wankhede Stadium, Mumbai",
    probablePlayers: {
      team1: [
        "Rohit Sharma",
        "Ishan Kishan",
        "Suryakumar Yadav",
        "Tilak Varma",
        "Tim David",
        "Hardik Pandya",
        "Romario Shepherd",
        "Piyush Chawla",
        "Gerald Coetzee",
        "Jasprit Bumrah",
        "Akash Madhwal",
      ],
      team2: [
        "Faf du Plessis",
        "Virat Kohli",
        "Rajat Patidar",
        "Glenn Maxwell",
        "Cameron Green",
        "Dinesh Karthik",
        "Mahipal Lomror",
        "Reece Topley",
        "Mohammed Siraj",
        "Karn Sharma",
        "Yash Dayal",
      ],
    },
    headToHead: {
      total: 32,
      team1Wins: 18,
      team2Wins: 14,
      draws: 0,
    },
    liveScore: {
      team1: {
        runs: 128,
        wickets: 2,
        overs: 12.4,
        runRate: 10.11,
        battingStats: [
          {
            player: "Rohit Sharma",
            runs: 65,
            balls: 32,
            fours: 6,
            sixes: 4,
            strikeRate: 203.13,
          },
          {
            player: "Suryakumar Yadav",
            runs: 42,
            balls: 24,
            fours: 3,
            sixes: 3,
            strikeRate: 175.0,
          },
        ],
        bowlingStats: [],
      },
      team2: {
        runs: 0,
        wickets: 0,
        overs: 0,
        runRate: 0,
        battingStats: [],
        bowlingStats: [
          {
            player: "Mohammed Siraj",
            overs: 4,
            runs: 38,
            wickets: 0,
            economy: 9.5,
          },
          {
            player: "Reece Topley",
            overs: 4,
            runs: 32,
            wickets: 1,
            economy: 8.0,
          },
          {
            player: "Glenn Maxwell",
            overs: 2,
            runs: 18,
            wickets: 0,
            economy: 9.0,
          },
          {
            player: "Cameron Green",
            overs: 2.4,
            runs: 29,
            wickets: 1,
            economy: 10.88,
          },
        ],
      },
      matchStatus: "In Progress - MI Batting",
      recentOvers: [
        { over: 8, runs: [1, 4, 6, 2, 0, 1] },
        { over: 9, runs: [4, 0, 1, 6, 4, 0] },
        { over: 10, runs: [0, 1, 4, 1, 1, 1] },
        { over: 11, runs: [6, 4, 1, 2, 0, 2] },
        { over: 12, runs: [1, 4, 0, 6, "W", 4] },
      ],
      commentary: [
        "12.4: GREEN to TILAK, FOUR! Beautifully driven through covers.",
        "12.3: GREEN to TILAK, OUT! Caught at deep midwicket. SKY departs for a well-made 42.",
        "12.2: GREEN to SKY, DOT BALL. Beaten outside off stump.",
        "12.1: GREEN to SKY, SIX! Magnificent shot over long-on!",
        "11.6: MAXWELL to ROHIT, TWO RUNS. Pushed to deep extra cover.",
      ],
    },
  },
  {
    team1: "CSK",
    team2: "KKR",
    date: "Mar 24, 2025",
    time: "7:30 PM",
    venue: "MA Chidambaram Stadium, Chennai",
    probablePlayers: {
      team1: [
        "Ruturaj Gaikwad",
        "Rachin Ravindra",
        "Ajinkya Rahane",
        "Daryl Mitchell",
        "Shivam Dube",
        "Ravindra Jadeja",
        "MS Dhoni",
        "Deepak Chahar",
        "Tushar Deshpande",
        "Maheesh Theekshana",
        "Mustafizur Rahman",
      ],
      team2: [
        "Shreyas Iyer",
        "Phil Salt",
        "Venkatesh Iyer",
        "Nitish Rana",
        "Rinku Singh",
        "Andre Russell",
        "Sunil Narine",
        "Mitchell Starc",
        "Varun Chakravarthy",
        "Harshit Rana",
        "Vaibhav Arora",
      ],
    },
    headToHead: {
      total: 28,
      team1Wins: 16,
      team2Wins: 12,
      draws: 0,
    },
    liveScore: {
      team1: {
        runs: 198,
        wickets: 8,
        overs: 20,
        runRate: 9.9,
        battingStats: [
          {
            player: "Ruturaj Gaikwad",
            runs: 78,
            balls: 52,
            fours: 8,
            sixes: 3,
            strikeRate: 150.0,
          },
          {
            player: "Shivam Dube",
            runs: 44,
            balls: 25,
            fours: 2,
            sixes: 4,
            strikeRate: 176.0,
          },
          {
            player: "MS Dhoni",
            runs: 28,
            balls: 15,
            fours: 1,
            sixes: 3,
            strikeRate: 186.67,
          },
        ],
        bowlingStats: [],
      },
      team2: {
        runs: 62,
        wickets: 3,
        overs: 6.4,
        runRate: 9.3,
        battingStats: [
          {
            player: "Phil Salt",
            runs: 32,
            balls: 18,
            fours: 4,
            sixes: 2,
            strikeRate: 177.78,
          },
          {
            player: "Shreyas Iyer",
            runs: 12,
            balls: 8,
            fours: 1,
            sixes: 1,
            strikeRate: 150.0,
          },
          {
            player: "Venkatesh Iyer",
            runs: 14,
            balls: 12,
            fours: 1,
            sixes: 1,
            strikeRate: 116.67,
          },
        ],
        bowlingStats: [
          {
            player: "Mitchell Starc",
            overs: 4,
            runs: 48,
            wickets: 1,
            economy: 12.0,
          },
          {
            player: "Sunil Narine",
            overs: 4,
            runs: 24,
            wickets: 3,
            economy: 6.0,
          },
          {
            player: "Andre Russell",
            overs: 3,
            runs: 36,
            wickets: 0,
            economy: 12.0,
          },
          {
            player: "Varun Chakravarthy",
            overs: 4,
            runs: 32,
            wickets: 2,
            economy: 8.0,
          },
        ],
      },
      matchStatus: "In Progress - KKR Batting",
      recentOvers: [
        { over: 2, runs: [1, 0, 4, 6, 1, 0] },
        { over: 3, runs: [4, 1, 0, 1, "W", 0] },
        { over: 4, runs: [1, 1, 4, 0, 1, 2] },
        { over: 5, runs: [0, 6, 1, 4, 1, 1] },
        { over: 6, runs: [4, 1, 1, 2, "W", 0] },
      ],
      commentary: [
        "6.4: THEEKSHANA to NITISH, DOT BALL. Good defensive shot.",
        "6.3: THEEKSHANA to SHREYAS, OUT! Caught by Jadeja at deep midwicket.",
        "6.2: THEEKSHANA to VENKATESH, TWO RUNS. Pushed to long-on.",
        "6.1: THEEKSHANA to VENKATESH, ONE RUN. Worked to midwicket.",
        "5.6: CHAHAR to VENKATESH, ONE RUN. Pushed to cover.",
      ],
    },
  },
  {
    team1: "DC",
    team2: "PBKS",
    date: "Mar 26, 2025",
    time: "7:30 PM",
    venue: "Arun Jaitley Stadium, Delhi",
    probablePlayers: {
      team1: [
        "David Warner",
        "Prithvi Shaw",
        "Mitchell Marsh",
        "Rishabh Pant",
        "Ricky Bhui",
        "Axar Patel",
        "Kuldeep Yadav",
        "Anrich Nortje",
        "Mukesh Kumar",
        "Ishant Sharma",
        "Khaleel Ahmed",
      ],
      team2: [
        "Shikhar Dhawan",
        "Jonny Bairstow",
        "Prabhsimran Singh",
        "Liam Livingstone",
        "Sam Curran",
        "Jitesh Sharma",
        "Harpreet Brar",
        "Kagiso Rabada",
        "Rahul Chahar",
        "Arshdeep Singh",
        "Harshal Patel",
      ],
    },
    headToHead: {
      total: 32,
      team1Wins: 16,
      team2Wins: 16,
      draws: 0,
    },
    liveScore: {
      team1: {
        runs: 204,
        wickets: 7,
        overs: 20,
        runRate: 10.2,
        battingStats: [
          {
            player: "David Warner",
            runs: 42,
            balls: 29,
            fours: 4,
            sixes: 2,
            strikeRate: 144.83,
          },
          {
            player: "Rishabh Pant",
            runs: 68,
            balls: 34,
            fours: 6,
            sixes: 4,
            strikeRate: 200.0,
          },
          {
            player: "Axar Patel",
            runs: 36,
            balls: 18,
            fours: 2,
            sixes: 3,
            strikeRate: 200.0,
          },
        ],
        bowlingStats: [],
      },
      team2: {
        runs: 172,
        wickets: 10,
        overs: 18.4,
        runRate: 9.21,
        battingStats: [
          {
            player: "Jonny Bairstow",
            runs: 54,
            balls: 36,
            fours: 5,
            sixes: 2,
            strikeRate: 150.0,
          },
          {
            player: "Liam Livingstone",
            runs: 48,
            balls: 28,
            fours: 3,
            sixes: 4,
            strikeRate: 171.43,
          },
          {
            player: "Sam Curran",
            runs: 28,
            balls: 18,
            fours: 2,
            sixes: 1,
            strikeRate: 155.56,
          },
        ],
        bowlingStats: [
          {
            player: "Arshdeep Singh",
            overs: 4,
            runs: 42,
            wickets: 2,
            economy: 10.5,
          },
          {
            player: "Kagiso Rabada",
            overs: 4,
            runs: 38,
            wickets: 3,
            economy: 9.5,
          },
          {
            player: "Harshal Patel",
            overs: 4,
            runs: 48,
            wickets: 1,
            economy: 12.0,
          },
        ],
      },
      matchStatus: "Completed - DC won by 32 runs",
      recentOvers: [
        { over: 16, runs: [0, 1, 4, "W", 1, 0] },
        { over: 17, runs: [6, 1, 2, "W", 0, 1] },
        { over: 18, runs: [4, 1, "W", 0, 2, 1] },
        { over: 19, runs: ["W", 0, "W", 0, 0, "W"] },
      ],
      commentary: [
        "18.4: NORTJE to CHAHAR, OUT! Bowled! PBKS all out for 172!",
        "18.3: NORTJE to CHAHAR, DOT BALL. Beaten outside off stump.",
        "18.2: NORTJE to RABADA, OUT! Caught at long-on by Marsh.",
        "18.1: NORTJE to RABADA, DOT BALL. Swing and a miss.",
        "17.6: KULDEEP to CHAHAR, ONE RUN. Pushed to cover.",
      ],
    },
  },
];

export default function GullyDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const gullyId = Number(params.id);
  const [loading, setLoading] = useState(true);
  const [gully, setGully] = useState<any>(null);
  const [participants, setParticipants] = useState<GullyParticipant[]>([]);
  const [selectedParticipant, setSelectedParticipant] =
    useState<GullyParticipant | null>(null);
  const [isViewTeamOpen, setIsViewTeamOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const { currentUser, setActiveGully, activeGully, setUserGullies } =
    useAppStore();
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const { toast } = useToast();
  const [isEditGullyOpen, setIsEditGullyOpen] = useState(false);
  const [editFormData, setEditFormData] = useState<EditGullyFormData>({
    name: "",
    telegram_group_id: "",
  });

  useEffect(() => {
    const fetchGullyDetails = async () => {
      try {
        setLoading(true);
        // Fetch gully details
        const gullyData = await gullyApi.getGully(gullyId);
        setGully(gullyData);

        // Set as active gully
        setActiveGully(gullyData);

        // Fetch participants
        const participantsData = await participantApi.getParticipants(gullyId);
        setParticipants(participantsData);
      } catch (error) {
        console.error("Error fetching gully details:", error);
        toast.error("Failed to load gully details");
      } finally {
        setLoading(false);
      }
    };

    if (gullyId) {
      fetchGullyDetails();
    }
  }, [gullyId, setActiveGully]);

  const handleViewTeam = (participant: GullyParticipant) => {
    setSelectedParticipant(participant);
    setIsViewTeamOpen(true);
    setIsEditMode(false);
  };

  const handleEditGully = (participant: GullyParticipant) => {
    setSelectedParticipant(participant);
    setIsViewTeamOpen(true);
    setIsEditMode(true);
  };

  const handleCopyInviteLink = async () => {
    try {
      const inviteLink = `${window.location.origin}/join-gully/${gullyId}`;
      await navigator.clipboard.writeText(inviteLink);
      toast({
        title: "Success",
        description: "Invite link copied to clipboard",
      });
    } catch (error) {
      console.error("Error copying link:", error);
      toast({
        title: "Error",
        description: "Failed to copy invite link",
        variant: "destructive",
      });
    }
  };

  const handleEditGullyOpen = () => {
    setEditFormData({
      name: gully.name,
      telegram_group_id: gully.telegram_group_id?.toString() || "",
    });
    setIsEditGullyOpen(true);
  };

  const handleEditGullySave = async () => {
    try {
      if (!gully) return;

      // Validate telegram group ID if provided
      if (editFormData.telegram_group_id) {
        const isValid = await TelegramService.validateChatId(
          editFormData.telegram_group_id
        );
        if (!isValid) {
          toast({
            title: "Invalid Telegram Group ID",
            description:
              "Please check the group ID and make sure the bot is added to the group.",
            variant: "destructive",
          });
          return;
        }
      }

      // Update gully using the API
      const updatedGully = await gullyApi.updateGully(gully.id, editFormData);

      // Update local state
      setGully(updatedGully);
      setActiveGully(updatedGully);

      // Update gullies list
      const updatedGullies = userGullies.map((g) =>
        g.id === updatedGully.id ? updatedGully : g
      );
      setUserGullies(updatedGullies);

      // Close dialog and show success message
      setIsEditGullyOpen(false);
      toast({
        title: "Gully Updated",
        description: "Your gully has been updated successfully.",
      });
    } catch (error) {
      console.error("Error updating gully:", error);
      toast({
        title: "Update Failed",
        description: "Failed to update gully. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleDeleteGully = async () => {
    if (!gully) return;

    try {
      const confirmed = window.confirm(
        "Are you sure you want to delete this gully? This action cannot be undone."
      );

      if (!confirmed) return;

      const response = await fetch(`/api/gullies/${gullyId}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete gully");

      toast({
        title: "Success",
        description: "Gully deleted successfully",
      });
      router.push("/dashboard/gullies");
    } catch (error) {
      console.error("Error deleting gully:", error);
      toast({
        title: "Error",
        description: "Failed to delete gully",
        variant: "destructive",
      });
    }
  };

  const handleSaveTeam = async (players: Player[]) => {
    if (!selectedParticipant) return;

    try {
      // Update the team using the participantApi
      await participantApi.updateTeam(selectedParticipant.id, players);

      // Update the local state
      const updatedParticipants = participants.map((participant) => {
        if (participant.id === selectedParticipant.id) {
          return {
            ...participant,
            players: players,
          };
        }
        return participant;
      });
      setParticipants(updatedParticipants);

      // Close the dialog and show success message
      setIsViewTeamOpen(false);
      toast({
        title: "Success",
        description: "Team updated successfully",
      });
    } catch (error) {
      console.error("Error updating team:", error);
      toast({
        title: "Error",
        description: "Failed to update team. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!gully) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardHeader>
            <CardTitle>Gully Not Found</CardTitle>
            <CardDescription>
              The gully you are looking for could not be found.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Link href="/dashboard/gullies" className="mr-2">
              <Button variant="ghost" size="icon">
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold">{gully.name}</h1>
          </div>
          <div className="flex gap-2">
            <Link href={`/dashboard/gullies/${params.id}/auction`}>
              <Button variant="outline" className="gap-2">
                <Gavel className="h-4 w-4" />
                Auction Players
              </Button>
            </Link>
            <Button
              onClick={handleEditGully}
              variant="outline"
              className="gap-2"
            >
              <Settings className="h-4 w-4" />
              Edit Gully
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-medium">
                Participants
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className="text-2xl font-bold">
                  {participants.length}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-medium">Your Rank</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                <span className="text-2xl font-bold">4th</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-medium">Points</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Award className="h-4 w-4 text-muted-foreground" />
                <span className="text-2xl font-bold">320</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-medium">
                Next Match
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-2xl font-bold">2d</span>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="participants" className="space-y-4">
          <TabsList>
            <TabsTrigger value="participants">Participants</TabsTrigger>
            <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
            <TabsTrigger value="matches">Matches</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="participants" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Participants</CardTitle>
                <CardDescription>
                  Members participating in this gully
                </CardDescription>
              </CardHeader>
              <CardContent>
                {participants.length > 0 ? (
                  <div className="space-y-2">
                    {participants.map((participant) => (
                      <div
                        key={participant.id}
                        className="flex items-center justify-between border-b pb-2"
                      >
                        <div>
                          <p className="font-medium">{participant.team_name}</p>
                          <p className="text-sm text-muted-foreground capitalize">
                            Role: {participant.role}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewTeam(participant)}
                          >
                            View Team
                          </Button>
                          {participant.role === "admin" && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditGully(participant)}
                            >
                              Edit Team
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No participants yet. Invite your friends to join!</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="leaderboard">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Leaderboard</CardTitle>
                <CardDescription>
                  Current standings in this gully
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between border-b pb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">1.</span>
                      <div>
                        <p className="font-medium">Team Alpha</p>
                        <p className="text-sm text-muted-foreground">
                          450 points
                        </p>
                      </div>
                    </div>
                    <Award className="h-5 w-5 text-yellow-500" />
                  </div>
                  <div className="flex items-center justify-between border-b pb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">2.</span>
                      <div>
                        <p className="font-medium">Team Beta</p>
                        <p className="text-sm text-muted-foreground">
                          420 points
                        </p>
                      </div>
                    </div>
                    <Award className="h-5 w-5 text-gray-400" />
                  </div>
                  <div className="flex items-center justify-between border-b pb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">3.</span>
                      <div>
                        <p className="font-medium">Team Gamma</p>
                        <p className="text-sm text-muted-foreground">
                          380 points
                        </p>
                      </div>
                    </div>
                    <Award className="h-5 w-5 text-orange-600" />
                  </div>
                  <div className="flex items-center justify-between border-b pb-2 bg-muted/50 p-2 rounded">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">4.</span>
                      <div>
                        <p className="font-medium">Your Team</p>
                        <p className="text-sm text-muted-foreground">
                          320 points
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="matches">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Upcoming Matches</CardTitle>
                <CardDescription>
                  Next matches that will award points
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {MOCK_MATCHES.map((match, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between border p-4 rounded-lg"
                    >
                      <div>
                        <p className="font-medium">
                          {IPL_TEAMS[match.team1]} vs {IPL_TEAMS[match.team2]}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {match.date} - {match.time}
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedMatch(match)}
                      >
                        View Details
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Gully Settings</CardTitle>
                <CardDescription>Manage your gully settings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Invite Members</h3>
                      <p className="text-sm text-muted-foreground">
                        Share link with friends
                      </p>
                    </div>
                    <Button variant="outline" onClick={handleCopyInviteLink}>
                      Copy Link
                    </Button>
                  </div>
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Edit Gully</h3>
                      <p className="text-sm text-muted-foreground">
                        Change gully name or settings
                      </p>
                    </div>
                    <Button variant="outline" onClick={handleEditGullyOpen}>
                      Edit
                    </Button>
                  </div>
                  {gully.status === "draft" && (
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-medium">Start Auction</h3>
                        <p className="text-sm text-muted-foreground">
                          Begin the player auction process
                        </p>
                      </div>
                      <Button>Start Auction</Button>
                    </div>
                  )}
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium text-destructive">
                        Delete Gully
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Permanently delete this gully
                      </p>
                    </div>
                    <Button variant="destructive" onClick={handleDeleteGully}>
                      Delete
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Dialog open={isViewTeamOpen} onOpenChange={setIsViewTeamOpen}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>
                {isEditMode ? "Edit Team" : "View Team"} -{" "}
                {selectedParticipant?.team_name}
              </DialogTitle>
            </DialogHeader>
            <div className="mt-4">
              {selectedParticipant && (
                <div className="space-y-4">
                  {isEditMode ? (
                    <TeamEditor
                      players={IPL_PLAYERS}
                      selectedPlayers={selectedParticipant.players || []}
                      onSave={(players) => {
                        handleSaveTeam(players);
                      }}
                      onCancel={() => setIsViewTeamOpen(false)}
                    />
                  ) : (
                    <div className="space-y-4">
                      {selectedParticipant.players &&
                      selectedParticipant.players.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {selectedParticipant.players.map((player) => (
                            <Card key={player.id} className="p-4">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-medium">{player.name}</p>
                                  <div className="flex items-center gap-2 mt-1">
                                    <Badge variant="outline">
                                      {player.team}
                                    </Badge>
                                    <Badge>{player.role}</Badge>
                                  </div>
                                  <div className="flex items-center gap-2 mt-1">
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
                              </div>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">
                            No players in team yet
                          </p>
                          {currentUser?.id === selectedParticipant.user_id && (
                            <Button
                              variant="outline"
                              className="mt-4"
                              onClick={() => setIsEditMode(true)}
                            >
                              Add Players
                            </Button>
                          )}
                        </div>
                      )}
                      {currentUser?.id === selectedParticipant.user_id &&
                        selectedParticipant.players?.length > 0 && (
                          <div className="flex justify-end">
                            <Button
                              variant="outline"
                              onClick={() => setIsEditMode(true)}
                            >
                              Edit Team
                            </Button>
                          </div>
                        )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>

        <Dialog open={isEditGullyOpen} onOpenChange={setIsEditGullyOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Edit Gully Settings</DialogTitle>
              <DialogDescription>
                Manage your gully's settings and configurations
              </DialogDescription>
            </DialogHeader>
            {gully && (
              <GullyEditor
                gully={gully}
                onSave={async (data) => {
                  try {
                    const updatedGully = await gullyApi.updateGully(
                      gully.id,
                      data
                    );
                    setGully(updatedGully);
                    setActiveGully(updatedGully);
                    const updatedGullies = userGullies.map((g) =>
                      g.id === updatedGully.id ? updatedGully : g
                    );
                    setUserGullies(updatedGullies);
                    setIsEditGullyOpen(false);
                    toast({
                      title: "Success",
                      description: "Gully settings updated successfully",
                    });
                  } catch (error) {
                    console.error("Error updating gully:", error);
                    toast({
                      title: "Error",
                      description: "Failed to update gully settings",
                      variant: "destructive",
                    });
                  }
                }}
                onDelete={handleDeleteGully}
                onClose={() => setIsEditGullyOpen(false)}
              />
            )}
          </DialogContent>
        </Dialog>

        {selectedMatch && (
          <MatchDetailsDialog
            isOpen={!!selectedMatch}
            onClose={() => setSelectedMatch(null)}
            match={selectedMatch}
          />
        )}
      </div>
    </div>
  );
}
