import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import AppShell from '../components/AppShell'
import Button from '../components/Button'
import Card from '../components/Card'
import Input from '../components/Input'
import { apiFetch } from '../lib/api'

function LoginPage() {
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const email = String(form.get('email') || '').trim()
    const password = String(form.get('password') || '')
    await apiFetch('/api/login', { method: 'POST', body: { email, password } })
    navigate('/questionnaire')
  }

  return (
    <AppShell
      eyebrow="Project Recommendation Engine"
      title="Find the right academic project direction with clarity."
      subtitle="A polished recommendation workspace for students exploring high-value project ideas across research, software, and systems domains."
      centered
      compact
    >
      <motion.div
        initial={{ opacity: 0, y: 26 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="mx-auto w-full max-w-md"
      >
        <Card className="rounded-[32px] p-8 sm:p-9">
          <div className="mb-8 text-center">
            <p className="section-title">Secure Login</p>
            <h2 className="mt-3 text-3xl font-semibold text-white">Welcome back</h2>
            <p className="mt-3 text-sm leading-6 text-mist">
              Sign in to continue reviewing project pathways, saved preferences, and curated recommendations.
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <Input label="Email" name="email" placeholder="Enter your email" required />
            <Input
              label="Password"
              name="password"
              type="password"
              placeholder="Enter your password"
              required
            />
            <Button type="submit" className="w-full">
              Sign In
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-mist">
            New to the platform?{' '}
            <Link to="/register" className="font-semibold text-rust hover:text-orange-300">
              Create an account
            </Link>
          </p>
        </Card>
      </motion.div>
    </AppShell>
  )
}

export default LoginPage
