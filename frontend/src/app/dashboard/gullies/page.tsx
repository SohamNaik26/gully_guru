"use client";

import { useEffect } from "react";
import { useAppStore } from "@/lib/store";
import { gullyApi } from "@/lib/api-client";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Plus, Users, TrendingUp, Award } from "lucide-react";
import { toast } from "sonner";

export default function GulliesPage() {
  const { userGullies, setUserGullies } = useAppStore();

  useEffect(() => {
    const fetchGullies = async () => {
      try {
        const gullies = await gullyApi.getUserGullies();
        setUserGullies(gullies);
      } catch (error) {
        console.error("Error fetching gullies:", error);
        toast.error("Failed to load gullies");
      }
    };

    fetchGullies();
  }, [setUserGullies]);

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">My Gullies</h1>
            <p className="text-muted-foreground">
              Manage your fantasy cricket leagues
            </p>
          </div>
          <Button asChild>
            <Link href="/dashboard/gullies/create">
              <Plus className="mr-2 h-4 w-4" />
              Create Gully
            </Link>
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {userGullies && userGullies.length > 0 ? (
            userGullies.map((gully) => (
              <Card key={gully.id}>
                <CardHeader>
                  <CardTitle>{gully.name}</CardTitle>
                  <CardDescription className="capitalize">
                    Status: {gully.status}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-2 text-center text-sm mb-4">
                    <div className="flex flex-col items-center p-2 border rounded">
                      <Users className="h-4 w-4 mb-1" />
                      <span className="text-muted-foreground">
                        Participants
                      </span>
                      <span className="font-bold">12</span>
                    </div>
                    <div className="flex flex-col items-center p-2 border rounded">
                      <TrendingUp className="h-4 w-4 mb-1" />
                      <span className="text-muted-foreground">Your Rank</span>
                      <span className="font-bold">4th</span>
                    </div>
                    <div className="flex flex-col items-center p-2 border rounded">
                      <Award className="h-4 w-4 mb-1" />
                      <span className="text-muted-foreground">Points</span>
                      <span className="font-bold">320</span>
                    </div>
                  </div>
                  <Button asChild className="w-full">
                    <Link href={`/dashboard/gullies/${gully.id}`}>
                      View Details
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card className="col-span-2">
              <CardHeader>
                <CardTitle>No Gullies Yet</CardTitle>
                <CardDescription>
                  Create a new Gully or join an existing one to get started
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild>
                  <Link href="/dashboard/gullies/create">
                    <Plus className="mr-2 h-4 w-4" />
                    Create Gully
                  </Link>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
