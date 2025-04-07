"use client";

import { useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { useToast } from "@/components/ui/use-toast";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  HelpCircle,
  AlertCircle,
  CheckCircle2,
  Loader2,
  ExternalLink,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";

interface Settings {
  emailNotifications: boolean;
  telegramNotifications: boolean;
  telegramChatId: string;
  theme: string;
  publicProfile: boolean;
  showStats: boolean;
  language: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingTelegram, setTestingTelegram] = useState(false);
  const [validatingId, setValidatingId] = useState(false);
  const [isValidId, setIsValidId] = useState<boolean | null>(null);
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    if (settings?.theme) {
      setTheme(settings.theme);
    }
  }, [settings?.theme, setTheme]);

  const fetchSettings = async () => {
    try {
      const response = await fetch("/api/users/settings");
      if (!response.ok) throw new Error("Failed to fetch settings");
      const data = await response.json();

      // Set default Telegram chat ID if not present
      const settings = {
        ...data.settings,
        telegramChatId:
          data.settings.telegramChatId ||
          process.env.DEFAULT_TELEGRAM_CHAT_ID ||
          "",
      };

      setSettings(settings);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load settings. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      const response = await fetch("/api/users/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });

      if (!response.ok) throw new Error("Failed to save settings");

      toast({
        title: "Success",
        description: "Settings saved successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save settings. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key: keyof Settings, value: boolean | string) => {
    if (!settings) return;
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    // If theme is changed, update it immediately
    if (key === "theme") {
      setTheme(value as string);
    }

    // Save settings to backend
    saveSettings();
  };

  const testTelegramNotifications = async () => {
    if (!settings?.telegramChatId) {
      toast({
        title: "Error",
        description: "Please enter a Telegram chat ID first",
        variant: "destructive",
      });
      return;
    }

    setTestingTelegram(true);
    try {
      const response = await fetch("/api/telegram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "test",
          chatId: settings.telegramChatId,
        }),
      });

      if (!response.ok) throw new Error("Failed to send test message");

      const { success } = await response.json();
      if (success) {
        toast({
          title: "Success",
          description: "Test message sent successfully! Check your Telegram.",
        });
      } else {
        throw new Error("Failed to send test message");
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send test message. Please verify your chat ID.",
        variant: "destructive",
      });
    } finally {
      setTestingTelegram(false);
    }
  };

  const validateTelegramId = async (id: string) => {
    if (!id) return;
    
    setValidatingId(true);
    setIsValidId(null);
    
    try {
      const response = await fetch("/api/telegram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "validate",
          chatId: id,
        }),
      });

      if (!response.ok) throw new Error("Validation failed");

      const { isValid } = await response.json();
      setIsValidId(isValid);
      
      if (!isValid) {
        toast({
          title: "Invalid Chat ID",
          description: "Please make sure you've started a chat with the bot and entered the correct ID.",
          variant: "destructive",
        });
      }
    } catch (error) {
      setIsValidId(false);
      toast({
        title: "Validation Error",
        description: "Failed to validate Telegram chat ID. Please try again.",
        variant: "destructive",
      });
    } finally {
      setValidatingId(false);
    }
  };

  const handleTelegramIdChange = (value: string) => {
    handleChange("telegramChatId", value);
    // Reset validation state when ID changes
    setIsValidId(null);
  };

  const openTelegramBot = () => {
    window.open(`https://t.me/${process.env.TELEGRAM_BOT_TOKEN?.split(':')[0]}`, '_blank');
  };

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <div className="space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-8 w-64" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-8 w-64" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-36" />
          <Skeleton className="h-8 w-64" />
        </div>
      </div>
    );
  }

  if (!settings) return null;

  return (
    <div className="max-w-3xl mx-auto space-y-8 p-6 bg-card rounded-lg shadow-sm">
      <div className="border-b pb-6">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Manage your account preferences and application settings.
        </p>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between p-4 rounded-lg border bg-card/50 hover:bg-accent/5 transition-colors">
          <div className="space-y-1">
            <Label htmlFor="email-notifications" className="text-base">
              Email Notifications
            </Label>
            <p className="text-sm text-muted-foreground">
              Receive email updates about your gullies and matches
            </p>
          </div>
          <Switch
            id="email-notifications"
            checked={settings.emailNotifications}
            onCheckedChange={(checked) =>
              handleChange("emailNotifications", checked)
            }
            disabled={saving}
            className="data-[state=checked]:bg-primary"
          />
        </div>

        <div className="space-y-4 p-4 rounded-lg border bg-card/50">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Label htmlFor="telegram-notifications" className="text-base">
                  Telegram Notifications
                </Label>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <HelpCircle className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Get instant notifications about matches, updates, and important events via Telegram</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <p className="text-sm text-muted-foreground">
                Get instant updates via Telegram
              </p>
            </div>
            <Switch
              id="telegram-notifications"
              checked={settings.telegramNotifications}
              onCheckedChange={(checked) =>
                handleChange("telegramNotifications", checked)
              }
              disabled={saving}
              className="data-[state=checked]:bg-primary"
            />
          </div>

          {settings.telegramNotifications && (
            <div className="space-y-4 pt-4 border-t">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Important</AlertTitle>
                <AlertDescription className="mt-2 text-sm">
                  To receive notifications:
                  <ol className="list-decimal ml-4 mt-2 space-y-1">
                    <li>Click the button below to open our Telegram bot</li>
                    <li>Start a chat with the bot by clicking "Start"</li>
                    <li>Enter your chat ID below and click "Verify"</li>
                  </ol>
                </AlertDescription>
              </Alert>

              <Button
                onClick={openTelegramBot}
                variant="outline"
                className="w-full flex items-center justify-center gap-2"
              >
                Open GullyGuru Bot in Telegram
                <ExternalLink className="h-4 w-4" />
              </Button>

              <div className="space-y-2">
                <Label htmlFor="telegram-chat-id">Telegram Chat ID</Label>
                <div className="flex space-x-2">
                  <div className="relative flex-1">
                    <Input
                      id="telegram-chat-id"
                      value={settings.telegramChatId}
                      onChange={(e) => handleTelegramIdChange(e.target.value)}
                      placeholder="Enter your Telegram chat ID"
                      className={`pr-8 ${
                        isValidId === true
                          ? "border-green-500 focus-visible:ring-green-500"
                          : isValidId === false
                          ? "border-red-500 focus-visible:ring-red-500"
                          : ""
                      }`}
                    />
                    {isValidId !== null && !validatingId && (
                      <div className="absolute right-2 top-1/2 -translate-y-1/2">
                        {isValidId ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    )}
                    {validatingId && (
                      <div className="absolute right-2 top-1/2 -translate-y-1/2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => validateTelegramId(settings.telegramChatId)}
                      disabled={validatingId || !settings.telegramChatId}
                      variant="outline"
                    >
                      Verify
                    </Button>
                    <Button
                      onClick={testTelegramNotifications}
                      disabled={testingTelegram || !settings.telegramChatId || isValidId === false}
                      variant="default"
                    >
                      {testingTelegram ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Testing...
                        </>
                      ) : (
                        "Test"
                      )}
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <HelpCircle className="h-3 w-3" />
                  Your Telegram chat ID is required to receive notifications
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border bg-card/50 hover:bg-accent/5 transition-colors">
          <div className="space-y-1">
            <Label htmlFor="theme" className="text-base">
              Theme
            </Label>
            <p className="text-sm text-muted-foreground">
              Choose your preferred theme
            </p>
          </div>
          <Select
            value={settings.theme}
            onValueChange={(value) => handleChange("theme", value)}
            disabled={saving}
          >
            <SelectTrigger className="w-[180px] bg-background">
              <SelectValue placeholder="Select theme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border bg-card/50 hover:bg-accent/5 transition-colors">
          <div className="space-y-1">
            <Label htmlFor="public-profile" className="text-base">
              Public Profile
            </Label>
            <p className="text-sm text-muted-foreground">
              Make your profile visible to other users
            </p>
          </div>
          <Switch
            id="public-profile"
            checked={settings.publicProfile}
            onCheckedChange={(checked) =>
              handleChange("publicProfile", checked)
            }
            disabled={saving}
            className="data-[state=checked]:bg-primary"
          />
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border bg-card/50 hover:bg-accent/5 transition-colors">
          <div className="space-y-1">
            <Label htmlFor="show-stats" className="text-base">
              Show Statistics
            </Label>
            <p className="text-sm text-muted-foreground">
              Display your fantasy cricket statistics on your profile
            </p>
          </div>
          <Switch
            id="show-stats"
            checked={settings.showStats}
            onCheckedChange={(checked) => handleChange("showStats", checked)}
            disabled={saving}
            className="data-[state=checked]:bg-primary"
          />
        </div>
      </div>

      <div className="flex justify-end pt-6 border-t">
        <button
          onClick={saveSettings}
          disabled={saving}
          className="px-6 py-2.5 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors font-medium flex items-center justify-center min-w-[120px]"
        >
          {saving ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Saving...
            </>
          ) : (
            "Save Changes"
          )}
        </button>
      </div>
    </div>
  );
}
