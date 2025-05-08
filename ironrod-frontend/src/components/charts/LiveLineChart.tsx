import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

interface DataPoint { timestamp: string; value: number }
interface LiveProps { endpoint: string; title: string; pollInterval?: number }

export default function LiveLineChart({ endpoint, title, pollInterval = 5000 }: LiveProps) {
  const [data, setData] = useState<DataPoint[]>([])

  useEffect(() => {
    const fetch = () => axios.get<DataPoint[]>(endpoint).then(r => setData(r.data))
    fetch()
    const iv = setInterval(fetch, pollInterval)
    return () => clearInterval(iv)
  }, [endpoint, pollInterval])

  return (
    <div>
      <h2 className="text-lg font-medium mb-2">{title}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
