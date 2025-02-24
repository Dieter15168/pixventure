import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // Only enable proxy in development
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/media/:path*',
          destination: 'http://127.0.0.1:8000/media/:path*', // Dev backend server
        },
      ];
    }

    // Production: no rewrites
    return [];
  },
};

export default nextConfig;
