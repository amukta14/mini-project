export async function apiFetch(path, { method = 'GET', body, headers } = {}) {
  const response = await fetch(path, {
    method,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(headers || {}) },
    body: body ? JSON.stringify(body) : undefined,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = data?.error || data?.message || 'Request failed'
    const err = new Error(message)
    err.status = response.status
    err.data = data
    throw err
  }
  return data
}

