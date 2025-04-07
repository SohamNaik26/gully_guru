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
import { Badge } from "@/components/ui/badge";
import { Trophy, Star, Target, Users, TrendingUp, Award } from "lucide-react";

interface Achievement {
  id: number;
  title: string;
  description: string;
  icon: JSX.Element;
  progress: number;
  total: number;
  category: "general" | "team" | "tournament" | "social";
  unlocked: boolean;
  unlockedAt?: string;
}

export default function AchievementsPage() {
  const { activeGully, currentUser } = useAppStore();
  const [achievements, setAchievements] = useState<Achievement[]>([]);

  useEffect(() => {
    // TODO: Fetch actual achievements data from API
    // For now, using mock data
    const mockAchievements: Achievement[] = [
      {
        id: 1,
        title: "Fantasy Master",
        description: "Win 5 fantasy tournaments",
        icon: <Trophy className="h-6 w-6" />,
        progress: 3,
        total: 5,
        category: "tournament",
        unlocked: false,
      },
      {
        id: 2,
        title: "Dream Team",
        description: "Create a team with all star players",
        icon: <Star className="h-6 w-6" />,
        progress: 1,
        total: 1,
        category: "team",
        unlocked: true,
        unlockedAt: "2024-03-15",
      },
      {
        id: 3,
        title: "Social Butterfly",
        description: "Join 3 different gullies",
        icon: <Users className="h-6 w-6" />,
        progress: 2,
        total: 3,
        category: "social",
        unlocked: false,
      },
      {
        id: 4,
        title: "Point Collector",
        description: "Earn 1000 total points",
        icon: <TrendingUp className="h-6 w-6" />,
        progress: 750,
        total: 1000,
        category: "general",
        unlocked: false,
      },
      {
        id: 5,
        title: "Sharp Shooter",
        description: "Pick the top scorer in 3 matches",
        icon: <Target className="h-6 w-6" />,
        progress: 3,
        total: 3,
        category: "team",
        unlocked: true,
        unlockedAt: "2024-03-20",
      },
    ];
    setAchievements(mockAchievements);
  }, []);

  const categories = {
    general: "General",
    team: "Team Management",
    tournament: "Tournament",
    social: "Social",
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Achievements</h1>
          <p className="text-muted-foreground">
            Track your progress and unlock rewards
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(categories).map(([category, title]) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="text-xl">{title}</CardTitle>
                <CardDescription>{title} related achievements</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {achievements
                    .filter((achievement) => achievement.category === category)
                    .map((achievement) => (
                      <div
                        key={achievement.id}
                        className={`relative flex items-start gap-4 p-4 rounded-lg border ${
                          achievement.unlocked
                            ? "bg-green-50 dark:bg-green-950/20"
                            : "bg-background"
                        }`}
                      >
                        <div
                          className={`flex items-center justify-center w-12 h-12 rounded-full ${
                            achievement.unlocked
                              ? "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {achievement.icon}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium">{achievement.title}</h3>
                            {achievement.unlocked && (
                              <Badge variant="success">Unlocked</Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            {achievement.description}
                          </p>
                          {!achievement.unlocked && (
                            <div className="mt-2">
                              <div className="h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-primary"
                                  style={{
                                    width: `${
                                      (achievement.progress /
                                        achievement.total) *
                                      100
                                    }%`,
                                  }}
                                />
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">
                                Progress: {achievement.progress}/
                                {achievement.total}
                              </p>
                            </div>
                          )}
                          {achievement.unlocked && achievement.unlockedAt && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Unlocked on{" "}
                              {new Date(
                                achievement.unlockedAt
                              ).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        {achievement.unlocked && (
                          <Award className="absolute top-4 right-4 h-5 w-5 text-green-500" />
                        )}
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
