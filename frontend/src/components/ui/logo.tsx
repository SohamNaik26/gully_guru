import Link from "next/link";
import { cn } from "@/lib/utils";
import { LogoSVG } from "./logo-svg";

interface LogoProps {
  className?: string;
  width?: number;
  height?: number;
  href?: string;
}

export function Logo({
  className,
  width = 150,
  height = 40,
  href = "/",
}: LogoProps) {
  const logo = (
    <div className={cn("relative", className)}>
      <LogoSVG
        width={width}
        height={height}
        className="dark:text-white text-slate-900"
      />
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="focus:outline-none">
        {logo}
      </Link>
    );
  }

  return logo;
}
