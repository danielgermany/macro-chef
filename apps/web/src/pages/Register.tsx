import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');
  const [pending, setPending] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setPending(true);
    try {
      await register(email, password, displayName.trim() || undefined);
      navigate('/meals');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setPending(false);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: '2rem auto', fontFamily: 'system-ui' }}>
      <h1>Create account</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <label>
          Display name (optional)
          <input
            type="text"
            value={displayName}
            onChange={(ev) => setDisplayName(ev.target.value)}
            style={{ width: '100%', padding: 8 }}
          />
        </label>
        <label>
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(ev) => setEmail(ev.target.value)}
            style={{ width: '100%', padding: 8 }}
          />
        </label>
        <label>
          Password (min 8 chars)
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(ev) => setPassword(ev.target.value)}
            style={{ width: '100%', padding: 8 }}
          />
        </label>
        {error ? <p style={{ color: 'crimson' }}>{error}</p> : null}
        <button type="submit" disabled={pending}>
          {pending ? 'Creating…' : 'Register'}
        </button>
      </form>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
