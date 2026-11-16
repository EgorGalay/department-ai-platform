export default function HomePage() {
  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">D</span>
          <span>Department AI Platform</span>
        </a>
        <span className="local-label">Локальная платформа кафедры</span>
      </header>

      <section className="welcome-card" aria-labelledby="welcome-title">
        <p className="eyebrow">Рабочая среда</p>
        <h1 id="welcome-title">Материалы кафедры и AI-инструменты — в одном месте.</h1>
        <p className="intro">
          Здесь будут доступны база знаний, обработка документов и помощники для учёбы и
          исследований. Платформа подключается к локальным AI-сервисам через backend.
        </p>
        <a className="api-link" href="http://localhost:8000/api/v1/health" target="_blank" rel="noreferrer">
          Проверить backend API <span aria-hidden="true">↗</span>
        </a>
      </section>

      <section className="module-grid" aria-label="Направления платформы">
        <article className="module-card">
          <span className="module-number">01</span>
          <h2>База знаний</h2>
          <p>Поиск по материалам дисциплин с ответами и ссылками на источники.</p>
          <span className="status">Следующий этап</span>
        </article>
        <article className="module-card">
          <span className="module-number">02</span>
          <h2>Документы</h2>
          <p>Проверка структуры и оформление работ по требованиям кафедры.</p>
          <span className="status">Запланировано</span>
        </article>
        <article className="module-card">
          <span className="module-number">03</span>
          <h2>Помощники</h2>
          <p>Инструменты для образовательных и исследовательских задач.</p>
          <span className="status">Запланировано</span>
        </article>
      </section>

      <footer className="footer">Прототип · сервисы и данные размещаются на сервере кафедры</footer>
    </main>
  );
}
