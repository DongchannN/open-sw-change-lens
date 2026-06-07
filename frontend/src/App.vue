<script setup>
import { onMounted, ref } from "vue";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const newsItems = ref([]);

onMounted(async () => {
  try {
    const response = await fetch(`${apiBaseUrl}/api/news`);
    if (!response.ok) {
      throw new Error(`Failed to fetch news: ${response.status}`);
    }

    const data = await response.json();
    newsItems.value = data.items ?? [];
  } catch (error) {
    console.error("뉴스를 불러오지 못했습니다.", error);
    newsItems.value = [];
  }
});

function formatDate(value) {
  if (!value) {
    return "";
  }

  return new Intl.DateTimeFormat("ko-KR", { dateStyle: "medium" }).format(
    new Date(value),
  );
}
</script>

<template>
  <main class="app-shell">
    <header class="page-header">
      <p class="eyebrow">GeekNews Insight Tracker</p>
      <h1>ChangeLens</h1>
      <p class="description">
        GeekNews 최신 글을 확인하고, 나에게 의미 있는 기술 변화를 기록합니다.
      </p>
    </header>

    <section class="news-section" aria-labelledby="news-heading">
      <h2 id="news-heading">최신 기술 뉴스</h2>

      <ul class="news-list">
        <li v-for="item in newsItems" :key="item.link" class="news-card">
          <a :href="item.link" target="_blank" rel="noreferrer" class="news-title">
            {{ item.title }}
          </a>
          <p v-if="item.summary" class="news-summary">
            {{ item.summary }}
          </p>
          <p v-if="item.published_at" class="news-date">
            {{ formatDate(item.published_at) }}
          </p>
        </li>
      </ul>
    </section>
  </main>
</template>
