import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiCreateMeal, apiListMeals } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

function todayUtc(): string {
  const d = new Date();
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, '0'),
    String(d.getDate()).padStart(2, '0'),
  ].join('-');
}

export function Meals() {
  const { logout, email } = useAuth();
  const queryClient = useQueryClient();
  const [date, setDate] = useState(() => todayUtc());
  const [name, setName] = useState('');
  const [calories, setCalories] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  const mealsQuery = useQuery({
    queryKey: ['meals', date],
    queryFn: () => apiListMeals(date),
    enabled: Boolean(date),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      apiCreateMeal({
        name,
        calories: calories === '' ? undefined : Number(calories),
      }),
    onSuccess: async () => {
      setMessage('Meal saved.');
      setName('');
      setCalories('');
      await queryClient.invalidateQueries({ queryKey: ['meals', date] });
    },
    onError: (err: Error) => setMessage(err.message),
  });

  const totals = useMemo(() => {
    const meals = mealsQuery.data?.meals ?? [];
    let cal = 0;
    for (const m of meals) {
      cal += m.calories ?? 0;
    }
    return { cal };
  }, [mealsQuery.data]);

  return (
    <div style={{ maxWidth: 560, margin: '2rem auto', fontFamily: 'system-ui' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>Meals</h1>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <span style={{ fontSize: 14, color: '#444' }}>{email}</span>
          <Link to="/login" onClick={() => logout()}>
            Sign out
          </Link>
        </div>
      </header>

      <section style={{ marginTop: 24 }}>
        <label>
          Day (UTC calendar date){' '}
          <input type="date" value={date} onChange={(ev) => setDate(ev.target.value)} />
        </label>
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Log something eaten</h2>
        <form
          style={{ display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 320 }}
          onSubmit={(e) => {
            e.preventDefault();
            setMessage(null);
            createMutation.mutate();
          }}
        >
          <input
            placeholder="Meal name"
            required
            value={name}
            onChange={(ev) => setName(ev.target.value)}
            style={{ padding: 8 }}
          />
          <input
            placeholder="Calories (optional)"
            type="number"
            min={0}
            value={calories}
            onChange={(ev) => setCalories(ev.target.value)}
            style={{ padding: 8 }}
          />
          <button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Saving…' : 'Save meal'}
          </button>
        </form>
        {message ? <p style={{ marginTop: 8 }}>{message}</p> : null}
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Logged for {date}</h2>
        {mealsQuery.isLoading ? <p>Loading…</p> : null}
        {mealsQuery.isError ? (
          <p style={{ color: 'crimson' }}>{(mealsQuery.error as Error).message}</p>
        ) : null}
        {mealsQuery.data ? (
          <>
            <p style={{ color: '#444', fontSize: 14 }}>
              Total calories (logged): {totals.cal || '—'}
            </p>
            <ul style={{ paddingLeft: 20 }}>
              {mealsQuery.data.meals.map((m) => (
                <li key={m.id} style={{ marginBottom: 8 }}>
                  <strong>{m.name}</strong>
                  {m.calories != null ? ` — ${m.calories} kcal` : ''}{' '}
                  <span style={{ color: '#666', fontSize: 13 }}>
                    ({new Date(m.eatenAt).toLocaleString()})
                  </span>
                </li>
              ))}
            </ul>
            {mealsQuery.data.meals.length === 0 ? <p>No meals yet for this day.</p> : null}
          </>
        ) : null}
      </section>
    </div>
  );
}
