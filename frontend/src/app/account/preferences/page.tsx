import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

export default function PreferencesPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-[#c4000e] text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/account" className="text-white">
            ←
          </Link>
          <h1 className="text-lg font-semibold">Preferences</h1>
        </div>
      </header>

      <div className="p-4 space-y-4">
        <Alert className="bg-green-50 border-green-100">
          <AlertDescription>
            Your preferences will be updated within 48 hours
          </AlertDescription>
        </Alert>

        {/* Contact Preferences */}
        <Card className="p-4 space-y-4">
          <h2 className="font-medium">Contact Preferences</h2>
          <p className="text-sm text-gray-600">GullyGuru may contact you by:</p>

          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox id="sms" defaultChecked />
              <label
                htmlFor="sms"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                SMS
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox id="phone" defaultChecked />
              <label
                htmlFor="phone"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Phone
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox id="whatsapp" defaultChecked />
              <label
                htmlFor="whatsapp"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                WhatsApp
              </label>
            </div>
          </div>
        </Card>

        {/* Message Preferences */}
        <Card className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-medium">Message Preferences</h2>
            <Link href="#" className="text-sm text-blue-600">
              read more
            </Link>
          </div>
          <p className="text-sm text-gray-600">
            You can control the communication you wish to receive from us.
          </p>

          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div></div>
              <div className="text-center font-medium">SMS</div>
              <div className="text-center font-medium">Email</div>
            </div>

            <div className="grid grid-cols-3 gap-4 items-center">
              <div className="text-sm">Newsletters</div>
              <div className="flex justify-center">
                <Checkbox id="sms-newsletter" />
              </div>
              <div className="flex justify-center">
                <Checkbox id="email-newsletter" />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 items-center">
              <div className="text-sm">Special Offers</div>
              <div className="flex justify-center">
                <Checkbox id="sms-offers" />
              </div>
              <div className="flex justify-center">
                <Checkbox id="email-offers" />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 items-center">
              <div className="text-sm">Tournaments/Contests</div>
              <div className="flex justify-center">
                <Checkbox id="sms-tournaments" defaultChecked />
              </div>
              <div className="flex justify-center">
                <Checkbox id="email-tournaments" />
              </div>
            </div>
          </div>
        </Card>

        {/* Account Deletion */}
        <Card className="p-4">
          <h2 className="font-medium mb-2">Account deletion</h2>
          <p className="text-sm text-gray-600 mb-4">
            To initiate deletion of your account please{" "}
            <Link href="/account/delete" className="text-blue-600">
              click here
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
