<script setup>
import { computed, onMounted, ref } from "vue";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
const newsItems = ref([]);
const savedNewsItems = ref([]);
const cachedAt = ref("");
const errorMessage = ref("");
const savedNewsErrorMessage = ref("");
const isLoading = ref(false);
const isSavedNewsLoading = ref(false);
const currentView = ref("news");
const saveStates = ref({});
const deleteStates = ref({});
const selectedNewsItem = ref(null);
const insightDraft = ref({
  impact: "Medium",
  interpretation: "",
  action: "",
});
const hasNewsItems = computed(() => newsItems.value.length > 0);
const hasSavedNewsItems = computed(() => savedNewsItems.value.length > 0);
const isInsightComposerOpen = computed(() => selectedNewsItem.value !== null);
const isNewsView = computed(() => currentView.value === "news");
const isMyLensView = computed(() => currentView.value === "myLens");
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

async function refreshSavedNews() {
  isSavedNewsLoading.value = true;
  savedNewsErrorMessage.value = "";

  try {
    const response = await fetch(`${apiBaseUrl}/api/saved-news`);
    if (!response.ok) {
      throw new Error(`Failed to fetch saved news: ${response.status}`);
    }

    const data = await response.json();
    savedNewsItems.value = data.items ?? [];
    syncSaveStatesFromSavedNews();
  } catch (error) {
    console.error("내 저장 목록을 불러오지 못했습니다.", error);
    savedNewsErrorMessage.value =
      "내 저장 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
  } finally {
    isSavedNewsLoading.value = false;
  }
}

onMounted(() => {
  refreshNews();
  refreshSavedNews();
});

function showNewsView() {
  currentView.value = "news";
}

function showMyLensView() {
  currentView.value = "myLens";
  refreshSavedNews();
}

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

function getInsightId(insight) {
  return insight.id ?? "";
}

function getDeleteState(insight) {
  return deleteStates.value[getInsightId(insight)] ?? "idle";
}

function setSaveState(link, state) {
  saveStates.value = {
    ...saveStates.value,
    [link]: state,
  };
}

function setDeleteState(insight, state) {
  const insightId = getInsightId(insight);
  if (!insightId) {
    return;
  }

  deleteStates.value = {
    ...deleteStates.value,
    [insightId]: state,
  };
}

function clearDeleteState(insight) {
  const insightId = getInsightId(insight);
  if (!insightId) {
    return;
  }

  const nextDeleteStates = { ...deleteStates.value };
  delete nextDeleteStates[insightId];
  deleteStates.value = nextDeleteStates;
}

function syncSaveStatesFromSavedNews() {
  const nextSaveStates = {};

  for (const [link, state] of Object.entries(saveStates.value)) {
    if (state === "saving" || state === "error") {
      nextSaveStates[link] = state;
    }
  }

  for (const savedNews of savedNewsItems.value) {
    if (savedNews.link) {
      nextSaveStates[savedNews.link] = "saved";
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

function openInsightComposer(item) {
  const currentState = getSaveState(item.link);
  if (currentState === "saving" || finalSaveStates.includes(currentState)) {
    return;
  }

  if (currentState === "error") {
    setSaveState(item.link, "idle");
  }

  selectedNewsItem.value = item;
  insightDraft.value = {
    impact: "Medium",
    interpretation: "",
    action: "",
  };
}

function closeInsightComposer() {
  if (
    selectedNewsItem.value &&
    getSaveState(selectedNewsItem.value.link) === "saving"
  ) {
    return;
  }

  selectedNewsItem.value = null;
}

async function saveInsight() {
  const item = selectedNewsItem.value;
  if (!item) {
    return;
  }

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
        interpretation: insightDraft.value.interpretation.trim(),
        impact: insightDraft.value.impact,
        action: insightDraft.value.action.trim(),
      }),
    });

    if (response.status === 409) {
      setSaveState(item.link, "duplicate");
      await refreshSavedNews();
      closeInsightComposer();
      return;
    }

    if (!response.ok) {
      throw new Error(`Failed to save insight: ${response.status}`);
    }

    setSaveState(item.link, "saved");
    await refreshSavedNews();
    closeInsightComposer();
  } catch (error) {
    console.error("관심 뉴스를 저장하지 못했습니다.", error);
    setSaveState(item.link, "error");
  }
}

async function deleteSavedInsight(insight) {
  const insightId = getInsightId(insight);
  if (!insightId || getDeleteState(insight) === "deleting") {
    return;
  }

  setDeleteState(insight, "deleting");

  try {
    const response = await fetch(`${apiBaseUrl}/api/insights/${insightId}`, {
      method: "DELETE",
    });

    if (!response.ok && response.status !== 404) {
      throw new Error(`Failed to delete insight: ${response.status}`);
    }

    clearDeleteState(insight);
    savedNewsItems.value = savedNewsItems.value.filter(
      (item) => getInsightId(item) !== insightId,
    );
    syncSaveStatesFromSavedNews();
    await refreshSavedNews();
  } catch (error) {
    console.error("저장한 인사이트를 삭제하지 못했습니다.", error);
    setDeleteState(insight, "error");
  }
}
</script>

<template>
  <main class="app-shell">
    <header class="page-header">
      <div class="page-header-top">
        <div>
          <p class="eyebrow">GeekNews Insight Tracker</p>
          <h1>ChangeLens</h1>
        </div>
        <button
          v-if="isNewsView"
          type="button"
          class="view-button"
          @click="showMyLensView"
        >
          My Lens
        </button>
        <button
          v-else
          type="button"
          class="view-button"
          @click="showNewsView"
        >
          최신 뉴스
        </button>
      </div>
      <p v-if="isNewsView" class="description">
        GeekNews 최신 글을 확인하고, 나에게 의미 있는 기술 변화를 기록합니다.
      </p>
      <p v-else class="description">
        저장한 뉴스와 직접 작성한 인사이트를 다시 확인합니다.
      </p>
    </header>

    <section
      v-if="isNewsView"
      class="news-section"
      aria-labelledby="news-heading"
    >
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
                @click="openInsightComposer(item)"
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

    <section
      v-if="isMyLensView"
      class="saved-section"
      aria-labelledby="saved-heading"
    >
      <div class="section-header">
        <div>
          <h2 id="saved-heading">내 저장 목록</h2>
          <p class="updated-at">
            저장한 뉴스와 작성한 인사이트를 함께 확인합니다.
          </p>
        </div>
        <button
          type="button"
          class="refresh-button"
          :disabled="isSavedNewsLoading"
          @click="refreshSavedNews"
        >
          {{ isSavedNewsLoading ? "불러오는 중" : "목록 갱신" }}
        </button>
      </div>

      <div
        v-if="isSavedNewsLoading && !hasSavedNewsItems"
        class="state-panel"
        role="status"
        aria-live="polite"
      >
        <p class="state-title">내 저장 목록을 불러오는 중입니다</p>
        <p class="state-description">
          저장한 뉴스와 인사이트를 함께 확인하고 있습니다.
        </p>
      </div>

      <div
        v-else-if="savedNewsErrorMessage && !hasSavedNewsItems"
        class="state-panel state-panel-error"
        role="alert"
        aria-live="assertive"
      >
        <p class="state-title">저장 목록을 표시할 수 없습니다</p>
        <p class="state-description">{{ savedNewsErrorMessage }}</p>
        <button
          type="button"
          class="retry-button"
          :disabled="isSavedNewsLoading"
          @click="refreshSavedNews"
        >
          다시 시도
        </button>
      </div>

      <div
        v-else-if="!hasSavedNewsItems"
        class="state-panel"
        role="status"
        aria-live="polite"
      >
        <p class="state-title">아직 저장한 뉴스가 없습니다</p>
        <p class="state-description">
          최신 기술 뉴스에서 인사이트를 작성해 저장하면 이곳에 표시됩니다.
        </p>
      </div>

      <template v-else>
        <div
          v-if="savedNewsErrorMessage"
          class="error-banner"
          role="alert"
          aria-live="assertive"
        >
          <p>{{ savedNewsErrorMessage }}</p>
          <button
            type="button"
            class="retry-button"
            :disabled="isSavedNewsLoading"
            @click="refreshSavedNews"
          >
            다시 시도
          </button>
        </div>

        <p
          v-if="isSavedNewsLoading"
          class="inline-refresh-status"
          role="status"
          aria-live="polite"
        >
          저장 목록을 갱신하는 중입니다.
        </p>

        <ul class="saved-list">
          <li
            v-for="(insight, index) in savedNewsItems"
            :key="insight.id || getNewsItemKey(insight, index)"
            class="saved-card"
          >
            <div class="saved-card-header">
              <a
                :href="insight.link"
                target="_blank"
                rel="noreferrer"
                class="news-title"
              >
                {{ insight.title }}
              </a>
              <button
                type="button"
                class="delete-button"
                :class="{
                  'delete-button-error': getDeleteState(insight) === 'error',
                }"
                :aria-label="`저장한 인사이트 삭제: ${insight.title || '제목 없음'}`"
                :disabled="getDeleteState(insight) === 'deleting'"
                @click="deleteSavedInsight(insight)"
              >
                {{ getDeleteState(insight) === "deleting" ? "삭제 중" : "삭제" }}
              </button>
            </div>
            <p v-if="insight.summary" class="news-summary">
              {{ insight.summary }}
            </p>
            <dl
              v-if="insight.insight || insight.action"
              class="insight-detail-list"
            >
              <div v-if="insight.insight" class="insight-detail">
                <dt>해석</dt>
                <dd>{{ insight.insight }}</dd>
              </div>
              <div v-if="insight.action" class="insight-detail">
                <dt>다음 행동</dt>
                <dd>{{ insight.action }}</dd>
              </div>
            </dl>
            <div class="news-meta">
              <p v-if="getPublishedAt(insight)" class="news-date">
                발행 {{ formatDate(getPublishedAt(insight)) }}
              </p>
              <p v-if="insight.savedAt || insight.saved_at" class="news-date">
                저장 {{ formatDate(insight.savedAt || insight.saved_at) }}
              </p>
              <p class="impact-badge">{{ insight.impact }}</p>
              <p
                v-if="getDeleteState(insight) === 'error'"
                class="save-status save-status-error"
                role="alert"
              >
                삭제하지 못했습니다. 다시 시도해 주세요.
              </p>
            </div>
          </li>
        </ul>
      </template>
    </section>
  </main>

  <div
    v-if="isInsightComposerOpen"
    class="modal-backdrop"
  >
    <form
      class="insight-form"
      role="dialog"
      aria-modal="true"
      aria-labelledby="insight-form-title"
      @submit.prevent="saveInsight"
      @keydown.escape="closeInsightComposer"
    >
      <div class="insight-form-header">
        <div>
          <p class="form-eyebrow">관심 뉴스 저장</p>
          <h2 id="insight-form-title">인사이트 작성</h2>
        </div>
        <button
          type="button"
          class="modal-close-button"
          :disabled="getSaveState(selectedNewsItem.link) === 'saving'"
          aria-label="닫기"
          @click="closeInsightComposer"
        >
          ×
        </button>
      </div>

      <p class="form-news-title">{{ selectedNewsItem.title }}</p>

      <label class="field">
        <span>영향도</span>
        <select v-model="insightDraft.impact" class="field-control">
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
        </select>
      </label>

      <label class="field">
        <span>해석</span>
        <textarea
          v-model="insightDraft.interpretation"
          class="field-control"
          rows="4"
          placeholder="이 뉴스가 나에게 어떤 의미인지 적어보세요."
        />
      </label>

      <label class="field">
        <span>다음 행동</span>
        <textarea
          v-model="insightDraft.action"
          class="field-control"
          rows="3"
          placeholder="읽고 나서 확인하거나 시도할 일을 적어보세요."
        />
      </label>

      <p
        v-if="getSaveState(selectedNewsItem.link) === 'error'"
        class="save-status save-status-error"
        role="alert"
      >
        저장하지 못했습니다. 다시 시도해 주세요.
      </p>

      <div class="form-actions">
        <button
          type="button"
          class="secondary-button"
          :disabled="getSaveState(selectedNewsItem.link) === 'saving'"
          @click="closeInsightComposer"
        >
          취소
        </button>
        <button
          type="submit"
          class="primary-button"
          :disabled="getSaveState(selectedNewsItem.link) === 'saving'"
        >
          {{
            getSaveState(selectedNewsItem.link) === "saving"
              ? "저장 중"
              : "저장"
          }}
        </button>
      </div>
    </form>
  </div>
</template>
