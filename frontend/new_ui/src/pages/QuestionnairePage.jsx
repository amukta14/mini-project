import { motion } from 'framer-motion'
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppShell from '../components/AppShell'
import Button from '../components/Button'
import FormSection from '../components/FormSection'
import Input from '../components/Input'
import MultiSelectChips from '../components/MultiSelectChips'
import ProgressBar from '../components/ProgressBar'
import { questionnaireQuestions } from '../data/mockData'
import { apiFetch } from '../lib/api'

const getInitialAnswers = () =>
  questionnaireQuestions.reduce((accumulator, question) => {
    accumulator[question.key] = question.type === 'multi' ? [] : question.type === 'slider' ? question.min : ''
    return accumulator
  }, {})

function QuestionnairePage() {
  const navigate = useNavigate()
  const [answers, setAnswers] = useState(getInitialAnswers)
  const [submitting, setSubmitting] = useState(false)

  const answeredCount = useMemo(
    () =>
      questionnaireQuestions.filter((question) => {
        const value = answers[question.key]
        return Array.isArray(value) ? value.length > 0 : value !== ''
      }).length,
    [answers],
  )

  const handleChange = (key, value) => {
    setAnswers((current) => ({ ...current, [key]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    try {
      // Map UI answers into backend questionnaire payload
      const domain = answers.interestDomain ? [answers.interestDomain] : []
      const skills = Array.isArray(answers.languages) ? answers.languages : []
      const experience_level = String(answers.skillLevel || '').toLowerCase()
      const time_available = Number(answers.timeCommitment || 0) <= 6 ? 'short' : Number(answers.timeCommitment || 0) <= 14 ? 'medium' : 'long'
      const team_or_individual = String(answers.teamPreference || '').toLowerCase().includes('solo') ? 'solo' : 'team'
      const hardware_availability = String(answers.hardware || '').toLowerCase().includes('embedded') ? 'basic' : 'none'
      const preferred_project_type =
        String(answers.outputType || '').toLowerCase().includes('web')
          ? 'application'
          : String(answers.outputType || '').toLowerCase().includes('mobile')
            ? 'application'
            : String(answers.outputType || '').toLowerCase().includes('hardware')
              ? 'system'
              : 'ml_model'
      const project_complexity_preference =
        String(answers.difficulty || '').toLowerCase().includes('high')
          ? 'complex'
          : String(answers.difficulty || '').toLowerCase().includes('stretch')
            ? 'moderate'
            : 'simple'

      const interests = String(answers.interestDomain || '').toLowerCase()

      const payload = {
        skills,
        core_skills: skills,
        other_skills: [],
        interests,
        experience_level,
        time_available,
        domain_preference: domain,
        project_complexity_preference,
        team_or_individual,
        hardware_availability,
        preferred_project_type,
        dataset_comfort: 'somewhat',
        learning_vs_execution: 'both',
        stretch_willingness: 'yes',
        skill_confidence_level: experience_level,
      }

      const data = await apiFetch('/recommend', { method: 'POST', body: payload })
      sessionStorage.setItem('projectiq:lastRecommendations', JSON.stringify(data.recommendations || []))
      navigate('/dashboard')
    } finally {
      setSubmitting(false)
    }
  }

  const renderField = (question) => {
    const value = answers[question.key]

    if (question.type === 'select') {
      return (
        <Input
          as="select"
          value={value}
          onChange={(event) => handleChange(question.key, event.target.value)}
          placeholder={question.placeholder}
        >
          {question.options.map((option) => (
            <option key={option} value={option} className="bg-navy text-white">
              {option}
            </option>
          ))}
        </Input>
      )
    }

    if (question.type === 'radio') {
      return (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {question.options.map((option) => {
            const selected = value === option

            return (
              <button
                key={option}
                type="button"
                onClick={() => handleChange(question.key, option)}
                className={`rounded-2xl border px-4 py-4 text-left text-sm transition duration-300 ${
                  selected
                    ? 'border-rust/45 bg-rust/18 text-white shadow-glow'
                    : 'border-white/10 bg-white/6 text-mist hover:border-white/20 hover:bg-white/10 hover:text-white'
                }`}
              >
                <span className="block font-medium">{option}</span>
              </button>
            )
          })}
        </div>
      )
    }

    if (question.type === 'multi') {
      return (
        <MultiSelectChips
          options={question.options}
          values={value}
          onChange={(nextValue) => handleChange(question.key, nextValue)}
        />
      )
    }

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/6 px-4 py-3">
          <span className="text-sm text-mist">Selected value</span>
          <span className="text-lg font-semibold text-white">
            {value}
            {question.suffix ? ` ${question.suffix}` : ''}
          </span>
        </div>
        <input
          type="range"
          min={question.min}
          max={question.max}
          step={question.step}
          value={value}
          onChange={(event) => handleChange(question.key, Number(event.target.value))}
          className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-rust"
        />
      </div>
    )
  }

  return (
    <AppShell
      eyebrow="Student Profiling"
      title="Tell us how you want to learn, build, and ship."
      subtitle="A structured academic questionnaire helps the recommendation engine surface projects that match your skills, ambition, and available resources."
      compact
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, delay: 0.1 }}
        className="space-y-6"
      >
        <ProgressBar value={answeredCount} total={questionnaireQuestions.length} />

        <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-2">
          {questionnaireQuestions.map((question, index) => (
            <FormSection
              key={question.key}
              index={index}
              title={question.label}
              description="Answer thoughtfully so the recommendation engine can prioritize the most relevant project directions."
              className={question.type === 'multi' ? 'lg:col-span-2' : ''}
            >
              {renderField(question)}
            </FormSection>
          ))}

          <div className="lg:col-span-2">
            <div className="glass-panel-strong rounded-[30px] p-6 sm:p-7">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="section-title">Ready For Matching</p>
                  <h2 className="mt-3 text-2xl font-semibold text-white">Submit your profile</h2>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-mist">
                    Your responses will tailor the dashboard toward projects that feel academically meaningful and realistically achievable.
                  </p>
                </div>
                <Button
                  type="submit"
                  className="sm:min-w-56"
                  disabled={submitting || answeredCount < questionnaireQuestions.length}
                >
                  View Recommendations
                </Button>
              </div>
            </div>
          </div>
        </form>
      </motion.div>
    </AppShell>
  )
}

export default QuestionnairePage
