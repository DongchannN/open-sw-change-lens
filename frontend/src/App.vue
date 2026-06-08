<script setup>
import { computed, onMounted, ref } from "vue";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
const newsItems = ref([]);
const insightItems = ref([]);
const cachedAt = ref("");
const errorMessage = ref("");
const insightErrorMessage = ref("");
const isLoading = ref(false);
const isInsightLoading = ref(false);
const saveStates = ref({});
const hasNewsItems = computed(() => newsItems.value.length > 0);
const hasInsightItems = computed(() => insightItems.value.length > 0);
const finalSaveStates = ["saved", "duplicate"];

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

async function refreshInsights() {
  isInsightLoading.value = true;
  insightErrorMessage.value = "";

  try {
    const response = await fetch(`${apiBaseUrl}/api/insights`);
    if (!response.ok) {
      throw new Error(`Failed to fetch insights: ${response.status}`);
    }

    const data = await response.json();
    insightItems.value = data.items ?? [];
    syncSaveStatesFromInsights();
  } catch (error) {
    console.error("저장한 인사이트를 불러오지 못했습니다.", error);
    insightErrorMessage.value =
      "저장한 인사이트를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
  } finally {
    isInsightLoading.value = false;
  }
}

onMounted(() => {
  refreshNews();
  refreshInsights();
});

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

function getPublishedAt(item) {
  return item.publishedAt ?? item.published_at ?? "";
}

function getSaveState(link) {
  return saveStates.value[link] ?? "idle";
}

function setSaveState(link, state) {
  saveStates.value = {
    ...saveStates.value,
    [link]: state,
  };
}

function syncSaveStatesFromInsights() {
  const nextSaveStates = {};

  for (const [link, state] of Object.entries(saveStates.value)) {
    if (state === "saving" || state === "error") {
      nextSaveStates[link] = state;
    }
  }

  for (const insight of insightItems.value) {
    if (insight.link) {
      nextSaveStates[insight.link] = "saved";
    }
  }

  saveStates.value = nextSaveStates;
}

function getSaveButtonLabel(item) {
  const state = getSaveState(item.link);

  if (state === "saving") {
    return "저장 중";
  }

  if (state === "saved" || state === "duplicate") {
    return "저장됨";
  }

  return "저장";
}

async function saveInsight(item) {
  const currentState = getSaveState(item.link);
  if (currentState === "saving" || finalSaveStates.includes(currentState)) {
    return;
  }

  setSaveState(item.link, "saving");

  try {
    const response = await fetch(`${apiBaseUrl}/api/insights`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: item.title,
        link: item.link,
        summary: item.summary ?? "",
        publishedAt: getPublishedAt(item) || null,
        impact: "Medium",
      }),
    });

    if (response.status === 409) {
      setSaveState(item.link, "duplicate");
      await refreshInsights();
      return;
    }

    if (!response.ok) {
      throw new Error(`Failed to save insight: ${response.status}`);
    }

    setSaveState(item.link, "saved");
    await refreshInsights();
  } catch (error) {
    console.error("관심 뉴스를 저장하지 못했습니다.", error);
    setSaveState(item.link, "error");
  }
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
            <div class="news-card-header">
              <a
                :href="item.link"
                target="_blank"
                rel="noreferrer"
                class="news-title"
              >
                {{ item.title }}
              </a>
              <button
                type="button"
                class="save-button"
                :class="{
                  'save-button-saved':
                    getSaveState(item.link) === 'saved' ||
                    getSaveState(item.link) === 'duplicate',
                  'save-button-error': getSaveState(item.link) === 'error',
                }"
                :disabled="
                  getSaveState(item.link) === 'saving' ||
                  getSaveState(item.link) === 'saved' ||
                  getSaveState(item.link) === 'duplicate'
                "
                @click="saveInsight(item)"
              >
                {{ getSaveButtonLabel(item) }}
              </button>
            </div>
            <p v-if="item.summary" class="news-summary">
              {{ item.summary }}
            </p>
            <div class="news-meta">
              <p v-if="getPublishedAt(item)" class="news-date">
                {{ formatDate(getPublishedAt(item)) }}
              </p>
              <p
                v-if="getSaveState(item.link) === 'saved'"
                class="save-status"
                role="status"
              >
                관심 뉴스로 저장되었습니다.
              </p>
              <p
                v-else-if="getSaveState(item.link) === 'duplicate'"
                class="save-status"
                role="status"
              >
                이미 저장된 뉴스입니다.
              </p>
              <p
                v-else-if="getSaveState(item.link) === 'error'"
                class="save-status save-status-error"
                role="alert"
              >
                저장하지 못했습니다. 다시 시도해 주세요.
              </p>
            </div>
          </li>
        </ul>
      </template>
    </section>

    <section class="insight-section" aria-labelledby="insight-heading">
      <div class="section-header">
        <div>
          <h2 id="insight-heading">저장한 인사이트</h2>
          <p class="updated-at">관심 뉴스로 저장한 항목을 모아 봅니다.</p>
        </div>
        <button
          type="button"
          class="refresh-button"
          :disabled="isInsightLoading"
          @click="refreshInsights"
        >
          {{ isInsightLoading ? "불러오는 중" : "목록 갱신" }}
        </button>
      </div>

      <div
        v-if="isInsightLoading && !hasInsightItems"
        class="state-panel"
        role="status"
        aria-live="polite"
      >
        <p class="state-title">저장한 인사이트를 불러오는 중입니다</p>
        <p class="state-description">
          백엔드에 남아 있는 저장 항목을 확인하고 있습니다.
        </p>
      </div>

      <div
        v-else-if="insightErrorMessage && !hasInsightItems"
        class="state-panel state-panel-error"
        role="alert"
        aria-live="assertive"
      >
        <p class="state-title">저장 목록을 표시할 수 없습니다</p>
        <p class="state-description">{{ insightErrorMessage }}</p>
        <button
          type="button"
          class="retry-button"
          :disabled="isInsightLoading"
          @click="refreshInsights"
        >
          다시 시도
        </button>
      </div>

      <div
        v-else-if="!hasInsightItems"
        class="state-panel"
        role="status"
        aria-live="polite"
      >
        <p class="state-title">아직 저장한 인사이트가 없습니다</p>
        <p class="state-description">
          최신 기술 뉴스에서 의미 있는 항목을 저장하면 이곳에 표시됩니다.
        </p>
      </div>

      <template v-else>
        <div
          v-if="insightErrorMessage"
          class="error-banner"
          role="alert"
          aria-live="assertive"
        >
          <p>{{ insightErrorMessage }}</p>
          <button
            type="button"
            class="retry-button"
            :disabled="isInsightLoading"
            @click="refreshInsights"
          >
            다시 시도
          </button>
        </div>

        <p
          v-if="isInsightLoading"
          class="inline-refresh-status"
          role="status"
          aria-live="polite"
        >
          저장 목록을 갱신하는 중입니다.
        </p>

        <ul class="insight-list">
          <li
            v-for="(insight, index) in insightItems"
            :key="insight.id || getNewsItemKey(insight, index)"
            class="insight-card"
          >
            <a
              :href="insight.link"
              target="_blank"
              rel="noreferrer"
              class="news-title"
            >
              {{ insight.title }}
            </a>
            <p v-if="insight.summary" class="news-summary">
              {{ insight.summary }}
            </p>
            <div class="news-meta">
              <p v-if="getPublishedAt(insight)" class="news-date">
                발행 {{ formatDate(getPublishedAt(insight)) }}
              </p>
              <p v-if="insight.createdAt || insight.created_at" class="news-date">
                저장 {{ formatDate(insight.createdAt || insight.created_at) }}
              </p>
              <p class="impact-badge">{{ insight.impact }}</p>
            </div>
          </li>
        </ul>
      </template>
    </section>
  </main>
</template>
