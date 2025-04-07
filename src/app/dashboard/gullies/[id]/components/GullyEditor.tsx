import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { gullyApi } from "@/lib/api-client";
import { Trophy, Users, Edit, Cricket } from "lucide-react";

interface GullyEditorProps {
  gully: {
    id: number;
    name: string;
    description?: string;
  };
  onSave: (updatedGully: any) => void;
}

export function GullyEditor({ gully, onSave }: GullyEditorProps) {
  const [name, setName] = useState(gully.name);
  const [description, setDescription] = useState(gully.description || "");
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    try {
      setLoading(true);

      if (!name.trim()) {
        toast.error("Gully name is required");
        return;
      }

      const updatedGully = await gullyApi.updateGully(gully.id, {
        name: name.trim(),
        description: description.trim(),
      });

      onSave(updatedGully);
      toast.success("Gully updated successfully");
    } catch (error) {
      console.error("Error updating gully:", error);
      toast.error("Failed to update gully");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between bg-card/50 p-6 rounded-lg glass-effect">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-full bg-primary/20 hover:bg-primary/30 transition-colors">
            <Trophy className="h-6 w-6 text-primary animate-bounce-slow" />
          </div>
          <div>
            <h2 className="text-2xl font-bold gradient-border">
              Gully Settings
            </h2>
            <p className="text-muted-foreground">
              Customize your cricket gully
            </p>
          </div>
        </div>
        <Button
          className="button-gradient hover:scale-105 transition-transform"
          onClick={handleSave}
          disabled={loading}
        >
          {loading ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
              <span>Saving...</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Edit className="h-4 w-4" />
              <span>Save Changes</span>
            </div>
          )}
        </Button>
      </div>

      <Card className="card-shine card-gradient p-8 relative overflow-hidden">
        {/* Cricket ball decoration */}
        <div
          className="absolute -right-8 -top-8 w-24 h-24 rounded-full bg-secondary/10 animate-spin-slow"
          style={{ animationDuration: "20s" }}
        >
          <div className="absolute inset-0 rounded-full bg-[linear-gradient(45deg,transparent_40%,white_45%,white_55%,transparent_60%)] rotate-45" />
        </div>

        <div className="space-y-8 relative">
          <div className="space-y-4">
            <Label
              htmlFor="name"
              className="text-lg font-medium flex items-center gap-2"
            >
              <Cricket className="h-4 w-4 text-primary" />
              Gully Name
            </Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your gully name"
              className="text-lg py-6 bg-background/50 hover:bg-background/70 transition-colors border-primary/20 focus:border-primary focus:ring-primary/20"
            />
          </div>
          <div className="space-y-4">
            <Label
              htmlFor="description"
              className="text-lg font-medium flex items-center gap-2"
            >
              <Cricket className="h-4 w-4 text-primary" />
              Description
            </Label>
            <Input
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Tell us about your gully"
              className="text-base py-6 bg-background/50 hover:bg-background/70 transition-colors border-primary/20 focus:border-primary focus:ring-primary/20"
            />
          </div>

          <div className="pt-6 border-t border-primary/10">
            <div className="flex items-center gap-3 text-muted-foreground bg-primary/5 p-4 rounded-lg hover:bg-primary/10 transition-colors">
              <Users className="h-5 w-5 text-primary" />
              <span className="text-sm">
                Changes will be visible to all gully members
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
