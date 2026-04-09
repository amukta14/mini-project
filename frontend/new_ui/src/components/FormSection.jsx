import { motion } from 'framer-motion'

function FormSection({ index, title, description, children, className = '' }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.04 }}
      className={`glass-panel rounded-[28px] p-6 sm:p-7 ${className}`}
    >
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-rust/80">
            Section {String(index + 1).padStart(2, '0')}
          </p>
          <h2 className="mt-2 text-xl font-semibold text-white">{title}</h2>
        </div>
        {description ? <p className="max-w-xl text-sm leading-6 text-mist">{description}</p> : null}
      </div>
      {children}
    </motion.section>
  )
}

export default FormSection
