import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings, Users, Bell, Trash } from "lucide-react";
import { toast } from "sonner";
import { TelegramService } from "@/lib/services/telegram";

interface GullyEditorProps {
  gully: {
    id: number;
    name: string;
    telegram_group_id?: string;
    status: string;
  };
  onSave: (data: { name: string; telegram_group_id?: string }) => Promise<void>;
  onDelete: () => Promise<void>;
  onClose: () => void;
}

export function GullyEditor({
  gully,
  onSave,
  onDelete,
  onClose,
}: GullyEditorProps) {
  const [activeTab, setActiveTab] = useState("general");
  const [formData, setFormData] = useState({
    name: gully.name,
    telegram_group_id: gully.telegram_group_id || "",
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    try {
      setLoading(true);

      // Validate telegram group ID if provided
      if (formData.telegram_group_id) {
        const isValid = await TelegramService.validateChatId(
          formData.telegram_group_id
        );
        if (!isValid) {
          toast.error(
            "Invalid Telegram Group ID. Please check the ID and ensure the bot is added to the group."
          );
          return;
        }
      }

      await onSave(formData);
      toast.success("Gully settings updated successfully");
      onClose();
    } catch (error) {
      console.error("Error saving gully settings:", error);
      toast.error("Failed to update gully settings");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this gully? This action cannot be undone."
    );

    if (confirmed) {
      try {
        setLoading(true);
        await onDelete();
        toast.success("Gully deleted successfully");
      } catch (error) {
        console.error("Error deleting gully:", error);
        toast.error("Failed to delete gully");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger
            value="notifications"
            className="flex items-center gap-2"
          >
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="danger" className="flex items-center gap-2">
            <Trash className="h-4 w-4" />
            Danger Zone
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Gully Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="Enter gully name"
                />
              </div>
              <div className="space-y-2">
                <Label>Status</Label>
                <div className="text-sm text-muted-foreground capitalize">
                  {gully.status}
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="telegram_group_id">Telegram Group ID</Label>
                <Input
                  id="telegram_group_id"
                  value={formData.telegram_group_id}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      telegram_group_id: e.target.value,
                    })
                  }
                  placeholder="Enter Telegram group ID"
                />
                <p className="text-sm text-muted-foreground">
                  Add our bot to your Telegram group and enter the group ID here
                  to receive notifications.
                </p>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="danger" className="space-y-4">
          <Card className="p-6 border-destructive">
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-destructive">
                  Delete Gully
                </h3>
                <p className="text-sm text-muted-foreground">
                  Once you delete a gully, there is no going back. Please be
                  certain.
                </p>
              </div>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={loading}
              >
                Delete Gully
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSave} disabled={loading}>
          Save Changes
        </Button>
      </div>
    </div>
  );
}
