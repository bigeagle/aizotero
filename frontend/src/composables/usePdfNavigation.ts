import { ref } from 'vue';

export interface NavigationEntry {
  pageNumber: number;
  timestamp: number;
}

const MAX_HISTORY = 20;

export function usePdfNavigation() {
  const history = ref<NavigationEntry[]>([]);
  const currentIndex = ref(-1);
  const lastPage = ref(1);

  /** Track current page from scroll events (does NOT record history) */
  function trackPage(pageNumber: number) {
    lastPage.value = pageNumber;
  }

  /** Record a navigation jump (e.g. from clicking a link) */
  function recordJump(fromPage: number) {
    // Truncate forward history if we're not at the end
    if (currentIndex.value < history.value.length - 1) {
      history.value = history.value.slice(0, currentIndex.value + 1);
    }

    // Add new entry
    history.value.push({ pageNumber: fromPage, timestamp: Date.now() });

    // Limit history size
    if (history.value.length > MAX_HISTORY) {
      history.value.shift();
    } else {
      currentIndex.value++;
    }
  }

  function canGoBack() {
    return currentIndex.value >= 0;
  }

  function goBack(): number | null {
    if (!canGoBack()) return null;
    const entry = history.value[currentIndex.value];
    currentIndex.value--;
    return entry.pageNumber;
  }

  function reset() {
    history.value = [];
    currentIndex.value = -1;
    lastPage.value = 1;
  }

  return {
    history,
    currentIndex,
    lastPage,
    canGoBack,
    trackPage,
    recordJump,
    goBack,
    reset,
  };
}
