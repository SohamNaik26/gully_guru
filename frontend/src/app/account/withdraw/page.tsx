import Link from "next/link";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Info } from "lucide-react";

export default function WithdrawPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-[#c4000e] text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/account" className="text-white">
            ←
          </Link>
          <h1 className="text-lg font-semibold">Withdraw Cash</h1>
        </div>
      </header>

      <div className="p-4 space-y-4">
        {/* Balance Info */}
        <Card className="p-4 bg-yellow-50 border-yellow-100">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Withdrawable Balance</span>
            <Link
              href="/account/transactions/history"
              className="text-sm text-blue-600"
            >
              History
            </Link>
          </div>
          <div className="text-2xl font-bold mt-1">₹0</div>
        </Card>

        {/* Amount Input */}
        <div className="space-y-2">
          <Input
            type="number"
            placeholder="Enter Amount to withdraw*"
            className="text-lg p-6"
          />
          <p className="text-xs text-gray-500">
            Minimum Withdrawal Amount ₹100
          </p>
          <div className="flex items-start gap-2 text-xs text-gray-500 mt-2">
            <Info className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <p>
              Govt policy: 30% Tax will apply on 'Net Winnings'.{" "}
              <Link href="#" className="text-blue-600">
                Know more
              </Link>
            </p>
          </div>
        </div>

        {/* Withdrawal Methods */}
        <Tabs defaultValue="upi" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="upi" className="data-[state=active]:bg-red-50">
              UPI
            </TabsTrigger>
            <TabsTrigger value="bank" className="data-[state=active]:bg-red-50">
              Bank Account
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upi" className="mt-4">
            <Card className="p-4">
              <div className="space-y-4">
                <Input placeholder="Enter UPI ID" />
                <Input placeholder="Re-enter UPI ID" />
                <Button className="w-full bg-green-500 hover:bg-green-600">
                  Verify & Proceed
                </Button>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="bank" className="mt-4">
            <Card className="p-4">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input placeholder="Enter Account Number" />
                  <Input placeholder="Re-Enter Account Number" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input placeholder="Search by IFSC" />
                  <Button variant="outline" className="w-full">
                    Search by Bank Name
                  </Button>
                </div>
                <Button className="w-full bg-green-500 hover:bg-green-600">
                  Search
                </Button>
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Info Card */}
        <Card className="p-4 space-y-2">
          <h3 className="font-medium">Important</h3>
          <ul className="text-sm text-gray-600 space-y-2 list-disc pl-4">
            <li>Withdrawal will be processed within 24-48 hours</li>
            <li>Bank account should be in your name</li>
            <li>Ensure KYC is complete before withdrawal</li>
            <li>Minimum withdrawal amount is ₹100</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
