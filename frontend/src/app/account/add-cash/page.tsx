"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ChevronLeft,
  QrCode,
  Smartphone,
  CreditCard,
  Plus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function AddCashPage() {
  const [amount, setAmount] = useState("");
  const popularAmounts = [100, 200, 500, 1000, 2000, 5000];
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState("upi");

  const handleAmountSelect = (value: number) => {
    setAmount(value.toString());
  };

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/[^0-9]/g, "");
    setAmount(value);
  };

  const handleAddCash = () => {
    // TODO: Implement payment gateway integration
    console.log("Processing payment:", {
      amount,
      method: selectedPaymentMethod,
    });
  };

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4">
          <Link href="/account/overview">
            <Button variant="ghost" size="icon">
              <ChevronLeft className="h-6 w-6" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Add Cash</h1>
            <p className="text-sm text-muted-foreground">
              Add money to your account
            </p>
          </div>
        </div>
      </div>

      {/* Amount Selection */}
      <Card className="mb-6">
        <div className="p-6">
          <Label htmlFor="amount">Enter Amount</Label>
          <div className="mt-2">
            <Input
              id="amount"
              type="text"
              value={amount ? `₹${amount}` : ""}
              onChange={handleAmountChange}
              placeholder="₹0"
              className="text-2xl font-bold"
            />
          </div>

          <div className="mt-4">
            <Label className="text-sm text-muted-foreground">
              Popular Amounts
            </Label>
            <div className="grid grid-cols-3 gap-2 mt-2">
              {popularAmounts.map((value) => (
                <Button
                  key={value}
                  variant={amount === value.toString() ? "default" : "outline"}
                  onClick={() => handleAmountSelect(value)}
                  className="w-full"
                >
                  ₹{value}
                </Button>
              ))}
            </div>
          </div>

          <div className="mt-4 flex items-center gap-2">
            <Badge variant="outline" className="text-green-600">
              Get 10% Extra on ₹1000+
            </Badge>
            <Badge variant="outline" className="text-blue-600">
              100% Safe & Secure
            </Badge>
          </div>
        </div>
      </Card>

      {/* Payment Methods */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Payment Methods</h2>

          <Tabs
            defaultValue="upi"
            className="w-full"
            onValueChange={setSelectedPaymentMethod}
          >
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="upi">UPI</TabsTrigger>
              <TabsTrigger value="cards">Cards</TabsTrigger>
              <TabsTrigger value="netbanking">Net Banking</TabsTrigger>
            </TabsList>

            <TabsContent value="upi" className="mt-4">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Card className="p-4 cursor-pointer hover:bg-accent">
                    <div className="flex items-center gap-3">
                      <QrCode className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-medium">UPI QR</p>
                        <p className="text-sm text-muted-foreground">
                          Scan & Pay
                        </p>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-4 cursor-pointer hover:bg-accent">
                    <div className="flex items-center gap-3">
                      <Smartphone className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-medium">UPI ID</p>
                        <p className="text-sm text-muted-foreground">
                          Pay via UPI app
                        </p>
                      </div>
                    </div>
                  </Card>
                </div>

                <div className="flex items-center gap-2">
                  <Input placeholder="Enter UPI ID (e.g. 1234567890@upi)" />
                  <Button variant="outline">Verify</Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="cards" className="mt-4">
              <div className="space-y-4">
                <Card className="p-4">
                  <div className="flex items-center gap-3">
                    <CreditCard className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Credit / Debit Card</p>
                      <p className="text-sm text-muted-foreground">
                        All major cards accepted
                      </p>
                    </div>
                  </div>
                </Card>

                <div className="space-y-4">
                  <Input placeholder="Card Number" />
                  <div className="grid grid-cols-2 gap-4">
                    <Input placeholder="MM/YY" />
                    <Input placeholder="CVV" type="password" maxLength={3} />
                  </div>
                  <Input placeholder="Card Holder Name" />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="netbanking" className="mt-4">
              <div className="grid grid-cols-3 gap-4">
                {["HDFC", "ICICI", "SBI", "Axis", "Kotak", "Other Banks"].map(
                  (bank) => (
                    <Card
                      key={bank}
                      className="p-4 cursor-pointer hover:bg-accent"
                    >
                      <p className="font-medium text-center">{bank}</p>
                    </Card>
                  )
                )}
              </div>
            </TabsContent>
          </Tabs>

          <Button
            className="w-full mt-6"
            size="lg"
            disabled={!amount || parseInt(amount) < 100}
            onClick={handleAddCash}
          >
            Add ₹{amount || "0"}
          </Button>

          <p className="text-sm text-muted-foreground text-center mt-4">
            Min: ₹100 | Max: ₹25,000 per day
          </p>
        </div>
      </Card>
    </div>
  );
}
