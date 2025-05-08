/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/qbo/:path*',
        destination: 'http://localhost:8001/api/qbo/:path*'
      }
    ]
  }
}
