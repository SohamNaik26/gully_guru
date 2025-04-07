"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import { toast } from "sonner";
import { gullyApi } from "@/lib/api-client";
import { useAppStore } from "@/lib/store";
import Link from "next/link";

const formSchema = z.object({
  name: z.string().min(3, {
    message: "Gully name must be at least 3 characters.",
  }),
  telegram_group_id: z.string().optional(),
});

export default function CreateGullyPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const { currentUser, setUserGullies, userGullies, setActiveGully } =
    useAppStore();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      telegram_group_id: "",
    },
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    if (!currentUser) {
      toast.error("You must be logged in to create a Gully");
      return;
    }

    try {
      setIsLoading(true);

      const createData = {
        name: values.name,
        telegram_group_id: values.telegram_group_id
          ? parseInt(values.telegram_group_id)
          : undefined,
      };

      const newGully = await gullyApi.createGully(createData);

      toast.success("Gully created successfully!");

      // Update the local store with the new gully
      if (userGullies) {
        setUserGullies([...userGullies, newGully]);
      } else {
        setUserGullies([newGully]);
      }

      // Set the new gully as active
      setActiveGully(newGully);

      // Redirect to the dashboard instead of the gully page
      // since the backend might not be available in development
      router.push("/dashboard");
    } catch (error) {
      console.error("Error creating gully:", error);
      toast.error("Failed to create Gully. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container max-w-xl mx-auto py-6">
      <Card>
        <CardHeader>
          <CardTitle>Create a New Gully</CardTitle>
          <CardDescription>
            Start a new fantasy cricket league and invite your friends
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gully Name</FormLabel>
                    <FormControl>
                      <Input placeholder="IPL Fantasy 2024" {...field} />
                    </FormControl>
                    <FormDescription>
                      Choose a unique name for your fantasy cricket league
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="telegram_group_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Telegram Group ID (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="-100123456789" {...field} />
                    </FormControl>
                    <FormDescription>
                      If you have a Telegram group, enter its ID for integrated
                      notifications
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Gully"}
              </Button>
            </form>
          </Form>
        </CardContent>
        <CardFooter className="flex justify-center border-t px-6 py-4">
          <Button variant="outline" asChild>
            <Link href="/dashboard">Cancel</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
