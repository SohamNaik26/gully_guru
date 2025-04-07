import axios from "axios";
import { getSession } from "next-auth/react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const session = await getSession();
      if (session?.user?.id) {
        config.headers.Authorization = `Bearer ${session.user.id}`;
      }
      return config;
    } catch (error) {
      return config;
    }
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Create a helper function for handling API requests in development mode
const developmentApiHandler = async <T>(
  apiCall: () => Promise<T>,
  mockData: T,
  errorMessage: string
): Promise<T> => {
  // Check if we should always use mock data in development
  if (
    process.env.NODE_ENV === "development" &&
    process.env.NEXT_PUBLIC_USE_MOCK_DATA === "true"
  ) {
    console.log("Using mock data due to NEXT_PUBLIC_USE_MOCK_DATA=true");
    return mockData;
  }

  if (process.env.NODE_ENV === "development") {
    try {
      return await apiCall();
    } catch (error) {
      // Check if the error is a CORS error or network error
      if (
        error instanceof Error &&
        (error.message.includes("NetworkError") ||
          error.message.includes("Network Error") ||
          error.message.includes("Failed to fetch") ||
          error.message.includes("CORS") ||
          // Axios specific error for CORS
          (axios.isAxiosError(error) &&
            (error.code === "ERR_NETWORK" || error.code === "CORS_ERROR")))
      ) {
        console.warn(`${errorMessage} (CORS/Network issue) Using mock data.`);
        return mockData;
      }

      console.warn(`${errorMessage} Using mock data.`);
      return mockData;
    }
  }

  try {
    return await apiCall();
  } catch (error) {
    console.error(errorMessage, error);
    throw error;
  }
};

// API endpoints grouped by domain
export const userApi = {
  getCurrentUser: async () => {
    try {
      const session = await getSession();
      if (!session?.user?.email) return null;

      // Always use mock data in development if the flag is set
      if (
        process.env.NODE_ENV === "development" &&
        process.env.NEXT_PUBLIC_USE_MOCK_DATA === "true"
      ) {
        console.log(
          "Using mock user data due to NEXT_PUBLIC_USE_MOCK_DATA=true"
        );
        return {
          id: parseInt(session.user.id || "1"),
          email: session.user.email,
          username:
            session.user.name?.replace(/\s+/g, "_").toLowerCase() || "user",
          full_name: session.user.name || "Test User",
          telegram_id: 123456789,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      }

      // For development, return mock user if backend is not available
      if (process.env.NODE_ENV === "development") {
        try {
          const response = await api.get(
            `/api/users?email=${encodeURIComponent(session.user.email)}`
          );
          return response.data.length > 0 ? response.data[0] : null;
        } catch (error) {
          // Check if the error is a CORS error or network error
          if (
            error instanceof Error &&
            (error.message.includes("NetworkError") ||
              error.message.includes("Network Error") ||
              error.message.includes("Failed to fetch") ||
              error.message.includes("CORS") ||
              // Axios specific error for CORS
              (axios.isAxiosError(error) &&
                (error.code === "ERR_NETWORK" || error.code === "CORS_ERROR")))
          ) {
            console.warn(
              "Backend connection failed (CORS/Network issue), using mock user data for development"
            );
          } else {
            console.warn(
              "Backend connection failed, using mock user data for development"
            );
          }

          // Return mock user for development
          return {
            id: parseInt(session.user.id || "1"),
            email: session.user.email,
            username:
              session.user.name?.replace(/\s+/g, "_").toLowerCase() || "user",
            full_name: session.user.name || "Test User",
            telegram_id: 123456789,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
        }
      }

      // Production flow - will fail if backend is not available
      const response = await api.get(
        `/api/users?email=${encodeURIComponent(session.user.email)}`
      );
      return response.data.length > 0 ? response.data[0] : null;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    }
  },

  updateProfile: async (
    userId: number,
    data: { username?: string; full_name?: string }
  ) => {
    const response = await api.put(`/api/users/${userId}`, data);
    return response.data;
  },
};

export const gullyApi = {
  getGullies: async () => {
    return developmentApiHandler(
      () => api.get("/api/gullies").then((response) => response.data),
      [],
      "Failed to fetch gullies."
    );
  },

  getGully: async (gullyId: number) => {
    return developmentApiHandler(
      () =>
        api.get(`/api/gullies/${gullyId}`).then((response) => response.data),
      {
        id: gullyId,
        name: "IPL Fantasy League 2024",
        status: "active",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        admin_id: 1,
        participants_count: 12,
        your_rank: 4,
        points: 320,
        next_match_in_days: 2,
      },
      `Failed to fetch gully with ID ${gullyId}.`
    );
  },

  createGully: async (data: { name: string; telegram_group_id?: number }) => {
    return developmentApiHandler(
      () => api.post("/api/gullies", data).then((response) => response.data),
      {
        id: Math.floor(Math.random() * 1000) + 100,
        name: data.name,
        telegram_group_id: data.telegram_group_id,
        status: "draft",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        admin_id: 1,
      },
      "Failed to create gully."
    );
  },

  getUserGullies: async (userId: number) => {
    return developmentApiHandler(
      () =>
        api
          .get(`/api/gullies/user/${userId}`)
          .then((response) => response.data),
      [
        {
          id: 1,
          name: "IPL Fantasy 2024",
          status: "active",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          admin_id: userId,
        },
        {
          id: 2,
          name: "Friends Cricket League",
          status: "draft",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          admin_id: userId,
        },
      ],
      `Failed to fetch gullies for user ID ${userId}.`
    );
  },

  updateGully: async (
    gullyId: number,
    data: { name: string; telegram_group_id?: string }
  ) => {
    return developmentApiHandler(
      () =>
        api
          .put(`/api/gullies/${gullyId}`, data)
          .then((response) => response.data),
      {
        id: gullyId,
        name: data.name,
        telegram_group_id: data.telegram_group_id,
        status: "active",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        admin_id: 1,
      },
      `Failed to update gully with ID ${gullyId}.`
    );
  },
};

export const participantApi = {
  joinGully: async (data: {
    gully_id: number;
    user_id: number;
    team_name: string;
  }) => {
    return developmentApiHandler(
      () =>
        api.post("/api/participants", data).then((response) => response.data),
      {
        id: Math.floor(Math.random() * 1000) + 100,
        gully_id: data.gully_id,
        user_id: data.user_id,
        team_name: data.team_name,
        role: "member",
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      "Failed to join gully."
    );
  },

  getParticipants: async (gullyId: number) => {
    return developmentApiHandler(
      () =>
        api
          .get(`/api/participants/gully/${gullyId}`)
          .then((response) => response.data),
      [
        {
          id: 1,
          user_id: 1,
          team_name: "Super Kings",
          role: "admin",
          players: [
            {
              id: 1,
              name: "MS Dhoni",
              team: "CSK",
              role: "Wicket-keeper",
              basePrice: 1600,
              stats: { average: 38.5 },
            },
            {
              id: 2,
              name: "Ruturaj Gaikwad",
              team: "CSK",
              role: "Batsman",
              basePrice: 1200,
              stats: { average: 42.5 },
            },
            {
              id: 3,
              name: "Ravindra Jadeja",
              team: "CSK",
              role: "All-rounder",
              basePrice: 1400,
              stats: { average: 35.5, economy: 7.2 },
            },
          ],
        },
        {
          id: 2,
          user_id: 2,
          team_name: "Mumbai Indians",
          role: "member",
          players: [
            {
              id: 4,
              name: "Rohit Sharma",
              team: "MI",
              role: "Batsman",
              basePrice: 1500,
              stats: { average: 45.5 },
            },
            {
              id: 5,
              name: "Hardik Pandya",
              team: "MI",
              role: "All-rounder",
              basePrice: 1400,
              stats: { average: 33.5, economy: 8.1 },
            },
          ],
        },
        {
          id: 3,
          user_id: 3,
          team_name: "Royal Challengers",
          role: "member",
          players: [
            {
              id: 6,
              name: "Virat Kohli",
              team: "RCB",
              role: "Batsman",
              basePrice: 1600,
              stats: { average: 51.5 },
            },
            {
              id: 7,
              name: "Glenn Maxwell",
              team: "RCB",
              role: "All-rounder",
              basePrice: 1300,
              stats: { average: 38.5, economy: 7.8 },
            },
          ],
        },
      ],
      `Failed to fetch participants for gully ${gullyId}.`
    );
  },

  updateTeam: async (participantId: number, players: any[]) => {
    return developmentApiHandler(
      () =>
        api
          .put(`/api/participants/${participantId}/team`, { players })
          .then((response) => response.data),
      {
        id: participantId,
        players: players,
        message: "Team updated successfully",
      },
      `Failed to update team for participant ${participantId}.`
    );
  },
};

export const squadApi = {
  getSquad: async (participantId: number) => {
    return developmentApiHandler(
      () =>
        api
          .get(`/api/participants/${participantId}/players`)
          .then((response) => response.data),
      [
        {
          id: 1,
          name: "MS Dhoni",
          team: "CSK",
          role: "Wicket-keeper",
          basePrice: 1600,
          stats: { average: 38.5 },
        },
        {
          id: 2,
          name: "Ruturaj Gaikwad",
          team: "CSK",
          role: "Batsman",
          basePrice: 1200,
          stats: { average: 42.5 },
        },
        {
          id: 3,
          name: "Ravindra Jadeja",
          team: "CSK",
          role: "All-rounder",
          basePrice: 1400,
          stats: { average: 35.5, economy: 7.2 },
        },
      ],
      `Failed to fetch squad for participant ID ${participantId}.`
    );
  },

  addPlayerToSquad: async (participantId: number, playerId: number) => {
    return developmentApiHandler(
      () =>
        api
          .post(`/api/participants/${participantId}/players`, {
            player_id: playerId,
          })
          .then((response) => response.data),
      {
        id: Math.floor(Math.random() * 1000) + 200,
        player_id: playerId,
        gully_participant_id: participantId,
      },
      `Failed to add player ${playerId} to squad.`
    );
  },
};

export const playerApi = {
  getPlayers: async () => {
    return developmentApiHandler(
      () => api.get("/api/players").then((response) => response.data),
      [
        {
          id: 1,
          name: "MS Dhoni",
          team: "CSK",
          role: "Wicket-keeper",
          basePrice: 1600,
          stats: { average: 38.5 },
        },
        {
          id: 2,
          name: "Ruturaj Gaikwad",
          team: "CSK",
          role: "Batsman",
          basePrice: 1200,
          stats: { average: 42.5 },
        },
        {
          id: 3,
          name: "Ravindra Jadeja",
          team: "CSK",
          role: "All-rounder",
          basePrice: 1400,
          stats: { average: 35.5, economy: 7.2 },
        },
        {
          id: 4,
          name: "Rohit Sharma",
          team: "MI",
          role: "Batsman",
          basePrice: 1500,
          stats: { average: 45.5 },
        },
        {
          id: 5,
          name: "Hardik Pandya",
          team: "MI",
          role: "All-rounder",
          basePrice: 1400,
          stats: { average: 33.5, economy: 8.1 },
        },
        {
          id: 6,
          name: "Virat Kohli",
          team: "RCB",
          role: "Batsman",
          basePrice: 1600,
          stats: { average: 51.5 },
        },
        {
          id: 7,
          name: "Glenn Maxwell",
          team: "RCB",
          role: "All-rounder",
          basePrice: 1300,
          stats: { average: 38.5, economy: 7.8 },
        },
      ],
      "Failed to fetch players."
    );
  },

  getPlayer: async (playerId: number) => {
    return developmentApiHandler(
      () =>
        api.get(`/api/players/${playerId}`).then((response) => response.data),
      {
        id: playerId,
        name: "Sample Player",
        team: "Sample Team",
        role: "All-rounder",
        price: 1000,
        stats: {
          matches: 50,
          runs: 1500,
          wickets: 30,
        },
      },
      `Failed to fetch player with ID ${playerId}.`
    );
  },
};

export const auctionApi = {
  getAuctionQueue: async (gullyId: number) => {
    return developmentApiHandler(
      () =>
        api
          .get(`/api/auction?gully_id=${gullyId}`)
          .then((response) => response.data),
      [
        {
          id: 301,
          gully_id: gullyId,
          player_id: 1,
          status: "pending",
          current_bid: 0,
          highest_bidder_id: null,
        },
        {
          id: 302,
          gully_id: gullyId,
          player_id: 2,
          status: "pending",
          current_bid: 0,
          highest_bidder_id: null,
        },
      ],
      `Failed to fetch auction queue for gully ID ${gullyId}.`
    );
  },

  placeBid: async (data: {
    auction_queue_id: number;
    gully_participant_id: number;
    bid_amount: number;
  }) => {
    return developmentApiHandler(
      () => api.post("/api/bids", data).then((response) => response.data),
      {
        id: Math.floor(Math.random() * 1000) + 400,
        auction_queue_id: data.auction_queue_id,
        gully_participant_id: data.gully_participant_id,
        bid_amount: data.bid_amount,
        created_at: new Date().toISOString(),
      },
      "Failed to place bid."
    );
  },
};

export default api;
