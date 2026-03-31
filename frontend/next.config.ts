import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://vishwass.onrender.com'
  },
  // Force rebuild
  output: 'standalone',
  trailingSlash: true,
};

export default nextConfig;
