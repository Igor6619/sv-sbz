function show_xlsl(file){
    const viewer = document.createElement('div');
    viewer.id = 'model-viewer';
    viewer.style.backgroundColor = "#fff"
    viewer.style.position = 'relative';
    viewer.style.width = '100%';
    viewer.style.height = '70vh'; // ← ФИКСИРОВАННАЯ высота (не 100%!)
    viewer.style.overflow = 'auto'; // ← ОБЯЗАТЕЛЬНО: включаем прокрутку
    
    // ===== КОНТЕЙНЕР ДЛЯ СТРАНИЦ =====
    const pagesContainer = document.createElement('div');
    pagesContainer.style.display = 'flex';
    pagesContainer.style.flexDirection = 'column';
    pagesContainer.style.alignItems = 'center';      // ← Центрирование по горизонтали
    pagesContainer.style.width = '100%';             // ← Занимает всю ширину viewer
    pagesContainer.style.padding = '20px';
    pagesContainer.style.gap = '10px';
    pagesContainer.style.boxSizing = 'border-box';   // ← Чтобы padding не добавлялся к ширине
    
     // ===== ПАНЕЛЬ УПРАВЛЕНИЯ =====
    const controlsPanel = document.createElement('div');
    controlsPanel.style.position = 'sticky';
    controlsPanel.style.top = '24px';
    // controlsPanel.style.right = '0';
    controlsPanel.style.marginRight = '24px';
    controlsPanel.style.marginLeft = 'auto';
    controlsPanel.style.width = 'fit-content';
    controlsPanel.style.padding = '0';
    controlsPanel.style.backgroundColor = 'rgba(50, 50, 50, 0.3)';
    controlsPanel.style.borderRadius = '6px';
    controlsPanel.style.display = 'flex';
    controlsPanel.style.justifyContent = 'flex-end';
    controlsPanel.style.alignItems = 'center';
    controlsPanel.style.zIndex = '100';
    controlsPanel.style.boxSizing = 'border-box';
    controlsPanel.style.flexShrink = '0'; // ← Запрещаем сжатие
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
    viewer.appendChild(controlsPanel);
    viewer.appendChild(pagesContainer);
    
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
    // function onFullscreenChange() {
    //     const isFullscreen = !!document.fullscreenElement;

    //     if (isFullscreen) {
    //         viewer.style.height = '100vh';
    //         viewer.style.overflowY = 'auto' // ← В полном экране: вся высота экрана
    //     }
    //     else {
    //     //     viewer.style.height = '70vh'; // ← В обычном режиме: 70% высоты
    //     }
    // }
    // Работаем напрямую с ArrayBuffer
    const data = new Uint8Array(file);
    const workbook = XLSX.read(data, { type: 'array' });

    // Перебираем все листы
    workbook.SheetNames.forEach(sheetName => {
        const sheet = workbook.Sheets[sheetName];
        // Добавляем заголовок для листа
        const titleDiv = document.createElement('div');
        titleDiv.className = 'sheet-title';
        titleDiv.innerText = `Лист: ${sheetName}`;
        pagesContainer.appendChild(titleDiv);

        // Преобразуем данные в HTML-таблицу
        const htmlTable = XLSX.utils.sheet_to_html(sheet);

        // Добавляем таблицу в вывод
        const tableDiv = document.createElement('div');
        tableDiv.innerHTML = htmlTable;
        pagesContainer.appendChild(tableDiv);
    });
    return viewer
}