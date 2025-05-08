import Link from 'next/link'
import '@/styles/globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="p-4 bg-gray-100 space-x-4">
          <Link href="/">Dashboard</Link>
          <Link href="/mentor-scorecard">Mentor Scorecard</Link>
        </nav>
        {children}
      </body>
    </html>
  )
}
