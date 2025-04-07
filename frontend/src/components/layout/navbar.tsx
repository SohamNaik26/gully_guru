"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAppStore } from "@/lib/store";
import {
  Home,
  User,
  LogOut,
  Settings,
  TrendingUp,
  Users,
  Wallet,
} from "lucide-react";
import { useEffect } from "react";

export default function Navbar() {
  const { data: session, status } = useSession();
  const pathname = usePathname();
  const activeGully = useAppStore((state) => state.activeGully);

  const isActive = (path: string) => {
    return pathname === path;
  };

  // Handle session error with fallback
  useEffect(() => {
    if (status === "loading") {
      console.log("Loading session...");
    } else if (status === "authenticated") {
      console.log("Session loaded successfully");
    } else if (status === "unauthenticated") {
      console.log("User is not authenticated");
    }
  }, [status]);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6 md:gap-10">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold">GullyGuru</span>
          </Link>

          {status === "authenticated" && (
            <nav className="hidden md:flex gap-6">
              <Link
                href="/dashboard"
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  isActive("/dashboard")
                    ? "text-blue-600 font-semibold"
                    : "text-muted-foreground"
                }`}
              >
                Dashboard
              </Link>

              {activeGully && (
                <>
                  <Link
                    href="/dashboard/squad"
                    className={`text-sm font-medium transition-colors hover:text-primary ${
                      isActive("/dashboard/squad")
                        ? "text-foreground"
                        : "text-muted-foreground"
                    }`}
                  >
                    My Squad
                  </Link>
                  <Link
                    href="/dashboard/auction"
                    className={`text-sm font-medium transition-colors hover:text-primary ${
                      isActive("/dashboard/auction")
                        ? "text-foreground"
                        : "text-muted-foreground"
                    }`}
                  >
                    Auction
                  </Link>
                  <Link
                    href="/dashboard/leaderboard"
                    className={`text-sm font-medium transition-colors hover:text-primary ${
                      isActive("/dashboard/leaderboard")
                        ? "text-foreground"
                        : "text-muted-foreground"
                    }`}
                  >
                    Leaderboard
                  </Link>
                </>
              )}
            </nav>
          )}
        </div>

        <div className="flex items-center gap-2">
          {status === "unauthenticated" ? (
            <Link href="/auth/signin">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-sm btn-primary-enhanced">
                Sign In
              </Button>
            </Link>
          ) : status === "authenticated" ? (
            <>
              {activeGully && (
                <div className="mr-4 hidden md:block">
                  <span className="text-sm font-medium text-muted-foreground">
                    Active Gully:
                  </span>
                  <span className="ml-1 text-sm font-medium">
                    {activeGully.name}
                  </span>
                </div>
              )}

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-8 w-8 rounded-full"
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarImage
                        src={session?.user?.image || undefined}
                        alt={session?.user?.name || "User"}
                      />
                      <AvatarFallback>
                        {session?.user?.name?.charAt(0) || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {session?.user?.name}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {session?.user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link
                      href="/dashboard"
                      className="flex w-full cursor-pointer items-center font-medium text-blue-600"
                    >
                      <Home className="mr-2 h-4 w-4 text-blue-600" />
                      <span>Dashboard</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/dashboard/matches"
                      className="flex w-full cursor-pointer items-center"
                    >
                      <TrendingUp className="mr-2 h-4 w-4" />
                      <span>Matches</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/dashboard/gullies"
                      className="flex w-full cursor-pointer items-center"
                    >
                      <Users className="mr-2 h-4 w-4" />
                      <span>My Gullies</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/account"
                      className="flex w-full cursor-pointer items-center"
                    >
                      <User className="mr-2 h-4 w-4" />
                      <span>My Account</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/account/transactions"
                      className="flex w-full cursor-pointer items-center"
                    >
                      <Wallet className="mr-2 h-4 w-4" />
                      <span>Transactions</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/account/preferences"
                      className="flex w-full cursor-pointer items-center"
                    >
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Preferences</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="cursor-pointer"
                    onClick={() => signOut({ callbackUrl: "/" })}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            // Loading state
            <div className="h-10 w-20 rounded bg-gray-200 animate-pulse"></div>
          )}
        </div>
      </div>
    </header>
  );
}
