"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAppStore } from "@/lib/store";
import {
  Home,
  Users,
  TrendingUp,
  ShoppingBag,
  Award,
  Settings,
  Menu,
  X,
  User,
  BarChart2,
  Shield,
  Trophy,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface SidebarProps {
  className?: string;
}

const navItems = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    name: "My Gullies",
    href: "/dashboard/gullies",
    icon: Users,
  },
  {
    name: "Matches",
    href: "/dashboard/matches",
    icon: TrendingUp,
  },
  {
    name: "Auction",
    href: "/dashboard/auction",
    icon: ShoppingBag,
  },
  {
    name: "Team",
    href: "/dashboard/team",
    icon: Shield,
  },
  {
    name: "Squad",
    href: "/dashboard/squad",
    icon: Users,
  },
  {
    name: "Stats",
    href: "/dashboard/stats",
    icon: BarChart2,
  },
  {
    name: "Leaderboard",
    href: "/dashboard/leaderboard",
    icon: Award,
  },
  {
    name: "Account",
    href: "/account",
    icon: User,
  },
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
  {
    name: "Contests",
    href: "/dashboard/contests",
    icon: Trophy,
  },
];

export default function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const activeGully = useAppStore((state) => state.activeGully);
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Mobile menu button */}
      <div className="flex lg:hidden items-center ml-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="lg:hidden"
        >
          <Menu className="h-6 w-6" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </div>

      {/* Mobile menu overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-background border-r transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:h-[calc(100vh-4rem)] ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } ${className}`}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b lg:hidden">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold">GullyGuru</span>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="lg:hidden"
          >
            <X className="h-5 w-5" />
            <span className="sr-only">Close menu</span>
          </Button>
        </div>

        <div className="py-4">
          {activeGully && (
            <div className="px-4 py-2 mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">
                Active Gully
              </h3>
              <p className="text-sm font-medium truncate">{activeGully.name}</p>
              <p className="text-xs text-muted-foreground capitalize">
                Status: {activeGully.status}
              </p>
            </div>
          )}

          <nav className="space-y-1 px-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? "bg-muted text-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? "text-foreground" : "text-muted-foreground"
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </>
  );
}
