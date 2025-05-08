"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/ui/Table";

export default function MentorScorecardPage() {
  const [scorecard, setScorecard] = useState({ dates: [], metrics: [] });

  useEffect(() => {
    axios.get("/api/qbo/scorecard/weekly").then(res => setScorecard(res.data));
  }, []);

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Mentor Weekly Scorecard</h1>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Week Of</TableHead>
            {scorecard.metrics.length > 0 &&
              Object.keys(scorecard.metrics[0]).map(key => (
                <TableHead key={key}>{key}</TableHead>
              ))
            }
          </TableRow>
        </TableHeader>
        <TableBody>
          {scorecard.dates.map((date, idx) => (
            <TableRow key={date}>
              <TableCell>{date}</TableCell>
              {Object.values(scorecard.metrics[idx] || {}).map((val, i) => (
                <TableCell key={i}>{val}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </main>
  );
}
