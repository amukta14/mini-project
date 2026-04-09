import { motion } from 'framer-motion'

const variants = {
  primary:
    'bg-rust text-white shadow-glow hover:bg-rust/90 focus-visible:outline-rust/70',
  secondary:
    'border border-white/12 bg-white/8 text-ink hover:bg-white/12 focus-visible:outline-white/50',
  ghost:
    'text-mist hover:bg-white/8 hover:text-white focus-visible:outline-white/40',
}

function Button({
  children,
  className = '',
  type = 'button',
  variant = 'primary',
  disabled = false,
  ...props
}) {
  return (
    <motion.button
      whileHover={disabled ? undefined : { y: -2, scale: 1.01 }}
      whileTap={disabled ? undefined : { scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      type={type}
      disabled={disabled}
      className={`inline-flex items-center justify-center rounded-2xl px-5 py-3 text-sm font-semibold transition duration-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  )
}

export default Button
