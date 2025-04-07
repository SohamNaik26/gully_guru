import {
  ChevronRight,
  User,
  Phone,
  Mail,
  MapPin,
  Calendar,
} from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function AccountPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-[#c4000e] text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-white">
            ←
          </Link>
          <h1 className="text-lg font-semibold">My Account</h1>
        </div>
        <Link
          href="/account/add-cash"
          className="bg-white text-[#c4000e] px-4 py-1.5 rounded-full text-sm font-medium flex items-center gap-1"
        >
          Add Cash <span className="text-lg">+</span>
        </Link>
      </header>

      <div className="p-4 space-y-4">
        {/* Account Overview */}
        <Link href="/account/overview">
          <Card className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <User className="h-5 w-5 text-gray-500" />
              <div>
                <p className="font-medium">Account Overview</p>
                <p className="text-sm text-gray-500">
                  View your account balance and transactions
                </p>
              </div>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400" />
          </Card>
        </Link>

        {/* Profile */}
        <Link href="/account/profile">
          <Card className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <User className="h-5 w-5 text-gray-500" />
              <div>
                <p className="font-medium">Profile</p>
                <p className="text-sm text-gray-500">
                  Manage your personal information
                </p>
              </div>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400" />
          </Card>
        </Link>

        {/* Account Details */}
        <Card className="p-4 space-y-4">
          <h2 className="font-medium">Account Details</h2>

          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="bg-green-100 p-2 rounded-lg">
                <Phone className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm text-gray-600">Mobile</p>
                  <Badge variant="success" className="text-xs">
                    VERIFIED
                  </Badge>
                </div>
                <p className="font-medium">+91 XXXXXXXXXX</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="bg-orange-100 p-2 rounded-lg">
                <Mail className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm text-gray-600">Email ID</p>
                  <Badge variant="secondary" className="text-xs">
                    PENDING
                  </Badge>
                </div>
                <button className="text-blue-600 text-sm font-medium">
                  Add email
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <p className="font-medium">Personal Information</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Name</p>
                  <p>N/A</p>
                </div>
                <div>
                  <p className="text-gray-500">Date of Birth</p>
                  <p>N/A</p>
                </div>
                <div>
                  <p className="text-gray-500">Pincode</p>
                  <p>N/A</p>
                </div>
                <div>
                  <p className="text-gray-500">Location</p>
                  <p>Not Available</p>
                </div>
              </div>
              <button className="text-blue-600 text-sm font-medium">
                Add Address Details
              </button>
            </div>
          </div>
        </Card>

        {/* Other Options */}
        <Link href="/account/withdraw">
          <Card className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-purple-100 p-2 rounded-lg">
                <svg
                  className="h-5 w-5 text-purple-600"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M12 2v20M2 12h20" />
                </svg>
              </div>
              <p className="font-medium">Withdraw Cash</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400" />
          </Card>
        </Link>

        <Link href="/account/preferences">
          <Card className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <svg
                  className="h-5 w-5 text-blue-600"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                  <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
                </svg>
              </div>
              <p className="font-medium">Preferences</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400" />
          </Card>
        </Link>
      </div>
    </div>
  );
}
