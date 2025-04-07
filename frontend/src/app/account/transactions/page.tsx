"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function TransactionsPage() {
  const [activeTab, setActiveTab] = useState("all");

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Link href="/account">
            <Button variant="ghost" size="icon">
              <ChevronLeft className="h-6 w-6" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Transactions</h1>
            <p className="text-sm text-muted-foreground">
              View your transaction history
            </p>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <Link
            href="/account/documents"
            className="text-sm text-primary hover:underline"
          >
            View Documents & Invoices
          </Link>
        </div>
      </div>

      {/* Transactions Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-4"
      >
        <TabsList className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="deposits">Deposits</TabsTrigger>
          <TabsTrigger value="withdrawals">Withdrawals</TabsTrigger>
          <TabsTrigger value="contests">Game Transactions</TabsTrigger>
          <TabsTrigger value="bonuses">Bonuses</TabsTrigger>
          <TabsTrigger value="cashback">Cashback</TabsTrigger>
          <TabsTrigger value="pending">Pending/Rejected</TabsTrigger>
        </TabsList>

        {/* All Transactions */}
        <TabsContent value="all">
          <Card className="p-6">
            <div className="text-center text-muted-foreground">
              No transactions found
            </div>
          </Card>
        </TabsContent>

        {/* Deposits */}
        <TabsContent value="deposits">
          <Card className="p-6">
            <div className="text-center text-muted-foreground">
              No deposits found
            </div>
          </Card>
        </TabsContent>

        {/* Withdrawals */}
        <TabsContent value="withdrawals">
          <Card className="p-6">
            <div className="text-center text-muted-foreground">
              No withdrawals found
            </div>
          </Card>
        </TabsContent>

        {/* Game Transactions */}
        <TabsContent value="contests">
          <Card className="p-6">
            <div className="text-center text-muted-foreground">
              No game transactions found
            </div>
          </Card>
        </TabsContent>

        {/* Bonuses */}
        <TabsContent value="bonuses">
          <Card className="p-6">
            <div className="text-center text-muted-foreground">
              No bonuses found
            </div>
          </Card>
        </TabsContent>

        {/* Cashback */}
        <TabsContent value="cashback">
          <Card className="p-6">
            <div className="text-center text-muted-foreground">
              No cashback transactions found
            </div>
          </Card>
        </TabsContent>

        {/* Pending/Rejected */}
        <TabsContent value="pending">
          <Card className="p-6">
            <div className="text-center text-muted-foreground">
              No pending or rejected transactions found
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
