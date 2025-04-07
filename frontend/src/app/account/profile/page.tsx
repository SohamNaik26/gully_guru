"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronLeft, Mail, Phone, MapPin, Calendar, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";

interface ProfileFormData {
  name: string;
  email: string;
  mobile: string;
  dob: string;
  address: {
    line1: string;
    line2: string;
    city: string;
    state: string;
    pincode: string;
  };
}

export default function ProfilePage() {
  const { toast } = useToast();
  const [isEmailDialogOpen, setIsEmailDialogOpen] = useState(false);
  const [isMobileDialogOpen, setIsMobileDialogOpen] = useState(false);
  const [isAddressDialogOpen, setIsAddressDialogOpen] = useState(false);
  const [isPersonalInfoDialogOpen, setIsPersonalInfoDialogOpen] =
    useState(false);
  const [formData, setFormData] = useState<ProfileFormData>({
    name: "",
    email: "",
    mobile: "",
    dob: "",
    address: {
      line1: "",
      line2: "",
      city: "",
      state: "",
      pincode: "",
    },
  });

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // TODO: Implement email update API call
      toast({
        title: "Verification Email Sent",
        description: "Please check your email to verify your address.",
      });
      setIsEmailDialogOpen(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update email. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleMobileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // TODO: Implement mobile update API call
      toast({
        title: "OTP Sent",
        description: "Please enter the OTP sent to your mobile number.",
      });
      setIsMobileDialogOpen(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update mobile number. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleAddressSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // TODO: Implement address update API call
      toast({
        title: "Address Updated",
        description: "Your address has been updated successfully.",
      });
      setIsAddressDialogOpen(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update address. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handlePersonalInfoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // TODO: Implement personal info update API call
      toast({
        title: "Profile Updated",
        description: "Your personal information has been updated successfully.",
      });
      setIsPersonalInfoDialogOpen(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update profile. Please try again.",
        variant: "destructive",
      });
    }
  };

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
            <h1 className="text-2xl font-bold">Profile</h1>
            <p className="text-sm text-muted-foreground">
              Manage your personal information
            </p>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <Card className="mb-6">
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Contact Information</h2>

          {/* Mobile Number */}
          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex items-center gap-3">
              <Phone className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Mobile Number</p>
                <p className="text-sm text-muted-foreground">+91 XXXXXXXXXX</p>
              </div>
              <Badge variant="success">VERIFIED</Badge>
            </div>
            <Dialog
              open={isMobileDialogOpen}
              onOpenChange={setIsMobileDialogOpen}
            >
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  Change
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Update Mobile Number</DialogTitle>
                  <DialogDescription>
                    Enter your new mobile number. We'll send an OTP for
                    verification.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleMobileSubmit}>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="mobile">Mobile Number</Label>
                      <Input
                        id="mobile"
                        placeholder="+91 XXXXXXXXXX"
                        value={formData.mobile}
                        onChange={(e) =>
                          setFormData({ ...formData, mobile: e.target.value })
                        }
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="submit">Send OTP</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Email */}
          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex items-center gap-3">
              <Mail className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Email ID</p>
                <p className="text-sm text-muted-foreground">Not Added</p>
              </div>
              <Badge variant="secondary">PENDING</Badge>
            </div>
            <Dialog
              open={isEmailDialogOpen}
              onOpenChange={setIsEmailDialogOpen}
            >
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  Add Email
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Email Address</DialogTitle>
                  <DialogDescription>
                    Enter your email address. We'll send a verification link.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleEmailSubmit}>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="you@example.com"
                        value={formData.email}
                        onChange={(e) =>
                          setFormData({ ...formData, email: e.target.value })
                        }
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="submit">Send Verification</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Address */}
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <MapPin className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Address</p>
                <p className="text-sm text-muted-foreground">Not Available</p>
              </div>
            </div>
            <Dialog
              open={isAddressDialogOpen}
              onOpenChange={setIsAddressDialogOpen}
            >
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  Add Address
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>Add Address</DialogTitle>
                  <DialogDescription>
                    Enter your complete address details.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleAddressSubmit}>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="line1">Address Line 1</Label>
                      <Input
                        id="line1"
                        placeholder="Street address"
                        value={formData.address.line1}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            address: {
                              ...formData.address,
                              line1: e.target.value,
                            },
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="line2">Address Line 2</Label>
                      <Input
                        id="line2"
                        placeholder="Apartment, suite, etc."
                        value={formData.address.line2}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            address: {
                              ...formData.address,
                              line2: e.target.value,
                            },
                          })
                        }
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="city">City</Label>
                        <Input
                          id="city"
                          placeholder="City"
                          value={formData.address.city}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              address: {
                                ...formData.address,
                                city: e.target.value,
                              },
                            })
                          }
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="state">State</Label>
                        <Input
                          id="state"
                          placeholder="State"
                          value={formData.address.state}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              address: {
                                ...formData.address,
                                state: e.target.value,
                              },
                            })
                          }
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="pincode">PIN Code</Label>
                      <Input
                        id="pincode"
                        placeholder="PIN Code"
                        value={formData.address.pincode}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            address: {
                              ...formData.address,
                              pincode: e.target.value,
                            },
                          })
                        }
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="submit">Save Address</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </Card>

      {/* Personal Information */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Personal Information</h2>
            <Dialog
              open={isPersonalInfoDialogOpen}
              onOpenChange={setIsPersonalInfoDialogOpen}
            >
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  Edit
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Edit Personal Information</DialogTitle>
                  <DialogDescription>
                    Update your personal details.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handlePersonalInfoSubmit}>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        placeholder="Your full name"
                        value={formData.name}
                        onChange={(e) =>
                          setFormData({ ...formData, name: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="dob">Date of Birth</Label>
                      <Input
                        id="dob"
                        type="date"
                        value={formData.dob}
                        onChange={(e) =>
                          setFormData({ ...formData, dob: e.target.value })
                        }
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="submit">Save Changes</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <User className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="font-medium">N/A</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Date of Birth</p>
                <p className="font-medium">N/A</p>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
