/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "bcciplayerimages.s3.ap-south-1.amazonaws.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "bcciplayerimages.s3.amazonaws.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "assets.iplt20.com",
        pathname: "/**",
      },
    ],
  },
};

module.exports = nextConfig;
