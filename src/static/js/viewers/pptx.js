function show_pptx(fileBuffer) {
    // Создаем контейнер для презентации
    const viewer = document.createElement('div');
    viewer.id = 'pptx-viewer';
    viewer.style.width = '100%';
    viewer.style.height = '70vh';
    viewer.style.backgroundColor = '#f5f5f5';
    viewer.style.overflow = 'auto';
    viewer.style.position = 'relative';

    // Создаем элемент для отображения презентации
    const resultDiv = document.createElement('div');
    resultDiv.id = 'pptx-result';
    resultDiv.style.width = '100%';
    resultDiv.style.height = '100%';
    viewer.appendChild(resultDiv);

    // Инициализируем презентацию
    try {
        // так как работает всё равно не стабильно тупо ... выкидываем в ошибку
        // throw new Error('Выкидываем до того момента пока разберемся');
        // Преобразуем ArrayBuffer в Blob
        const blob = new Blob([fileBuffer], {
            type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        });
        const url = URL.createObjectURL(blob);


        
        // Проверяем, загружена ли библиотека
        if (typeof $.fn.pptxToHtml === 'undefined') {
            throw new Error('Библиотека pptxjs не загружена');
        }

        // // Преобразуем ArrayBuffer в Base64 Data URL
        // const base64 = arrayBufferToBase64(fileBuffer);
        // const dataUrl = `data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,${base64}`;


        // Инициализируем PPTX.js
        $(resultDiv).pptxToHtml({
            pptxFileUrl: url,
            // pptxFileUrl: dataUrl,
            slideMode: true,
            keyBoardShortCut: false,
            slideModeConfig: {
                first: 1,
                nav: true,
                navTxtColor: "black",
                navNextTxt: "›",
                navPrevTxt: "‹",
                showPlayPauseBtn: true,
                keyBoardShortCut: false,
                showSlideNum: true,
                showTotalSlideNum: true,
                autoSlide: false,
                randomAutoSlide: false,
                loop: false,
                background: "white",
                transition: "default",
                transitionTime: 0.5
            }
        });

        // Добавляем кнопку полноэкранного режима
        const fullscreenBtn = document.createElement('button');
        fullscreenBtn.textContent = '⛶';
        fullscreenBtn.style.position = 'absolute';
        fullscreenBtn.style.top = '10px';
        fullscreenBtn.style.right = '10px';
        fullscreenBtn.style.zIndex = '1000';
        fullscreenBtn.style.padding = '5px 10px';
        fullscreenBtn.style.backgroundColor = '#ffffff';
        fullscreenBtn.style.border = '1px solid #ccc';
        fullscreenBtn.style.borderRadius = '3px';
        fullscreenBtn.style.cursor = 'pointer';

        fullscreenBtn.addEventListener('click', function() {
            $(resultDiv).toggleFullScreen();
        });

        viewer.appendChild(fullscreenBtn);

    } catch (error) {
        console.error('Error loading PPTX:', error);
        resultDiv.innerHTML = '<p>Не удалось загрузить презентацию. Пожалуйста, скачайте файл для просмотра.</p>';
    }

    return viewer;
}