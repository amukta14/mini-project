import { motion } from 'framer-motion'
import { useMemo, useState } from 'react'
import AppShell from '../components/AppShell'
import Button from '../components/Button'
import FormSection from '../components/FormSection'
import Input from '../components/Input'
import LoadingAnimation from '../components/LoadingAnimation'
import MultiSelectChips from '../components/MultiSelectChips'
import ProgressBar from '../components/ProgressBar'
import { newProjectQuestions } from '../data/mockData'

const getInitialAnswers = () =>
  newProjectQuestions.reduce((accumulator, question) => {
    accumulator[question.key] = question.type === 'multi' ? [] : question.type === 'slider' ? question.min : ''
    return accumulator
  }, {})

function NewProjectSetupPage() {
  const [answers, setAnswers] = useState(getInitialAnswers)
  const [isGenerating, setIsGenerating] = useState(false)

  const answeredCount = useMemo(
    () =>
      newProjectQuestions.filter((question) => {
        const value = answers[question.key]
        return Array.isArray(value) ? value.length > 0 : value !== ''
      }).length,
    [answers],
  )

  const handleChange = (key, value) => {
    setAnswers((current) => ({ ...current, [key]: value }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    setIsGenerating(true)
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
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
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
      eyebrow="New Project Setup"
      title="Refine the delivery conditions for your next project path."
      subtitle="Use this extended setup form to tune scope, execution constraints, and innovation targets before generating the next batch of recommendations."
      compact
    >
      {isGenerating ? (
        <motion.div
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass-panel-strong mx-auto w-full max-w-3xl rounded-[34px] p-8 sm:p-10"
        >
          <LoadingAnimation />
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.08 }}
          className="space-y-6"
        >
          <ProgressBar value={answeredCount} total={newProjectQuestions.length} />

          <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-2">
            {newProjectQuestions.map((question, index) => (
              <FormSection
                key={question.key}
                index={index}
                title={question.label}
                description="Shape the operating conditions of your next build so the generated ideas stay practical and academically strong."
                className={question.type === 'multi' ? 'lg:col-span-2' : ''}
              >
                {renderField(question)}
              </FormSection>
            ))}

            <div className="lg:col-span-2">
              <div className="glass-panel-strong rounded-[30px] p-6 sm:p-7">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="section-title">Generate New Paths</p>
                    <h2 className="mt-3 text-2xl font-semibold text-white">Create a fresh recommendation batch</h2>
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-mist">
                      When you submit, the interface will transition into a loading state while it prepares a more targeted set of project directions.
                    </p>
                  </div>
                  <Button type="submit" className="sm:min-w-64" disabled={answeredCount < newProjectQuestions.length}>
                    Generate Recommendations
                  </Button>
                </div>
              </div>
            </div>
          </form>
        </motion.div>
      )}
    </AppShell>
  )
}

export default NewProjectSetupPage
