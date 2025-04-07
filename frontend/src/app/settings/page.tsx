import {
  ChevronLeft,
  ChevronRight,
  Wallet,
  Bell,
  Timer,
  Shield,
  MapPin,
  Smartphone,
} from "lucide-react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-black text-white p-4">
        <div className="flex items-center gap-4">
          <Link href="/dashboard">
            <ChevronLeft className="h-6 w-6" />
          </Link>
          <h1 className="font-semibold">Manage Account</h1>
        </div>
      </header>

      {/* Profile Section */}
      <div className="p-4 bg-black text-white">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-gray-700 flex items-center justify-center">
            <span className="text-2xl">S</span>
          </div>
          <div>
            <h2 className="text-lg font-semibold">SOHAM FIRST TEAM 1091655</h2>
            <p className="text-sm text-gray-400">Skill Score: 619</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 mb-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Wallet className="h-5 w-5" />
              <span>My Balance</span>
            </div>
            <span className="font-semibold">₹51</span>
          </div>
          <Button className="w-full mt-4 bg-green-500 hover:bg-green-600">
            ADD CASH
          </Button>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="p-4 space-y-6">
        {/* Alerts */}
        <Card>
          <CardContent className="p-4">
            <h3 className="text-lg font-semibold mb-4">Set Alerts</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-orange-100 p-2 rounded-lg">
                    <Wallet className="h-5 w-5 text-orange-500" />
                  </div>
                  <div>
                    <p className="font-medium">Deposit alerts</p>
                    <p className="text-sm text-muted-foreground">
                      Get notified when your monthly deposits reach a set amount
                    </p>
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-muted-foreground" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-red-100 p-2 rounded-lg">
                    <Bell className="h-5 w-5 text-red-500" />
                  </div>
                  <div>
                    <p className="font-medium">Loss alerts</p>
                    <p className="text-sm text-muted-foreground">
                      Get notified when your yearly loss reaches a set amount
                    </p>
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-muted-foreground" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Limits */}
        <Card>
          <CardContent className="p-4">
            <h3 className="text-lg font-semibold mb-4">Set Limits</h3>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Timer className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="font-medium">Take a break</p>
                  <p className="text-sm text-muted-foreground">
                    Restrict yourself from playing cash contests
                  </p>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        {/* GullyGuru Cares */}
        <Card>
          <CardContent className="p-4">
            <h3 className="text-lg font-semibold mb-4">GullyGuru Cares</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="bg-green-100 p-2 rounded-lg">
                  <Shield className="h-5 w-5 text-green-500" />
                </div>
                <div>
                  <p className="font-medium">Age limit</p>
                  <p className="text-sm text-muted-foreground">
                    We ensure that you are 18 years & above in order to join
                    cash contests
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <Shield className="h-5 w-5 text-purple-500" />
                </div>
                <div>
                  <p className="font-medium">KYC verification</p>
                  <p className="text-sm text-muted-foreground">
                    In order to withdraw or add cash, we ensure your
                    verification is complete
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="bg-red-100 p-2 rounded-lg">
                  <MapPin className="h-5 w-5 text-red-500" />
                </div>
                <div>
                  <p className="font-medium">Location permission</p>
                  <p className="text-sm text-muted-foreground">
                    We check your location to ensure you're not playing in a
                    restricted state
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Smartphone className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="font-medium">No cash transactions</p>
                  <p className="text-sm text-muted-foreground">
                    We strictly deal in online payments only to ensure
                    transparency
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Version */}
        <div className="text-center text-sm text-muted-foreground">
          VERSION 1.0.0
        </div>

        {/* Logout Button */}
        <Button
          variant="outline"
          className="w-full border-red-500 text-red-500 hover:bg-red-50"
        >
          LOGOUT
        </Button>
      </div>
    </div>
  );
}
