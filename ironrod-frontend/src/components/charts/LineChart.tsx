"use client"
"use client"
"use client"
"use client"
"use client"
"use client"
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

interface LineDataPoint { date: string; amount: number }
interface LineProps { endpoint: string; xKey: string; dataKey: string }

export default function LineChart({ endpoint, xKey, dataKey }: LineProps) {
  const [data, setData] = useState<LineDataPoint[]>([])

  useEffect(() => {
    axios.get<LineDataPoint[]>(endpoint).then(res => setData(res.data))
  }, [endpoint])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ReLineChart data={data}>
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey={dataKey} dot={false} />
      </ReLineChart>
    </ResponsiveContainer>
  )
}
