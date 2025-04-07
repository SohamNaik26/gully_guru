"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useAppStore } from "@/lib/store";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { toast } from "sonner";

const profileFormSchema = z.object({
  username: z.string().min(3).max(30),
  full_name: z.string().min(2).max(100),
  telegram_id: z.string().optional(),
});

type ProfileFormValues = z.infer<typeof profileFormSchema>;

export default function ProfilePage() {
  const { data: session } = useSession();
  const { currentUser } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      username: currentUser?.username || "",
      full_name: currentUser?.full_name || session?.user?.name || "",
      telegram_id: currentUser?.telegram_id?.toString() || "",
    },
  });

  useEffect(() => {
    if (currentUser) {
      form.reset({
        username: currentUser.username,
        full_name: currentUser.full_name,
        telegram_id: currentUser.telegram_id?.toString(),
      });
    }
  }, [currentUser, form]);

  async function onSubmit(data: ProfileFormValues) {
    setIsLoading(true);
    try {
      // In a real app, make an API call to update the profile
      // await userApi.updateProfile(data);
      toast.success("Profile updated successfully");
    } catch (error) {
      console.error("Error updating profile:", error);
      toast.error("Failed to update profile");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Profile Settings
          </h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences
          </p>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>
                Update your profile details and preferences
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-4"
                >
                  <FormField
                    control={form.control}
                    name="username"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Username</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormDescription>
                          This is your public display name
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="full_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Full Name</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormDescription>
                          Your full name as it appears on your account
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="telegram_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Telegram ID</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormDescription>
                          Your Telegram ID for notifications (optional)
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? "Saving..." : "Save Changes"}
                  </Button>
                </form>
              </Form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Account Statistics</CardTitle>
              <CardDescription>
                Overview of your account activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex flex-col items-center justify-center border rounded-lg p-4">
                  <span className="text-3xl font-bold">
                    {currentUser?.gullies?.length || 0}
                  </span>
                  <span className="text-sm text-muted-foreground">
                    Gullies Joined
                  </span>
                </div>
                <div className="flex flex-col items-center justify-center border rounded-lg p-4">
                  <span className="text-3xl font-bold">15</span>
                  <span className="text-sm text-muted-foreground">
                    Players Owned
                  </span>
                </div>
                <div className="flex flex-col items-center justify-center border rounded-lg p-4">
                  <span className="text-3xl font-bold">550</span>
                  <span className="text-sm text-muted-foreground">
                    Total Points
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
