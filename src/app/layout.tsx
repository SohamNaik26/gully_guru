import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GullyGuru Fantasy Cricket",
  description: "Your ultimate fantasy cricket platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="relative min-h-screen overflow-hidden">
            {/* Cricket-themed background */}
            <div className="fixed inset-0 bg-gradient-to-br from-background via-background to-background/90">
              {/* Pitch pattern overlay */}
              <div className="absolute inset-0 opacity-5 pointer-events-none">
                <div className="h-full w-full bg-[linear-gradient(0deg,transparent_24%,var(--border)_25%,var(--border)_26%,transparent_27%,transparent_74%,var(--border)_75%,var(--border)_76%,transparent_77%,transparent)] bg-[length:60px_60px]" />
              </div>

              {/* Animated gradient blobs */}
              <div className="absolute inset-0">
                <div className="absolute top-0 -left-4 w-72 h-72 blob-primary rounded-full mix-blend-multiply filter blur-xl animate-blob" />
                <div className="absolute top-0 -right-4 w-72 h-72 blob-secondary rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000" />
                <div className="absolute -bottom-8 left-20 w-72 h-72 blob-accent rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000" />
              </div>
            </div>

            {/* Content */}
            <div className="relative">
              <div className="container mx-auto px-4 py-4">
                {/* Cricket ball decoration */}
                <div
                  className="pointer-events-none fixed top-10 right-10 w-20 h-20 rounded-full bg-secondary/20 animate-spin-slow hidden lg:block"
                  style={{ animationDuration: "30s" }}
                >
                  <div className="absolute inset-0 rounded-full bg-[linear-gradient(45deg,transparent_40%,white_45%,white_55%,transparent_60%)] rotate-45" />
                </div>

                {children}
              </div>
            </div>
          </div>
          <Toaster position="top-center" />
        </ThemeProvider>
      </body>
    </html>
  );
}
