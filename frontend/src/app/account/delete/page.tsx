"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ChevronLeft, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { useAppStore } from "@/lib/store";

const DeleteAccountPage = () => {
  const router = useRouter();
  const { currentUser, logout } = useAppStore();
  const [confirmation, setConfirmation] = useState("");
  const [loading, setLoading] = useState(false);

  const handleDeleteAccount = async () => {
    if (confirmation !== "DELETE") {
      toast.error("Please type DELETE to confirm account deletion");
      return;
    }

    try {
      setLoading(true);
      // Call API to delete account
      const response = await fetch("/api/users/delete", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to delete account");
      }

      // Log out the user
      await logout();

      toast.success("Your account has been successfully deleted");
      router.push("/auth/login");
    } catch (error) {
      console.error("Error deleting account:", error);
      toast.error("Failed to delete account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container max-w-2xl mx-auto py-8">
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-4">
          <Link href="/account">
            <Button variant="ghost" size="icon">
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">Delete Account</h1>
        </div>

        <Card className="p-6">
          <div className="space-y-6">
            <div className="flex items-start gap-4 p-4 bg-destructive/10 rounded-lg text-destructive">
              <AlertTriangle className="h-5 w-5 mt-0.5" />
              <div className="space-y-1">
                <h3 className="font-medium">
                  Warning: This action cannot be undone
                </h3>
                <p className="text-sm text-muted-foreground">
                  Deleting your account will:
                </p>
                <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                  <li>Remove all your personal information</li>
                  <li>Delete all your gullies and teams</li>
                  <li>Cancel any ongoing contests or tournaments</li>
                  <li>Remove you from all participant lists</li>
                  <li>Delete your transaction history</li>
                </ul>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="confirmation">
                  Type <span className="font-mono font-bold">DELETE</span> to
                  confirm
                </Label>
                <Input
                  id="confirmation"
                  value={confirmation}
                  onChange={(e) => setConfirmation(e.target.value)}
                  placeholder="Type DELETE to confirm"
                  className="font-mono"
                />
              </div>

              <Button
                variant="destructive"
                onClick={handleDeleteAccount}
                disabled={confirmation !== "DELETE" || loading}
                className="w-full"
              >
                {loading ? "Deleting Account..." : "Permanently Delete Account"}
              </Button>
            </div>

            <div className="text-center">
              <Link href="/account">
                <Button variant="ghost" className="text-sm">
                  Cancel and go back
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DeleteAccountPage;
