import { motion } from 'framer-motion'

function Card({ children, className = '', hoverable = true }) {
  return (
    <motion.div
      whileHover={hoverable ? { y: -6, scale: 1.01 } : undefined}
      transition={{ type: 'spring', stiffness: 240, damping: 20 }}
      className={`glass-panel-strong rounded-[28px] p-6 ${className}`}
    >
      {children}
    </motion.div>
  )
}

export default Card
