import { cn } from "@/lib/utils";

interface LogoLoadingProps {
  className?: string;
  width?: number;
  height?: number;
}

export function LogoLoading({
  className,
  width = 300,
  height = 80,
}: LogoLoadingProps) {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 600 160"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("", className)}
    >
      {/* Cricket Stumps - Animated */}
      <g className="stumps animate-pulse">
        <rect
          x="120"
          y="30"
          width="8"
          height="80"
          rx="2"
          fill="currentColor"
          opacity="0.3"
        />
        <rect
          x="135"
          y="30"
          width="8"
          height="80"
          rx="2"
          fill="currentColor"
          opacity="0.5"
        />
        <rect
          x="150"
          y="30"
          width="8"
          height="80"
          rx="2"
          fill="currentColor"
          opacity="0.3"
        />
        {/* Bails */}
        <rect
          x="118"
          y="28"
          width="42"
          height="4"
          rx="1"
          fill="currentColor"
          opacity="0.5"
        />
      </g>

      {/* Cricket Ball - Animated */}
      <circle
        cx="90"
        cy="100"
        r="15"
        fill="#dc2626"
        className="animate-bounce"
      />

      {/* Text - Shimmer Effect */}
      <text
        x="180"
        y="100"
        className="text-[64px] font-bold"
        fill="currentColor"
        opacity="0.2"
        style={{
          fontFamily: "system-ui, -apple-system, sans-serif",
          letterSpacing: "-0.05em",
        }}
      >
        GULLYGURU
      </text>

      {/* Green Line - Loading Animation */}
      <line
        x1="90"
        y1="120"
        x2="510"
        y2="120"
        stroke="#16a34a"
        strokeWidth="3"
        strokeDasharray="10,5"
        className="animate-[dash_1.5s_linear_infinite]"
      />

      <style>{`
        @keyframes dash {
          to {
            stroke-dashoffset: -15;
          }
        }
      `}</style>
    </svg>
  );
}
