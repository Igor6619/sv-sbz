async function show_pdf(file){
    const viewer =  document.createElement('div');
    viewer.className = 'pdf-viewer';
    viewer.style.position = 'relative';
    viewer.style.height = '65vh';
    // viewer.style.overflow = 'auto';
    viewer.innerHTML = '';
    
    
    // ===== КОНТЕЙНЕР ДЛЯ СТРАНИЦ =====
    const pagesContainer = document.createElement('div');
    pagesContainer.style.height = '65vh';
    pagesContainer.style.overflow = 'auto';
    pagesContainer.style.display = 'flex';
    pagesContainer.style.flexDirection = 'column';
    // pagesContainer.style.alignItems = 'center';      // ← Центрирование по горизонтали
    pagesContainer.style.width = '100%';             // ← Занимает всю ширину viewer
    pagesContainer.style.padding = '20px';
    pagesContainer.style.gap = '10px';
    pagesContainer.style.boxSizing = 'border-box';   // ← Чтобы padding не добавлялся к ширине
    viewer.appendChild(pagesContainer);
     // ===== ПАНЕЛЬ УПРАВЛЕНИЯ =====
    const controlsPanel = document.createElement('div');
    // controlsPanel.style.position = 'sticky';
    controlsPanel.style.position = 'absolute';
    controlsPanel.style.bottom = '24px';
    // controlsPanel.style.right = '0';
    controlsPanel.style.marginLeft = 'auto';
    controlsPanel.style.right = '24px';
    controlsPanel.style.width = 'fit-content';
    controlsPanel.style.padding = '0';
    controlsPanel.style.backgroundColor = 'rgba(50, 50, 50, 0.3)';
    controlsPanel.style.borderRadius = '6px';
    controlsPanel.style.display = 'flex';
    controlsPanel.style.justifyContent = 'flex-end';
    controlsPanel.style.alignItems = 'center';
    controlsPanel.style.zIndex = '100';
    controlsPanel.style.boxSizing = 'border-box';
    // Кнопка полноэкранного режима
    const fullscreenBtn = document.createElement('button');
    fullscreenBtn.textContent = '⛶';
    fullscreenBtn.style.margin = '0 10px';
    fullscreenBtn.style.fontSize = '36px';
    fullscreenBtn.style.background = 'transparent';
    fullscreenBtn.style.border = 'none';
    fullscreenBtn.style.color = '#fff';
    fullscreenBtn.style.cursor = 'pointer';
    fullscreenBtn.title = 'Полноэкранный режим';

    controlsPanel.appendChild(fullscreenBtn);

    // viewer.appendChild(controlsPanel);
    viewer.appendChild(controlsPanel)

     // ===== УПРАВЛЕНИЕ ПОЛНОЭКРАННЫМ РЕЖИМОМ =====
    fullscreenBtn.addEventListener('click', toggleFullscreen);

    function toggleFullscreen() {
        const fullscreenElement = document.fullscreenElement;

        if (!fullscreenElement) {
            viewer.requestFullscreen().catch(err => {
                console.warn(`Не удалось войти в полноэкранный режим: ${err.message}`);
            });
        } else {
            document.exitFullscreen();
        }
    }

    // ✅ ОБРАБОТЧИК СМЕНЫ ПОЛНОЭКРАННОГО РЕЖИМА
    // Меняем размеры И viewer, И pagesContainer
    function onFullscreenChange() {
        if (document.fullscreenElement === viewer) {
            // === ВХОД в fullscreen ===
            viewer.style.height = '100vh';
            pagesContainer.style.height = '100vh';   // ← растягиваем контейнер страниц
            pagesContainer.style.padding = '40px';   // ← увеличиваем отступы (опционально)
            fullscreenBtn.title = 'Выйти из полноэкранного режима';
        } else {
            // === ВЫХОД из fullscreen ===
            viewer.style.height = '65vh';
            pagesContainer.style.height = '65vh';    // ← возвращаем исходную высоту
            pagesContainer.style.padding = '20px';   // ← возвращаем отступы
            fullscreenBtn.title = 'Полноэкранный режим';
        }
    }

    document.addEventListener('fullscreenchange', onFullscreenChange);

    // Инициализация PDF.js
    const pdf = await pdfjsLib.getDocument({ data: file }).promise;

        // Отображение страниц PDF
    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
        const page = await pdf.getPage(pageNumber);

        // Создание контейнера для страницы
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        const viewport = page.getViewport({ scale: 1.5 });

        canvas.width = viewport.width;
        canvas.height = viewport.height;

        // Рендеринг страницы
        await page.render({ canvasContext: context, viewport: viewport }).promise;

        // Добавление страницы в область просмотра
        const pageDiv = document.createElement('div');
        pageDiv.className = 'page';
        pageDiv.style.display = 'flex';
        pageDiv.style.justifyContent = 'center';         // ← Центрирование canvas внутри pageDiv
        pageDiv.style.width = '100%';                    // ← Занимает всю ширину pagesContainer
        pageDiv.style.flexShrink = '0';
        pageDiv.appendChild(canvas);
        // viewer.appendChild(pageDiv);
        pagesContainer.appendChild(pageDiv);
        }
    // viewer.className = 'document-iframe';

    return viewer
}