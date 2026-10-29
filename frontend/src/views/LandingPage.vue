<template>
  <div class="landing-page">
    <!-- Шапка -->
    <header class="landing-header">
      <div class="logo">Пространство</div>
      <div class="auth-links">
        <router-link to="/login" class="btn-link">Войти</router-link>
        <router-link to="/register" class="btn-primary">Создать пространство</router-link>
      </div>
    </header>

    <!-- Главный экран -->
    <section class="hero-section">
      <h1>Ваше личное пространство<br>для проведения мероприятий</h1>
      <p class="hero-sub">
        Объедините все свои направления на одной странице. 
        Управляйте афишей, собирайте заявки и синхронизируйте события с Яндекс.Календарем.
      </p>
      <router-link to="/register" class="btn-cta">Начать бесплатно</router-link>
    </section>

    <!-- Преимущества -->
    <section class="features">
      <div class="feature-card">
        <h3>Одна ссылка</h3>
        <p>Вместо 5 разных каналов — один красивый сайт, который легко отправить клиенту.</p>
      </div>
      <div class="feature-card">
        <h3>Учет групп</h3>
        <p>Система сама посчитает участников и покажет, набралась ли критическая масса.</p>
      </div>
      <div class="feature-card">
        <h3>Яндекс.Календарь</h3>
        <p>Создавайте события на сайте — они мгновенно появляются у вас в телефоне.</p>
      </div>
    </section>
    
    <!-- Пример сайта (ссылка на демо Жени) -->
    <section class="demo-section">
      <p>Посмотрите, как это выглядит:</p>
      <router-link to="/jenyaz" class="btn-demo">Пример сайта (Женя Зонова)</router-link>
    </section>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: var(--color-bg);
  font-family: var(--font-sans);
  padding: 20px 40px;
}

/* Шапка */
.landing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0;
}
.logo {
  font-family: var(--font-serif);
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--color-text);
}
.auth-links {
  display: flex;
  gap: 20px;
  align-items: center;
}
.btn-link {
  color: var(--color-text);
  text-decoration: none;
  font-weight: 500;
}
.btn-primary {
  background: var(--color-text);
  color: white;
  padding: 10px 20px;
  text-decoration: none;
  border-radius: 4px;
  transition: 0.3s;
}
.btn-primary:hover { background: var(--color-accent); }

/* Главный экран */
.hero-section {
  text-align: center;
  max-width: 800px;
  margin: 80px auto;
}
.hero-section h1 {
  font-family: var(--font-serif);
  font-size: 3.5rem;
  color: var(--color-text);
  line-height: 1.2;
  margin-bottom: 20px;
}
.hero-sub {
  font-size: 1.2rem;
  color: var(--color-text-light);
  margin-bottom: 40px;
  line-height: 1.6;
}
.btn-cta {
  background: var(--color-accent);
  color: white;
  padding: 16px 40px;
  font-size: 1.1rem;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 600;
  display: inline-block;
  transition: 0.3s;
}
.btn-cta:hover { background: var(--color-text); }

/* Преимущества */
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1000px;
  margin: 0 auto 80px;
}
.feature-card {
  background: white;
  padding: 40px;
  border-radius: 4px;
  border-top: 4px solid var(--color-gold);
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
}
.feature-card h3 {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: var(--color-text);
}
.feature-card p { color: var(--color-text-light); line-height: 1.6; }

/* Демо */
.demo-section {
  text-align: center;
  margin-bottom: 60px;
}
.demo-section p { color: var(--color-text-light); margin-bottom: 15px; }
.btn-demo {
  color: var(--color-accent);
  text-decoration: underline;
  font-size: 1.1rem;
}
</style>