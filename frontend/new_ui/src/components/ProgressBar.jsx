import { motion } from 'framer-motion'

function ProgressBar({ value, total }) {
  const percentage = Math.round((value / total) * 100)

  return (
    <div className="glass-panel rounded-full p-2">
      <div className="mb-2 flex items-center justify-between px-2 text-xs font-semibold uppercase tracking-[0.24em] text-mist">
        <span>Completion</span>
        <span>{percentage}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-white/8">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="h-full rounded-full bg-gradient-to-r from-rust via-orange-400 to-amber-200"
        />
      </div>
    </div>
  )
}

export default ProgressBar
