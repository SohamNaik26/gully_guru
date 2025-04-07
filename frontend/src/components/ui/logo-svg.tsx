import { cn } from "@/lib/utils";

interface LogoSVGProps {
  className?: string;
  width?: number;
  height?: number;
}

export function LogoSVG({ className, width = 300, height = 80 }: LogoSVGProps) {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 600 160"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("", className)}
    >
      {/* Cricket Stumps */}
      <g className="stumps">
        <rect x="120" y="30" width="8" height="80" rx="2" fill="#1e293b" />
        <rect x="135" y="30" width="8" height="80" rx="2" fill="#1e293b" />
        <rect x="150" y="30" width="8" height="80" rx="2" fill="#1e293b" />
        {/* Bails */}
        <rect x="118" y="28" width="42" height="4" rx="1" fill="#1e293b" />
      </g>

      {/* Cricket Ball */}
      <circle cx="90" cy="100" r="15" fill="#dc2626" />
      <path
        d="M80 100 Q90 85, 100 100 Q90 115, 80 100"
        stroke="white"
        strokeWidth="1.5"
        fill="none"
      />

      {/* Text */}
      <text
        x="180"
        y="100"
        className="text-[64px] font-bold"
        fill="currentColor"
        style={{
          fontFamily: "system-ui, -apple-system, sans-serif",
          letterSpacing: "-0.05em",
        }}
      >
        GULLYGURU
      </text>

      {/* Green Line */}
      <line
        x1="90"
        y1="120"
        x2="510"
        y2="120"
        stroke="#16a34a"
        strokeWidth="3"
      />
    </svg>
  );
}
