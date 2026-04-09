import { AnimatePresence } from 'framer-motion'
import { Route, Routes, useLocation } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import NewProjectSetupPage from './pages/NewProjectSetupPage'
import QuestionnairePage from './pages/QuestionnairePage'
import RegisterPage from './pages/RegisterPage'

function App() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/questionnaire" element={<QuestionnairePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/new-project" element={<NewProjectSetupPage />} />
      </Routes>
    </AnimatePresence>
  )
}

export default App
