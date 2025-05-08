"use client"
"use client"
"use client"
"use client"
"use client"
"use client"
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

interface BarDataPoint { account: string; amount: number }
interface BarProps { endpoint: string; xKey: string; dataKey: string }

export default function BarChart({ endpoint, xKey, dataKey }: BarProps) {
  const [data, setData] = useState<BarDataPoint[]>([])

  useEffect(() => {
    axios.get<BarDataPoint[]>(endpoint).then(res => setData(res.data))
  }, [endpoint])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ReBarChart data={data}>
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Bar dataKey={dataKey} />
      </ReBarChart>
    </ResponsiveContainer>
  )
}
