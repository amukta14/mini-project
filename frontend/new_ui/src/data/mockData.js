export const recommendedProjects = [
  {
    title: 'Smart Campus Energy Optimizer',
    domain: 'IoT Analytics',
    difficulty: 'Intermediate',
    description:
      'Forecast classroom energy demand and recommend efficient schedules using sensor streams and lightweight ML.',
  },
  {
    title: 'AI Research Paper Navigator',
    domain: 'NLP',
    difficulty: 'Advanced',
    description:
      'Build an academic assistant that clusters papers by theme, summarizes findings, and suggests related reading paths.',
  },
  {
    title: 'Rural Health Triage Dashboard',
    domain: 'Healthcare',
    difficulty: 'Intermediate',
    description:
      'Design a data-driven intake dashboard that prioritizes patient cases and highlights resource constraints.',
  },
]

export const trendingProjects = [
  {
    title: 'Autonomous Lab Equipment Monitor',
    domain: 'Embedded Systems',
    difficulty: 'Advanced',
    description:
      'Track device health in university labs with anomaly alerts, usage trends, and downtime forecasting.',
  },
  {
    title: 'Curriculum Skills Gap Mapper',
    domain: 'EdTech',
    difficulty: 'Beginner',
    description:
      'Compare course outcomes with job market skills and visualize the strongest improvement opportunities.',
  },
  {
    title: 'Sustainable Supply Route Planner',
    domain: 'Operations Research',
    difficulty: 'Advanced',
    description:
      'Optimize multi-stop delivery routes under carbon caps, budget limits, and service-level constraints.',
  },
]

export const questionnaireQuestions = [
  {
    key: 'interestDomain',
    label: 'Primary Interest Domain',
    type: 'select',
    placeholder: 'Choose your strongest area',
    options: ['Artificial Intelligence', 'Web Development', 'Data Science', 'Cybersecurity', 'IoT Systems'],
  },
  {
    key: 'skillLevel',
    label: 'Skill Level',
    type: 'radio',
    options: ['Beginner', 'Intermediate', 'Advanced'],
  },
  {
    key: 'languages',
    label: 'Preferred Programming Languages',
    type: 'multi',
    options: ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'R'],
  },
  {
    key: 'hardware',
    label: 'Hardware Availability',
    type: 'select',
    placeholder: 'Select your setup',
    options: ['Laptop only', 'Laptop + GPU', 'University lab access', 'Embedded hardware kit'],
  },
  {
    key: 'teamPreference',
    label: 'Team Preference',
    type: 'radio',
    options: ['Solo', 'Pair', 'Small Team'],
  },
  {
    key: 'timeCommitment',
    label: 'Time Commitment (hours per week)',
    type: 'slider',
    min: 2,
    max: 30,
    step: 1,
    suffix: 'hrs',
  },
  {
    key: 'projectGoal',
    label: 'Project Goal',
    type: 'radio',
    options: ['Portfolio-ready product', 'Research publication', 'Competition submission'],
  },
  {
    key: 'difficulty',
    label: 'Preferred Difficulty Level',
    type: 'radio',
    options: ['Comfortable', 'Stretching', 'High challenge'],
  },
  {
    key: 'outputType',
    label: 'Interested Output Type',
    type: 'select',
    placeholder: 'Pick your ideal result',
    options: ['Web App', 'Mobile App', 'Research Prototype', 'Hardware Demo', 'Analytics Dashboard'],
  },
  {
    key: 'constraints',
    label: 'Constraints',
    type: 'multi',
    options: ['Low budget', 'Short timeline', 'Need mentor support', 'Minimal hardware', 'Small dataset'],
  },
]

export const newProjectQuestions = [
  {
    key: 'duration',
    label: 'Duration',
    type: 'select',
    placeholder: 'Expected project duration',
    options: ['2-4 weeks', '1-2 months', '3-4 months', 'Semester-long'],
  },
  {
    key: 'budget',
    label: 'Budget Sensitivity',
    type: 'slider',
    min: 0,
    max: 1000,
    step: 50,
    suffix: 'USD',
  },
  {
    key: 'datasetAvailability',
    label: 'Dataset Availability',
    type: 'radio',
    options: ['Existing dataset', 'Can collect data', 'Need synthetic data'],
  },
  {
    key: 'impact',
    label: 'Real-world Impact Priority',
    type: 'slider',
    min: 1,
    max: 10,
    step: 1,
    suffix: '/10',
  },
  {
    key: 'deployment',
    label: 'Deployment Preference',
    type: 'radio',
    options: ['Local demo', 'Cloud deployment', 'Mobile release', 'Embedded deployment'],
  },
  {
    key: 'learningGoal',
    label: 'Learning Goal',
    type: 'multi',
    options: ['Model building', 'UI/UX', 'System design', 'Data engineering', 'DevOps'],
  },
  {
    key: 'specificity',
    label: 'Domain Specificity',
    type: 'select',
    placeholder: 'How specific should the domain be?',
    options: ['Broad and flexible', 'Moderately focused', 'Highly specialized'],
  },
  {
    key: 'integration',
    label: 'Integration Needs',
    type: 'multi',
    options: ['API integration', 'Sensors / hardware', 'Database layer', 'Authentication', 'Visualization'],
  },
  {
    key: 'deadlinePressure',
    label: 'Deadline Pressure',
    type: 'radio',
    options: ['Low', 'Moderate', 'High'],
  },
  {
    key: 'innovation',
    label: 'Innovation Level',
    type: 'slider',
    min: 1,
    max: 10,
    step: 1,
    suffix: '/10',
  },
]
