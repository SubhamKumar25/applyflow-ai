import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const COLORS = ['#1c61f5', '#10b981', '#f59e0b', '#ef4444', '#a855f7', '#0ea5e9']

export default function Analytics() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/jobs/analytics').then((r) => setData(r.data)).catch(() => {})
  }, [])

  const statusEntries = Object.entries(data?.by_status || {}).map(([name, value]) => ({ name, value }))
  const platformEntries = Object.entries(data?.by_platform || {}).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-slate-500 mt-1">Visual breakdown of your applications.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Stat label="Total" value={data?.total_applications ?? 0} />
        <Stat label="Applied" value={data?.applied ?? 0} />
        <Stat label="Interview" value={data?.interview ?? 0} />
        <Stat label="Rejected" value={data?.rejected ?? 0} />
        <Stat label="Offers" value={data?.offered ?? 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <div className="font-semibold mb-4">By status</div>
          <div className="h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={statusEntries} dataKey="value" nameKey="name" outerRadius={90} label>
                  {statusEntries.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-6">
          <div className="font-semibold mb-4">By platform</div>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={platformEntries}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgb(148 163 184 / 0.2)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#1c61f5" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="card p-5">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
    </div>
  )
}
