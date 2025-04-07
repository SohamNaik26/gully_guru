"use client";

import Link from "next/link";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  ArrowDownToLine,
  ArrowUpFromLine,
  Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function AccountOverviewPage() {
  // Mock data - replace with actual API calls
  const accountBalance = {
    total: 500,
    withdrawable: 450,
    bonus: 50,
    winnings: 200,
    deposits: 250,
  };

  const recentTransactions = [
    {
      id: 1,
      type: "deposit",
      amount: 100,
      status: "success",
      date: "2024-02-20",
      description: "Added via UPI",
    },
    {
      id: 2,
      type: "contest",
      amount: -50,
      status: "success",
      date: "2024-02-19",
      description: "IND vs ENG Contest Entry",
    },
    {
      id: 3,
      type: "withdrawal",
      amount: -200,
      status: "pending",
      date: "2024-02-18",
      description: "Withdrawal to bank account",
    },
  ];

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4">
          <Link href="/account">
            <Button variant="ghost" size="icon">
              <ChevronLeft className="h-6 w-6" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Account Overview</h1>
            <p className="text-sm text-muted-foreground">
              View your balance and recent transactions
            </p>
          </div>
        </div>
      </div>

      {/* Balance Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Total Balance</p>
          <p className="text-2xl font-bold">₹{accountBalance.total}</p>
          <div className="mt-2 flex items-center gap-2">
            <Badge variant="outline">
              Withdrawable: ₹{accountBalance.withdrawable}
            </Badge>
          </div>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Bonus Balance</p>
          <p className="text-2xl font-bold">₹{accountBalance.bonus}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Total Winnings</p>
          <p className="text-2xl font-bold">₹{accountBalance.winnings}</p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Total Deposits</p>
          <p className="text-2xl font-bold">₹{accountBalance.deposits}</p>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <Link href="/account/add-cash">
          <Card className="p-4 hover:bg-accent transition-colors cursor-pointer">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-full">
                  <Plus className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium">Add Cash</p>
                  <p className="text-sm text-muted-foreground">
                    Add money to your account
                  </p>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </Card>
        </Link>

        <Link href="/account/withdraw">
          <Card className="p-4 hover:bg-accent transition-colors cursor-pointer">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-full">
                  <ArrowUpFromLine className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium">Withdraw</p>
                  <p className="text-sm text-muted-foreground">
                    Withdraw your winnings
                  </p>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </Card>
        </Link>

        <Link href="/account/transactions">
          <Card className="p-4 hover:bg-accent transition-colors cursor-pointer">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-full">
                  <Clock className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium">Transaction History</p>
                  <p className="text-sm text-muted-foreground">
                    View all transactions
                  </p>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </Card>
        </Link>
      </div>

      {/* Recent Transactions */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Transactions</h2>
            <Link href="/account/transactions">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>
          <div className="space-y-4">
            {recentTransactions.map((transaction) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between py-2"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-full">
                    {transaction.type === "deposit" && (
                      <ArrowDownToLine className="h-5 w-5 text-green-600" />
                    )}
                    {transaction.type === "withdrawal" && (
                      <ArrowUpFromLine className="h-5 w-5 text-red-600" />
                    )}
                    {transaction.type === "contest" && (
                      <Clock className="h-5 w-5 text-primary" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-muted-foreground">
                      {transaction.date}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p
                    className={`font-medium ${
                      transaction.amount > 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {transaction.amount > 0 ? "+" : ""}
                    {transaction.amount}
                  </p>
                  <Badge
                    variant={
                      transaction.status === "success" ? "success" : "secondary"
                    }
                    className="text-xs"
                  >
                    {transaction.status.toUpperCase()}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
