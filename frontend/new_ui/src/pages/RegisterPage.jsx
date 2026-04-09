import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import AppShell from '../components/AppShell'
import Button from '../components/Button'
import Card from '../components/Card'
import Input from '../components/Input'
import { apiFetch } from '../lib/api'

function RegisterPage() {
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const name = String(form.get('name') || '').trim()
    const email = String(form.get('email') || '').trim()
    const password = String(form.get('password') || '')
    await apiFetch('/api/register', { method: 'POST', body: { name, email, password } })
    navigate('/questionnaire')
  }

  return (
    <AppShell
      eyebrow="Create Profile"
      title="Set up your student workspace for smarter project matching."
      subtitle="A short onboarding flow captures your project profile and routes you to more relevant academic recommendations."
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
            <p className="section-title">Registration</p>
            <h2 className="mt-3 text-3xl font-semibold text-white">Create your account</h2>
            <p className="mt-3 text-sm leading-6 text-mist">
              Start with a focused setup and we will guide you into your academic preference questionnaire.
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <Input label="Full name" name="name" placeholder="Enter your full name" required />
            <Input label="Email" name="email" type="email" placeholder="Enter your email" required />
            <Input
              label="Password"
              name="password"
              type="password"
              placeholder="Create a password (min 8 characters)"
              required
            />
            <Button type="submit" className="w-full">
              Continue to Questionnaire
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-mist">
            Already registered?{' '}
            <Link to="/" className="font-semibold text-rust hover:text-orange-300">
              Return to login
            </Link>
          </p>
        </Card>
      </motion.div>
    </AppShell>
  )
}

export default RegisterPage
