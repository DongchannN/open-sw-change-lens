<script setup>
import { computed, onMounted, ref } from "vue";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
const newsItems = ref([]);
const cachedAt = ref("");
const errorMessage = ref("");
const isLoading = ref(false);
const hasNewsItems = computed(() => newsItems.value.length > 0);

async function refreshNews() {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch(`${apiBaseUrl}/api/news`);
    if (!response.ok) {
      throw new Error(`Failed to fetch news: ${response.status}`);
    }

    const data = await response.json();
    newsItems.value = data.items ?? [];
    cachedAt.value = data.cachedAt ?? data.cached_at ?? "";
  } catch (error) {
    console.error("뉴스를 불러오지 못했습니다.", error);
    errorMessage.value =
      "뉴스를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(refreshNews);

function formatDate(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getNewsItemKey(item, index) {
  return item.link || item.id || `${item.title ?? "news"}-${index}`;
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
      <div class="section-header">
        <div>
          <h2 id="news-heading">최신 기술 뉴스</h2>
          <p v-if="cachedAt" class="updated-at">
            마지막 갱신 {{ formatDate(cachedAt) }}
          </p>
        </div>
        <button
          type="button"
          class="refresh-button"
          :disabled="isLoading"
          @click="refreshNews"
        >
          {{ isLoading ? "불러오는 중" : "새로고침" }}
        </button>
      </div>

      <div
        v-if="isLoading && !hasNewsItems"
        class="state-panel"
        role="status"
        aria-live="polite"
      >
        <p class="state-title">뉴스를 불러오는 중입니다</p>
        <p class="state-description">GeekNews 최신 글을 확인하고 있습니다.</p>
      </div>

      <div
        v-else-if="errorMessage && !hasNewsItems"
        class="state-panel state-panel-error"
        role="alert"
        aria-live="assertive"
      >
        <p class="state-title">뉴스 목록을 표시할 수 없습니다</p>
        <p class="state-description">{{ errorMessage }}</p>
        <button
          type="button"
          class="retry-button"
          :disabled="isLoading"
          @click="refreshNews"
        >
          다시 시도
        </button>
      </div>

      <div
        v-else-if="!hasNewsItems"
        class="state-panel"
        role="status"
        aria-live="polite"
      >
        <p class="state-title">표시할 뉴스가 없습니다</p>
        <p class="state-description">새 글이 수집되면 이곳에 표시됩니다.</p>
      </div>

      <template v-else>
        <div
          v-if="errorMessage"
          class="error-banner"
          role="alert"
          aria-live="assertive"
        >
          <p>{{ errorMessage }}</p>
          <button
            type="button"
            class="retry-button"
            :disabled="isLoading"
            @click="refreshNews"
          >
            다시 시도
          </button>
        </div>

        <p
          v-if="isLoading"
          class="inline-refresh-status"
          role="status"
          aria-live="polite"
        >
          최신 뉴스로 갱신하는 중입니다.
        </p>

        <ul class="news-list">
          <li
            v-for="(item, index) in newsItems"
            :key="getNewsItemKey(item, index)"
            class="news-card"
          >
            <a
              :href="item.link"
              target="_blank"
              rel="noreferrer"
              class="news-title"
            >
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
      </template>
    </section>
  </main>
</template>
