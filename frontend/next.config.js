/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Rewrite config to direct frontend API calls on localhost to port 5000 (Express server)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
