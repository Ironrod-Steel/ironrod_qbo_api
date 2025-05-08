"use client"
"use client"
"use client"
"use client"
"use client"
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table'

interface ScorecardData {
  dates: string[]
  metrics: Record<string, number | string>[]
}

export default function MentorScorecard() {
  const [data, setData] = useState<ScorecardData | null>(null)

  useEffect(() => {
    axios.get<ScorecardData>('/api/qbo/scorecard/weekly')
      .then(res => setData(res.data))
      .catch(console.error)
  }, [])

  if (!data) return <div>Loading scorecard...</div>

  const latest = data.dates.length - 1
  return (
    <div>
      <h2 className="text-lg font-medium mb-2">
        Mentor Weekly Scorecard — {data.dates[latest]}
      </h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Metric</TableHead>
            <TableHead>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Object.entries(data.metrics[latest]).map(([key, val]) => (
            <TableRow key={key}>
              <TableCell>{key}</TableCell>
              <TableCell>{val}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
