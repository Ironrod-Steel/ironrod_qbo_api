import React from 'react'
import MentorScorecard from '@/components/scorecard/MentorScorecard'

export default function MentorScorecardPage() {
  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Mentor Weekly Scorecard</h1>
      <MentorScorecard />
    </main>
  )
}
