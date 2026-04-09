function MultiSelectChips({ options, values = [], onChange }) {
  const toggleValue = (option) => {
    const nextValues = values.includes(option)
      ? values.filter((value) => value !== option)
      : [...values, option]

    onChange(nextValues)
  }

  return (
    <div className="flex flex-wrap gap-3">
      {options.map((option) => {
        const selected = values.includes(option)

        return (
          <button
            key={option}
            type="button"
            onClick={() => toggleValue(option)}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition duration-300 ${
              selected
                ? 'border-rust/50 bg-rust/18 text-white shadow-glow'
                : 'border-white/10 bg-white/6 text-mist hover:border-white/20 hover:bg-white/10 hover:text-white'
            }`}
          >
            {option}
          </button>
        )
      })}
    </div>
  )
}

export default MultiSelectChips
