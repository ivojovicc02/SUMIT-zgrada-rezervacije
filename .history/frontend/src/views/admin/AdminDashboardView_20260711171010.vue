<template>
  <section>
    <h2>Pregled sustava</h2>

    <div class="stats-grid">
      <article>
        <span>Ukupno rezervacija</span>
        <strong>0</strong>
      </article>

      <article>
        <span>Rezervacije na čekanju</span>
        <strong>0</strong>
      </article>

      <article>
        <span>Aktivni prostori</span>
        <strong>0</strong>
      </article>

      <article>
        <span>Ukupan prihod</span>
        <strong>0 KM</strong>
      </article>
    </div>
  </section>
</template>

<style scoped>
h2 {
  margin-top: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

article {
  display: grid;
  gap: 12px;
  padding: 20px;
  background: white;
  border-radius: 12px;
}

strong {
  font-size: 28px;
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 520px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>