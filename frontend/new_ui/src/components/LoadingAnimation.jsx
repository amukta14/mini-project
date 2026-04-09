import { motion } from 'framer-motion'

function LoadingAnimation({ label = 'Generating recommendations...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-5 py-10 text-center">
      <div className="relative flex h-16 w-16 items-center justify-center">
        <motion.span
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.15, 0.5] }}
          transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute h-full w-full rounded-full border border-rust/35"
        />
        <motion.span
          animate={{ rotate: 360 }}
          transition={{ duration: 1.8, repeat: Infinity, ease: 'linear' }}
          className="h-9 w-9 rounded-full border-2 border-rust border-t-transparent"
        />
      </div>
      <div>
        <p className="text-lg font-semibold text-white">{label}</p>
        <p className="mt-2 max-w-md text-sm leading-6 text-mist">
          We are synthesizing your academic preferences, technical constraints, and delivery goals into a focused set of project paths.
        </p>
      </div>
    </div>
  )
}

export default LoadingAnimation
