import { redirect } from "next/navigation";
import { getServerSession } from "next-auth/next";
import { Suspense } from "react";
import { Toaster } from "sonner";
import { authOptions } from "../api/auth/[...nextauth]/route";
import Navbar from "@/components/layout/navbar";
import Sidebar from "@/components/layout/sidebar";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession(authOptions);

  if (!session?.user) {
    redirect("/auth/signin");
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar className="hidden lg:block" />
        <main className="flex-1 p-6">
          <Suspense fallback={<div>Loading...</div>}>{children}</Suspense>
        </main>
      </div>
      <Toaster position="top-right" />
    </div>
  );
}
