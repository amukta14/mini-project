import { motion } from 'framer-motion'
import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import AppShell from '../components/AppShell'
import Button from '../components/Button'
import Card from '../components/Card'
import { apiFetch } from '../lib/api'

function datasetHref(project) {
  const link = project.dataset?.link?.trim()
  if (link) return link
  const name = project.dataset?.name?.trim()
  if (name) return `https://www.kaggle.com/search?q=${encodeURIComponent(name)}`
  return ''
}

function ProjectCard({ project, delay }) {
  const dsUrl = datasetHref(project)
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card className="h-full rounded-[30px]">
        <div className="flex h-full flex-col">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full border border-rust/25 bg-rust/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-orange-200">
              {Array.isArray(project.domain) ? project.domain.join(', ') : project.domain}
            </span>
            <span className="rounded-full border border-white/10 bg-white/6 px-3 py-1 text-xs font-medium text-mist">
              {project.difficulty}
            </span>
          </div>
          <h3 className="mt-5 text-2xl font-semibold text-white">{project.title}</h3>
          <p className="mt-4 flex-1 text-sm leading-7 text-mist">{project.description}</p>
          {dsUrl ? (
            <a
              href={dsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex max-w-full items-center gap-2 text-sm font-medium text-rust underline decoration-rust/40 underline-offset-4 hover:text-orange-200"
            >
              <span className="truncate">Dataset: {project.dataset?.name || 'Open dataset'}</span>
            </a>
          ) : null}
          <div className="mt-6 flex items-center gap-2 text-sm font-medium text-rust">
            <span className="h-2 w-2 rounded-full bg-rust" />
            Explore fit analysis
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

function DashboardPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [me, setMe] = useState(null)
  const [recs, setRecs] = useState([])

  useEffect(() => {
    ;(async () => {
      const status = await apiFetch('/api/me')
      if (!status.authenticated) {
        navigate('/')
        return
      }
      setMe(status)
      const fromNav = location.state && Array.isArray(location.state.recommendations) ? location.state.recommendations : null
      if (fromNav && fromNav.length) {
        setRecs(fromNav)
        try {
          sessionStorage.setItem('projectiq:lastRecommendations', JSON.stringify(fromNav))
        } catch {
          /* ignore quota */
        }
        navigate(location.pathname, { replace: true, state: {} })
        return
      }
      try {
        const raw = sessionStorage.getItem('projectiq:lastRecommendations')
        setRecs(raw ? JSON.parse(raw) : [])
      } catch {
        setRecs([])
      }
    })()
  }, [navigate, location.pathname, location.state])

  const profileHighlights = useMemo(() => {
    if (!me?.student_name) return ['Academic Projects', 'Personalized Matching', 'Professional Delivery']
    return [`Signed in as ${me.student_name}`, 'Explainable Matching', 'Industry-grade Ideas']
  }, [me])

  return (
    <AppShell
      eyebrow="Recommendation Dashboard"
      title="Project recommendations that feel rigorous, relevant, and achievable."
      subtitle="A calm, high-trust dashboard for exploring recommended project paths, seeing what is trending, and launching a new setup flow when your requirements change."
    >
      <motion.section
        initial={{ opacity: 0, y: 22 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55 }}
        className="glass-panel-strong rounded-[34px] p-7 sm:p-8"
      >
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="section-title">Student Profile Snapshot</p>
            <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">
              Your recommendation engine is calibrated and ready.
            </h2>
            <p className="mt-4 text-sm leading-7 text-mist">
              The current feed balances academic depth, execution feasibility, and portfolio value while preserving room for experimentation.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              {profileHighlights.map((highlight) => (
                <span
                  key={highlight}
                  className="rounded-full border border-white/10 bg-white/8 px-4 py-2 text-sm font-medium text-white"
                >
                  {highlight}
                </span>
              ))}
            </div>
          </div>

          <Button onClick={() => navigate('/new-project')} className="sm:min-w-56">
            Start New Project
          </Button>
        </div>
      </motion.section>

      <section>
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="section-title">Recommended Projects</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Best-fit options for your current profile</h2>
          </div>
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          {(recs || []).slice(0, 6).map((project, index) => (
            <ProjectCard
              key={`${project.title}-${index}`}
              project={{
                title: project.title,
                domain: project.domain,
                difficulty: project.difficulty,
                description: project.project_description || project.problem_statement || '',
                dataset: project.dataset,
              }}
              delay={index * 0.08}
            />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="section-title">Trending Projects</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">What students are exploring this week</h2>
          </div>
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          {(recs || []).slice(6, 12).map((project, index) => (
            <ProjectCard
              key={`${project.title}-t-${index}`}
              project={{
                title: project.title,
                domain: project.domain,
                difficulty: project.difficulty,
                description: project.project_description || project.problem_statement || '',
                dataset: project.dataset,
              }}
              delay={0.18 + index * 0.08}
            />
          ))}
        </div>
      </section>
    </AppShell>
  )
}

export default DashboardPage
