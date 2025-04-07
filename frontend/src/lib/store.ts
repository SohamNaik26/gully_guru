import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: number;
  telegram_id: number;
  username: string;
  full_name: string;
  email: string | null;
}

interface Gully {
  id: number;
  name: string;
  status: "draft" | "auction" | "transfers" | "completed";
  telegram_group_id?: number;
}

interface Participant {
  id: number;
  user_id: number;
  gully_id: number;
  team_name: string;
  budget: number;
  points: number;
  role: "member" | "admin";
}

interface Player {
  id: number;
  name: string;
  team: string;
  player_type: "BAT" | "BOWL" | "AR" | "WK";
  base_price: number;
  sold_price?: number;
}

interface AppState {
  currentUser: User | null;
  setCurrentUser: (user: User | null) => void;

  activeGully: Gully | null;
  setActiveGully: (gully: Gully | null) => void;

  userGullies: Gully[];
  setUserGullies: (gullies: Gully[]) => void;

  userParticipations: Participant[];
  setUserParticipations: (participations: Participant[]) => void;

  selectedPlayers: Player[];
  setSelectedPlayers: (players: Player[]) => void;
  addSelectedPlayer: (player: Player) => void;
  removeSelectedPlayer: (playerId: number) => void;

  searchQuery: string;
  setSearchQuery: (query: string) => void;

  currentView: "squad" | "auction" | "leaderboard" | "transfer";
  setCurrentView: (
    view: "squad" | "auction" | "leaderboard" | "transfer"
  ) => void;

  clearStore: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentUser: null,
      setCurrentUser: (user) => set({ currentUser: user }),

      activeGully: null,
      setActiveGully: (gully) => set({ activeGully: gully }),

      userGullies: [],
      setUserGullies: (gullies) => set({ userGullies: gullies }),

      userParticipations: [],
      setUserParticipations: (participations) =>
        set({ userParticipations: participations }),

      selectedPlayers: [],
      setSelectedPlayers: (players) => set({ selectedPlayers: players }),
      addSelectedPlayer: (player) =>
        set((state) => ({
          selectedPlayers: [...state.selectedPlayers, player],
        })),
      removeSelectedPlayer: (playerId) =>
        set((state) => ({
          selectedPlayers: state.selectedPlayers.filter(
            (p) => p.id !== playerId
          ),
        })),

      searchQuery: "",
      setSearchQuery: (query) => set({ searchQuery: query }),

      currentView: "squad",
      setCurrentView: (view) => set({ currentView: view }),

      clearStore: () =>
        set({
          currentUser: null,
          activeGully: null,
          userGullies: [],
          userParticipations: [],
          selectedPlayers: [],
          searchQuery: "",
          currentView: "squad",
        }),
    }),
    {
      name: "gullyguru-storage",
      partialize: (state) => ({
        currentUser: state.currentUser,
        activeGully: state.activeGully,
        userGullies: state.userGullies,
        userParticipations: state.userParticipations,
      }),
    }
  )
);
