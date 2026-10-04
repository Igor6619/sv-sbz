// ============ СОСТОЯНИЕ ============
let allSuggestionsCache = [];
let cacheTimestamp = 0;
const CACHE_TTL = 24 * 60 * 60 * 1000; // сутки

let currentSuggestions = [];      // Текущий отфильтрованный список
let activeIndex = -1;             // Индекс выбранного элемента (-1 = ничего)
let debounceTimer = null;

// ============ DOM ЭЛЕМЕНТЫ ============
const input = document.getElementById('search-input');
const list = document.getElementById('suggestions-list');
const search_button = document.querySelector('.search-button');

// ============ ЗАГРУЗКА КЭША ============
async function loadAllSuggestions() {
    // Проверяем localStorage
    const cached = localStorage.getItem('suggestions_cache');
    const timestamp = parseInt(localStorage.getItem('suggestions_timestamp') || '0');

    if (cached && Date.now() - timestamp < CACHE_TTL) {
        allSuggestionsCache = JSON.parse(cached);
        cacheTimestamp = timestamp;
        return;
    }

    try {
        const response = await fetch('/api/search_queries/get_search_queries');
        if (!response.ok) throw new Error('Failed to load');

        allSuggestionsCache = await response.json();
        cacheTimestamp = Date.now();

        // Сохраняем в localStorage
        localStorage.setItem('suggestions_cache', JSON.stringify(allSuggestionsCache));
        localStorage.setItem('suggestions_timestamp', cacheTimestamp.toString());
    } catch (error) {
        console.error('Ошибка загрузки подсказок:', error);
        // Если есть старый кэш - используем его
        if (cached) {
            allSuggestionsCache = JSON.parse(cached);
        }
    }
}

// ============ ФИЛЬТРАЦИЯ ============
function filterSuggestions(query, limit = 5) {
    const normalized = query.trim().toLowerCase();

    if (normalized.length < 2) {
        return [];
    }

    return allSuggestionsCache
        .filter(s => s && typeof s.value === 'string' && s.value.length > 0)
        .filter(s => s.value.toLowerCase().includes(normalized))
        .sort((a, b) => {
            // Приоритет 1: начинается с запроса (UX - точное совпадение в начале)
            const aStarts = a.value.toLowerCase().startsWith(normalized) ? 1 : 0;
            const bStarts = b.value.toLowerCase().startsWith(normalized) ? 1 : 0;
            if (aStarts !== bStarts) return bStarts - aStarts;

            // Приоритет 2: сколько раз искали этот запрос (по убыванию)
            const aCount = a.count || 0;
            const bCount = b.count || 0;
            if (aCount !== bCount) return bCount - aCount;

            // Приоритет 3: сколько материалов найдено (по убыванию)
            const aResults = a.results_count || 0;
            const bResults = b.results_count || 0;
            if (aResults !== bResults) return bResults - aResults;

            // Приоритет 4: алфавитный порядок (для стабильности)
            return a.value.localeCompare(b.value, 'ru');
        })
        .slice(0, limit);
}

// ============ ПОДСВЕТКА СОВПАДЕНИЙ ============
function highlightMatch(text, query) {
    const normalizedQuery = query.trim();
    if (!normalizedQuery) return escapeHtml(text);

    // Ищем позицию вхождения (без учета регистра)
    const lowerText = text.toLowerCase();
    const lowerQuery = normalizedQuery.toLowerCase();
    const index = lowerText.indexOf(lowerQuery);

    if (index === -1) return escapeHtml(text);

    const before = escapeHtml(text.slice(0, index));
    const match = escapeHtml(text.slice(index, index + normalizedQuery.length));
    const after = escapeHtml(text.slice(index + normalizedQuery.length));

    return `${before}<mark>${match}</mark>${after}`;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ============ ОТОБРАЖЕНИЕ ПОДСКАЗОК ============
function pluralizeMaterial(n) {
    const abs = Math.abs(n) % 100;
    const lastDigit = abs % 10;

    if (abs > 10 && abs < 20) {
        return 'материалов';
    }
    if (lastDigit === 1) {
        return 'материал';
    }
    if (lastDigit >= 2 && lastDigit <= 4) {
        return 'материала';
    }
    return 'материалов';
}

function showSuggestions(suggestions, query) {
    currentSuggestions = suggestions;
    activeIndex = -1; // Сбрасываем активный элемент

    // Если пусто - скрываем список
    if (!suggestions || suggestions.length === 0) {
        hideSuggestions();
        return;
    }

    // Очищаем список
    list.innerHTML = '';

    // Создаем элементы
    suggestions.forEach((suggestion, index) => {
        const li = document.createElement('li');
        li.setAttribute('role', 'option');
        li.setAttribute('data-index', index);
        li.id = `suggestion-${index}`;

        // Подсвечиваем совпадение (используем suggestion.value)
        const querySpan = document.createElement('span');
        querySpan.className = 'query-text';
        querySpan.innerHTML = highlightMatch(suggestion.value, query);

        // Счетчик использований с правильным склонением
        const countSpan = document.createElement('span');
        countSpan.className = 'count';
        const count = suggestion.results_count || 0;
        const word = pluralizeMaterial(count);
        countSpan.textContent = `${count} ${word} искали ${suggestion.count} раз(-а)`;

        li.appendChild(querySpan);
        li.appendChild(countSpan);

        // Обработчик клика (используем suggestion.value)
        li.addEventListener('click', () => {
            selectSuggestion(suggestion.value);
        });

        li.addEventListener('mouseenter', () => {
            setActiveItem(index);
        });

        list.appendChild(li);
    });

    // Обновляем ARIA
    input.setAttribute('aria-activedescendant', '');

    // Показываем список
    list.classList.add('visible');
}

function hideSuggestions() {
    list.classList.remove('visible');
    list.innerHTML = '';
    currentSuggestions = [];
    activeIndex = -1;
}

// ============ УПРАВЛЕНИЕ АКТИВНЫМ ЭЛЕМЕНТОМ ============
function setActiveItem(index) {
    // Убираем active со всех
    const items = list.querySelectorAll('li');
    items.forEach(item => item.classList.remove('active'));

    // Если индекс валидный - активируем
    if (index >= 0 && index < items.length) {
        activeIndex = index;
        items[index].classList.add('active');
        input.setAttribute('aria-activedescendant', `suggestion-${index}`);

        // Прокручиваем, если элемент не виден
        items[index].scrollIntoView({ block: 'nearest' });
    } else {
        activeIndex = -1;
        input.setAttribute('aria-activedescendant', '');
    }
}

// ============ ВЫБОР ПОДСКАЗКИ ============
function selectSuggestion(text) {
    input.value = text;
    hideSuggestions();
    input.focus();
    search_button.click();
}

// ============ ОБРАБОТЧИКИ СОБЫТИЙ ============

// Ввод текста
input.addEventListener('input', (e) => {
    const query = e.target.value;

    clearTimeout(debounceTimer);

    if (query.trim().length < 2) {
        hideSuggestions();
        return;
    }

    // Debounce 200ms
    debounceTimer = setTimeout(() => {
        const suggestions = filterSuggestions(query);
        showSuggestions(suggestions, query);
    }, 200);
});

// Клавиатурная навигация
input.addEventListener('keydown', (e) => {
    if (!list.classList.contains('visible') || currentSuggestions.length === 0) {
        return;
    }

    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            // Двигаемся вниз, циклически
            const nextIndex = activeIndex < currentSuggestions.length - 1
                ? activeIndex + 1
                : 0;
            setActiveItem(nextIndex);
            break;

        case 'ArrowUp':
            e.preventDefault();
            // Двигаемся вверх, циклически
            const prevIndex = activeIndex > 0
                ? activeIndex - 1
                : currentSuggestions.length - 1;
            setActiveItem(prevIndex);
            break;

        case 'Enter':
            e.preventDefault();
            if (activeIndex >= 0) {
                // Выбран элемент - используем его
                selectSuggestion(currentSuggestions[activeIndex].value);
            } else {
                // Ничего не выбрано - обычный поиск
                search_button.click();
            }
            break;

        case 'Escape':
            hideSuggestions();
            break;

        case 'Tab':
            hideSuggestions();
            break;
    }
});

// Закрытие при клике вне области
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-form')) {
        hideSuggestions();
    }
});

// Показ при фокусе (если есть текст)
input.addEventListener('focus', () => {
    if (input.value.trim().length >= 2) {
        const suggestions = filterSuggestions(input.value);
        showSuggestions(suggestions, input.value);
    }
});

// ============ ИНИЦИАЛИЗАЦИЯ ============
loadAllSuggestions();