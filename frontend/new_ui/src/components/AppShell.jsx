import { motion } from 'framer-motion'

function AppShell({ eyebrow, title, subtitle, children, centered = false, compact = false }) {
  return (
    <div className="relative min-h-screen overflow-hidden px-4 py-8 sm:px-6 lg:px-8">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[10%] top-20 h-56 w-56 animate-float rounded-full bg-rust/15 blur-3xl" />
        <div
          className="absolute right-[8%] top-12 h-72 w-72 rounded-full bg-sky-400/10 blur-3xl"
          style={{ animation: 'float 12s ease-in-out infinite' }}
        />
        <div className="absolute bottom-8 left-1/2 h-48 w-48 -translate-x-1/2 rounded-full bg-white/5 blur-3xl" />
      </div>

      <div
        className={`relative z-10 mx-auto flex w-full max-w-7xl flex-col ${
          compact ? 'gap-8' : 'gap-10'
        }`}
      >
        <motion.header
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className={centered ? 'mx-auto max-w-3xl text-center' : 'max-w-3xl'}
        >
          {eyebrow ? <p className="section-title">{eyebrow}</p> : null}
          <h1 className="mt-4 text-balance text-4xl font-semibold leading-tight text-white sm:text-5xl">
            {title}
          </h1>
          {subtitle ? <p className="mt-4 text-lg leading-8 text-mist">{subtitle}</p> : null}
        </motion.header>

        {children}
      </div>
    </div>
  )
}

export default AppShell
