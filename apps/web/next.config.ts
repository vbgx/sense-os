import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: process.cwd(),
  },
  webpack: (config) => {
    const appNodeModules = path.resolve(process.cwd(), "node_modules");
    config.resolve = config.resolve || {};
    config.resolve.modules = [
      appNodeModules,
      ...(config.resolve.modules || []),
    ];
    return config;
  },
};

export default nextConfig;
