import { motion } from 'framer-motion'

export default function StatCard({ label, value, icon, trend, color = 'brand' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-500 dark:text-slate-400">{label}</div>
          <div className="text-3xl font-bold mt-1">{value}</div>
          {trend && <div className="text-xs text-green-600 mt-1">{trend}</div>}
        </div>
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center bg-${color}-50 dark:bg-${color}-900/30 text-2xl`}>
          {icon}
        </div>
      </div>
    </motion.div>
  )
}
