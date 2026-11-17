"use client";

import { useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const TOKEN_KEY = "department-ai-access-token";

export default function HomePage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const token = sessionStorage.getItem(TOKEN_KEY);
    if (token) loadProfile(token);
  }, []);

  async function loadProfile(token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Сессия завершилась. Войдите снова.");
      setProfile(await response.json());
      setError("");
    } catch (requestError) {
      sessionStorage.removeItem(TOKEN_KEY);
      setProfile(null);
      setError(requestError.message || "Не удалось связаться с backend.");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const body = new URLSearchParams({ username: email, password });
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!response.ok) {
        throw new Error(response.status === 401 ? "Проверьте email и пароль." : "Backend не смог выполнить вход.");
      }

      const { access_token: token } = await response.json();
      sessionStorage.setItem(TOKEN_KEY, token);
      setPassword("");
      await loadProfile(token);
    } catch (requestError) {
      setError(requestError.message || "Не удалось связаться с backend.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout() {
    sessionStorage.removeItem(TOKEN_KEY);
    setProfile(null);
    setError("");
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">D</span>
          <span>Department AI Platform</span>
        </a>
        <span className="local-label">Локальная платформа кафедры</span>
      </header>

      {profile ? (
        <section className="account-card" aria-labelledby="account-title">
          <p className="eyebrow">Личный кабинет</p>
          <h1 id="account-title">Здравствуйте, {profile.full_name}</h1>
          <p className="intro">{profile.email}</p>
          <h2>Организации</h2>
          {profile.memberships.length ? (
            <ul className="membership-list">
              {profile.memberships.map((membership) => (
                <li key={membership.organization_id}>
                  <span>{membership.organization_name}</span>
                  <span className="role-label">{membership.role}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-state">Пока нет членства в организациях.</p>
          )}
          <button className="secondary-button" onClick={handleLogout} type="button">
            Выйти
          </button>
        </section>
      ) : (
        <section className="login-card" aria-labelledby="login-title">
          <p className="eyebrow">Вход в платформу</p>
          <h1 id="login-title">Войдите в аккаунт кафедры</h1>
          <p className="login-description">Используйте email и пароль, выданные администратором.</p>
          <form className="login-form" onSubmit={handleSubmit}>
            <label htmlFor="email">Email</label>
            <input
              autoComplete="username"
              id="email"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
            <label htmlFor="password">Пароль</label>
            <input
              autoComplete="current-password"
              id="password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
            {error && <p className="error-message" role="alert">{error}</p>}
            <button className="primary-button" disabled={isLoading} type="submit">
              {isLoading ? "Входим…" : "Войти"}
            </button>
          </form>
        </section>
      )}

      <footer className="footer">Сервисы и данные платформы доступны через backend API</footer>
    </main>
  );
}
