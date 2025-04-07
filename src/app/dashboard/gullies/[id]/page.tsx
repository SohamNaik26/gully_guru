"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAppStore } from "@/lib/store";
import { gullyApi } from "@/lib/api-client";
import { GullyEditor } from "./components/GullyEditor";

export default function GullyDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { currentUser, userGullies, setUserGullies } = useAppStore();
  const [gully, setGully] = useState(null);
  const [activeGully, setActiveGully] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGully = async () => {
      try {
        setLoading(true);
        const gullyData = await gullyApi.getGully(params.id);
        setGully(gullyData);
        setActiveGully(gullyData);
      } catch (error) {
        console.error("Error fetching gully:", error);
        toast.error("Failed to load gully details");
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchGully();
    }
  }, [params.id]);

  const onSave = async (updatedGully) => {
    try {
      // Update local state
      setGully(updatedGully);
      setActiveGully(updatedGully);

      // Update gullies in global store
      const currentGullies = userGullies || [];
      const updatedGullies = currentGullies.map((g) =>
        g.id === updatedGully.id ? updatedGully : g
      );
      setUserGullies(updatedGullies);

      toast.success("Gully updated successfully");
    } catch (error) {
      console.error("Error updating gully:", error);
      toast.error("Failed to update gully");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!gully) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Gully not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <GullyEditor gully={gully} onSave={onSave} />
    </div>
  );
}
