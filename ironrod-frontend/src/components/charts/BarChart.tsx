"use client";

import React from "react";
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export interface BarChartProps {
  data: Array<{ [key: string]: any }>;
  xKey: string;
  dataKey: string;
}

export default function BarChart({ data, xKey, dataKey }: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <RechartsBarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey={dataKey} fill="#8884d8" />
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}
