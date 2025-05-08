"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import LineChart from "../components/charts/LineChart";
import BarChart from "../components/charts/BarChart";
import LiveLineChart from "../components/charts/LiveLineChart";

export default function DashboardPage() {
  const [plData, setPlData] = useState([]);
  const [bsData, setBsData] = useState([]);
  const [revData, setRevData] = useState([]);

  useEffect(() => {
    axios.get("/api/qbo/pl").then((res) => setPlData(res.data));
    axios.get("/api/qbo/bs").then((res) => {
      console.log("Balance Sheet data →", res.data); // 👈 Add this line
      setBsData(res.data);
    });
    axios.get("/api/qbo/realtime/revenue").then((res) => setRevData(res.data));
  }, []);

  return (
    <main className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Profit &amp; Loss</CardTitle>
        </CardHeader>
        <CardContent>
          <LineChart data={plData} xKey="date" dataKey="total" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Balance Sheet</CardTitle>
        </CardHeader>
        <CardContent>
          <BarChart data={bsData} xKey="account" dataKey="total" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Daily Revenue</CardTitle>
        </CardHeader>
        <CardContent>
          <LiveLineChart data={revData} xKey="timestamp" dataKey="value" />
        </CardContent>
      </Card>
    </main>
  );
}
