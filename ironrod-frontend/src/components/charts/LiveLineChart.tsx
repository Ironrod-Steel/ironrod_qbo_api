"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export interface LiveLineChartProps {
  data: Array<{ [key: string]: any }>;
  xKey: string;
  dataKey: string;
}

export default function LiveLineChart({ data, xKey, dataKey }: LiveLineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} angle={-45} interval={0} />
        <YAxis />
        <Tooltip
          formatter={(value: number) => `$${parseFloat(value).toLocaleString()}`}
        />
        <Legend />
        <Line type="monotone" dataKey={dataKey} stroke="#8884d8" activeDot={{ r: 8 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

