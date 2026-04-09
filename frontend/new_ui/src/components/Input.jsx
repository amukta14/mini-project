function Input({
  label,
  as = 'input',
  className = '',
  children,
  placeholder,
  ...props
}) {
  const sharedClassName =
    'w-full rounded-2xl border border-white/10 bg-white/6 px-4 py-3 text-sm text-white outline-none transition duration-300 placeholder:text-mist/60 focus:border-rust/60 focus:bg-white/10 focus:ring-2 focus:ring-rust/20'

  return (
    <label className="block">
      {label ? <span className="field-label">{label}</span> : null}
      {as === 'select' ? (
        <select className={`${sharedClassName} ${className}`} {...props}>
          {placeholder ? (
            <option value="" disabled className="bg-navy text-mist">
              {placeholder}
            </option>
          ) : null}
          {children}
        </select>
      ) : (
        <input placeholder={placeholder} className={`${sharedClassName} ${className}`} {...props} />
      )}
    </label>
  )
}

export default Input
