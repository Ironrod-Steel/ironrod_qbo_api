import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import LineChart from '@/components/charts/LineChart'
import BarChart from '@/components/charts/BarChart'
import LiveLineChart from '@/components/charts/LiveLineChart'

export default function DashboardPage() {
  return (
    <main className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Ironrod QBO Dashboard</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Profit & Loss</CardTitle></CardHeader>
          <CardContent>
            <LineChart endpoint="/api/qbo/pl" xKey="date" dataKey="amount" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Balance Sheet</CardTitle></CardHeader>
          <CardContent>
            <BarChart endpoint="/api/qbo/bs" xKey="account" dataKey="amount" />
          </CardContent>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Real-Time Revenue</CardTitle></CardHeader>
          <CardContent>
            <LiveLineChart endpoint="/api/qbo/realtime/revenue" title="Revenue Over Time" />
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
