import { Bell, Wallet } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/mode-toggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <Logo href="/dashboard" className="mr-8" />

        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Wallet className="h-4 w-4" />
              <span>₹51</span>
            </Button>
            <ModeToggle />
          </div>
        </div>
      </div>
    </header>
  );
}
