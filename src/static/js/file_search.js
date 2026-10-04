async function createFileViewer(body, fileData) {
    // Очищаем предыдущий контент
    body.innerHTML = `
        <p>Загрузка контента</p>
    `;

    // Определяем способ отображения по расширению файла
    if (isImage(fileData.ext) && fileData.is_360) {
        // Для изображений
        const response = await fetch(fileData.url)
        if (!response.ok) throw new Error('Failed to load FILE');
        const file = await response.arrayBuffer();
        if (!file) return;
        body.innerHTML = '';
        body.appendChild(await show_360_image(file));
    }
    else if (isImage(fileData.ext)) {
        // Для изображений
        // 1. Создаем контейнер-обертку для изображения и кнопки
        const imageWrapper = document.createElement('div');
        imageWrapper.style.position = 'relative';
        imageWrapper.style.display = 'block';          // ← было inline-block
        imageWrapper.style.width = 'fit-content';      // ← подстраивается под размер картинки
        imageWrapper.style.maxWidth = '100%';          // ← не вылезет за пределы родителя
        imageWrapper.style.margin = '0 auto';
        imageWrapper.style.maxHeight = '70vh';
        imageWrapper.style.lineHeight = '0'; // Убираем возможные лишние отступы снизу у inline-block
        
        // 2. Создаем само изображение
        const viewer = document.createElement('img');
        viewer.id = 'model-viewer';
        viewer.style.height = '65vh';
        viewer.src = fileData.url;
        viewer.alt = fileData.name;
        viewer.className = 'modal-image';
        

        body.innerHTML = '';
        // body.appendChild(viewer);
        // ===== КНОПКА ПОЛНОЭКРАННОГО РЕЖИМА (слева) =====
        const fullscreenBtn = document.createElement('button');
        fullscreenBtn.textContent = '⛶';
        fullscreenBtn.style.position = 'absolute';
        fullscreenBtn.style.bottom = '24px';
        fullscreenBtn.style.right = '24px';
        fullscreenBtn.style.zIndex = '101';
        fullscreenBtn.style.fontSize = '24px';
        fullscreenBtn.style.background = 'rgba(50, 50, 50, 0.3)';
        fullscreenBtn.style.border = 'none';
        fullscreenBtn.style.borderRadius = '6px';
        fullscreenBtn.style.color = '#fff';
        fullscreenBtn.style.cursor = 'pointer';
        fullscreenBtn.style.padding = '8px 12px';
        fullscreenBtn.style.lineHeight = '1';
        fullscreenBtn.style.transition = 'background 0.2s';
        fullscreenBtn.title = 'Полноэкранный режим';

        // 4. Собираем всё вместе
        imageWrapper.appendChild(viewer);
        imageWrapper.appendChild(fullscreenBtn);
        body.innerHTML = '';
        body.appendChild(imageWrapper); // Добавляем в body именно обертку
        
         // ===== УПРАВЛЕНИЕ ПОЛНОЭКРАННЫМ РЕЖИМОМ =====
        fullscreenBtn.addEventListener('click', toggleFullscreen);
        function toggleFullscreen() {
            // Проверяем, находимся ли мы уже в полноэкранном режиме
        
            const fullscreenElement = document.fullscreenElement ;
            if (!fullscreenElement) {
                // Входим в полноэкранный режим
                imageWrapper.requestFullscreen();
                
            } else {
                // Выходим из полноэкранного режима
                document.exitFullscreen();
                
            }
        }
        // ===== ОБРАБОТЧИК СМЕНЫ ПОЛНОЭКРАННОГО РЕЖИМА =====
        function onFullscreenChange() {
            if (document.fullscreenElement === imageWrapper) {
                // === ВХОД в полноэкранный режим ===
                // Растягиваем обертку на весь экран
                
                imageWrapper.style.display = 'flex';
                imageWrapper.style.alignItems = 'center';
                imageWrapper.style.justifyContent = 'center';
                imageWrapper.style.width = '100vw';
                imageWrapper.style.height = '100vh';
                imageWrapper.style.maxHeight = 'none';
                imageWrapper.style.background = '#000'; // черный фон для красоты

                // Растягиваем картинку, сохраняя пропорции
                viewer.style.height = '100vh';
                viewer.style.maxWidth = '100vw';
                viewer.style.objectFit = 'contain'; // важно: вписать с сохранением пропорций

                fullscreenBtn.title = 'Выйти из полноэкранного режима';
            } else {
                // === ВЫХОД из полноэкранного режима ===
                // Полностью сбрасываем все inline-стили обёртки
                imageWrapper.removeAttribute('style');
                // Возвращаем исходные стили
                imageWrapper.style.position = 'relative';
                imageWrapper.style.display = 'block';          // ← было inline-block
                imageWrapper.style.width = 'fit-content';      // ← подстраивается под размер картинки
                imageWrapper.style.maxWidth = '100%';          // ← не вылезет за пределы родителя
                imageWrapper.style.margin = '0 auto';
                imageWrapper.style.maxHeight = '70vh';
                imageWrapper.style.lineHeight = '0'; // Убираем возможные лишние отступы снизу у inline-block
                // imageWrapper.style.border = '1px solid red';

                // Полностью сбрасываем все inline-стили картинки
                viewer.removeAttribute('style');
                // Возвращаем исходные стили
                viewer.id = 'model-viewer';
                viewer.style.height = '65vh';
                viewer.src = fileData.url;
                viewer.alt = fileData.name;
                viewer.className = 'modal-image';

                fullscreenBtn.title = 'Полноэкранный режим';    
            }
        }

        document.addEventListener('fullscreenchange', onFullscreenChange);
    }

    else if (isVideo(fileData.ext) && fileData.is_360) {
        // Для видео - 360

        const response = await fetch(fileData.url)
        if (!response.ok) throw new Error('Failed to load FILE');
        const file = await response.arrayBuffer();
        if (!file) return;

        body.innerHTML = '';
        body.appendChild(await show_360_video(file));
    }
    else if (isVideo(fileData.ext)) {
        // Для видео
        const video = document.createElement('video');
        video.controls = true;
        video.className = 'modal-video';

        const source = document.createElement('source');
        source.src = fileData.url;
        source.type = getVideoMimeType(fileData.ext);

        console.log(source.type)
        console.log(fileData.url)

        video.appendChild(source);
        video.appendChild(document.createTextNode('Ваш браузер не поддерживает видео.'));

        body.innerHTML = '';
        body.appendChild(video);
    }
    // else if (isPdf(fileData.ext)) {
    //     // Для PDF
        
    //     const response = await fetch(fileData.url)
    //     if (!response.ok) throw new Error('Failed to load FILE');
    //     const file = await response.arrayBuffer();
    //     if (!file) return;

    //     body.innerHTML = '';
    //     body.appendChild(await show_pdf(file));
    // }
    else if (is3D(fileData.ext)) {
        // Для 3D моделей (GLB/GLTF)
        const response = await fetch(fileData.url);
        if (!response.ok) throw new Error('Failed to load 3D model');
        const file = await response.arrayBuffer();
        if (!file) return;

        body.innerHTML = '';
        body.appendChild(await show_glb(file));
    }
    else if (isAudio(fileData.ext)) {
        // Для аудио - создаем кастомный плеер
        body.innerHTML = '';
        body.appendChild(createAudioPlayer(fileData));
    }
    // else if (isTableDoc(fileData.ext)) {
    //     const response = await fetch(fileData.url);
    //     if (!response.ok) throw new Error('Failed to load FILE');
    //     const file = await response.arrayBuffer();
    //     if (!file) return;

    //     body.innerHTML = '';
    //     body.appendChild(show_xlsl(file))
    // }
    // else if (isPresentation(fileData.ext)) {
    //     const response = await fetch(fileData.url);
    //     if (!response.ok) throw new Error('Failed to load FILE');
    //     const fileBuffer = await response.arrayBuffer();
    //     if (!fileBuffer) return;

    //     // Передаём ArrayBuffer в функцию
    //     body.innerHTML = '';
    //     body.appendChild(show_pptx(fileBuffer));
    //     //  body.innerHTML = `
    //     //     <div class="office-preview">
    //     //         <div class="office-icon">
    //     //             ${getOfficeIcon(fileData.ext)}
    //     //         </div>
    //     //         <p>Для просмотра этого документа скачайте файл</p>
    //     //         <p class="file-info">${fileData.name}.${fileData.ext}</p>
    //     //     </div>
    //     // `;
    // }
    // // ///////////////////////////////////////////////////////////////////////
    // else if (isOfficeDocument(fileData.ext)) {
    //     // 1. Очищаем содержимое контейнера, как вы и делали
    //     body.innerHTML = '';

    //     // 2. Ссылка на локальный контейнер Collabora
    //     const collaboraUrl = "http://localhost:9980"; 
        
    //     // 3. Ссылка на ваш FastAPI для Collabora (используем host.docker.internal)
    //     // Убедитесь, что fileData.id содержит UUID файла
    //     const wopiSrc = encodeURIComponent(`http://docker.internal{fileData.id}`);
        
    //     // 4. Формируем финальный URL для фрейма
    //     const viewerUrl = `${collaboraUrl}/browser/dist/cool.html?WOPISrc=${wopiSrc}`;

    //     // 5. Создаем элемент iframe динамически
    //     const iframe = document.createElement('iframe');
    //     iframe.src = viewerUrl;
    //     iframe.style.width = '100%';
    //     iframe.style.height = '600px'; // Или любая удобная вам высота
    //     iframe.style.border = 'none';
    //     iframe.id = 'collabora-iframe';

    //     // 6. Добавляем iframe на страницу вместо старого просмотрщика Excel
    //     body.appendChild(iframe);
    // }

    // ///////////////////////////////////////////////////////////////////////////////////////
    // else if (isOfficeDocument(fileData.ext)) {
    //     // Для документов Office показываем сообщение
    //     body.innerHTML = `
    //         <div class="office-preview">
    //             <div class="office-icon">
    //                 ${getOfficeIcon(fileData.ext)}
    //             </div>
    //             <p>Для просмотра этого документа скачайте файл </p>
    //             <p class="file-info">${fileData.name}.${fileData.ext}</p>
    //         </div>
    //     `;
    // }
    else if (isOfficeDocument(fileData.ext)) {
       
        // Получаем ID файла из URL скачивания (вытаскиваем UUID из строки типа /api/files/UUID/download)
        // Если у вас в fileData есть прямой доступ к ID (например, fileData.id), лучше использовать его
        const urlParts = fileData.url.split('/');
        const fileId = urlParts[urlParts.length - 2]; // Обычно ID идет перед /download
        console.log('fileId: ', fileId)
        // Вместо текста заглушки вставляем iframe, который ссылается на наш новый эндпоинт конвертации
        body.innerHTML = `
            <div class="office-preview" style="width: 100%; height: 100%; min-height: 750px;">
                
                <iframe 
                    src="/api/files/${fileId}/pdf" 
                    style="width: 100%; height: 100%; min-height: 750px; border: none;"
                    allowfullscreen>
                </iframe>
            </div>
        `;
    }

    // else if (isNewOfficeDocument(fileData.ext)) {
    //     console.log('body ', body)
    //     console.log('fileData!!!: ', fileData)
    //     // Получаем ID файла из URL скачивания (вытаскиваем UUID из строки типа /api/files/UUID/download)
    //     // Если у вас в fileData есть прямой доступ к ID (например, fileData.id), лучше использовать его
    //     const urlParts = fileData.url.split('/');
    //     const fileId = urlParts[urlParts.length - 2]; // Обычно ID идет перед /download
    //     console.log('fileId: ', fileId)
    //    // 1. Вставляем чистый div-контейнер, куда ONLYOFFICE встроит редактор
    //     body.innerHTML = `
    //         <div id="onlyoffice-placeholder" style="width: 100%; height: 100%; min-height: 750px;"></div>
    //     `;
    //     // 2. Функция, которая делает fetch-запрос к вашему FastAPI за конфигом
    //     const loadEditorConfig = () => {
    //         fetch(`/api/files/${fileId}/onlyoffice-config`)
    //             .then(response => {
    //                 if (!response.ok) throw new Error('Бэкенд не отдал конфигурацию');
    //                 return response.json();
    //             })
    //             .then(config => {
    //                 // Инициализируем редактор ONLYOFFICE внутри нашего div
    //                 new DocsAPI.DocEditor("onlyoffice-placeholder", config);
    //             })
    //             .catch(err => {
    //                 console.error('Ошибка при получении конфигурации от FastAPI:', err);
    //                 body.innerHTML = `<div style="color: red; padding: 20px;">Не удалось загрузить конфигурацию документа.</div>`;
    //             });
    //     };
    //     // 3. Проверяем наличие скрипта ONLYOFFICE в браузере
    //     if (window.DocsAPI) {
    //         // Если скрипт уже загружен ранее, сразу делаем fetch-запрос
    //         loadEditorConfig();
    //     } else {
    //         // Если скрипта еще нет, динамически создаем тег <script>
    //         const script = document.createElement('script');
    //         script.type = 'text/javascript';
    //         // Укажите точный IP вашего Docker-контейнера ONLYOFFICE
    //         script.src = 'http://localhost:8087/web-apps/apps/api/documents/api.js'; 

    //         // Ждем загрузки api.js, и только ПОСЛЕ этого делаем fetch-запрос
    //         script.onload = () => {
    //             console.log('api.js успешно загружен с сервера документов');
    //             loadEditorConfig();
    //         };

    //         script.onerror = () => {
    //             console.error('Сервер ONLYOFFICE недоступен по указанному IP.');
    //             body.innerHTML = `<div style="color: red; padding: 20px;">Ошибка: Сервер редактирования документов недоступен.</div>`;
    //         };

    //         // Добавляем тег в head страницы для начала скачивания
    //         document.head.appendChild(script);
    //     }
    // }
    else if (isBiblio(fileData.ext)) {
        await launchBiblioFile(body, fileData)
    }
    else {
        // Для неподдерживаемых типов
        body.innerHTML = `
            <div class="unsupported-preview">
                <p>Файл "${fileData.name}" с расширением "${fileData.ext}" нельзя просмотреть онлайн</p>
                <p>Пожалуйста, скачайте файл для просмотра</p>
            </div>
        `;
    }
}

async function openModal(buttonElement) {
    const fileId = buttonElement.getAttribute('data-file-id');

    const fileItem = buttonElement.closest('.result-item');

    // Получаем данные из DOM
    const fileName = fileItem.querySelector('.result-title').textContent;
    const fileDescription = fileItem.querySelector('.result-description').textContent;
    const fileType = fileItem.querySelector('.result-type').textContent;

    const modal = document.getElementById('contentModal');
    // Закрываем модалку по клику за пределами modal-content 
    // непосредственно по элементу с id = 'contentModal'
    modal.addEventListener('click', (e)=>{
        if (e.target.id === 'contentModal') {
            closeModal()
        }
    })
    const modalTitle = document.getElementById('modal-title');
    const modalMeta = document.getElementById('modal-meta');
    const modalBody = document.getElementById('modal-body');

    const fileExt = buttonElement.dataset['file_ext'];
    const downloadLink = buttonElement.dataset['url_download'];
    // Python ставит строчное значение и с большой буквы
    const is_360 = buttonElement.dataset['is_360'] == 'True';


    // Устанавливаем базовую информацию
    modalTitle.textContent = fileName;
    modalMeta.innerHTML = `
        <p>${fileDescription}</p>
        <span class="file-type">${fileType}</span>
    `;

    // Очищаем предыдущий контент
    modalBody.innerHTML = `
        <p>Загрузка контента</p>
    `;

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    createFileViewer(modalBody, {
        id: fileId,
        url: downloadLink, 
        name: fileName,
        ext: fileExt,
        is_360: is_360,
    })

    // Показываем модальное окно
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Вспомогательные функции
function isImage(ext) {
    // return ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg1'].includes(ext);
    return ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'].includes(ext.toLowerCase());
}

function isVideo(ext) {
    return ['.mp4', '.mkv', '.webm', '.ogg', '.mov', '.avi', '.wmv'].includes(ext.toLowerCase());
}

function is3D(ext) {
    return [ /* 'stl',*/ '.glb'].includes(ext.toLowerCase());
}

function isAudio(ext) {
    return ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a', '.wma'].includes(ext.toLowerCase());
}

function isSunRavBook(ext) {
    return ['.srb'].includes(ext.toLowerCase());
}

function isBiblio(ext) {
    return ['.bdt'].includes(ext.toLowerCase());
}
// function isPdf(ext) {
//     return ext === '.pdf2';
// }

// function isTableDoc(ext) {
//     return ['.xls', '.xlsx'].includes(ext);
// }

// function isPresentation(ext) {
//     return ['.ppt', '.pptx'].includes(ext);
// }

// function isOfficeDocument(ext) {
//     return ['.doc', '.docx', '.odt', '.ods', '.odp'].includes(ext);
// }

function isOfficeDocument(ext) {
     return [
        '.doc', 
        '.docx', 
        '.odt', 
        '.ods', 
        '.odp', 
        '.xls', 
        '.xlsx',
        '.ppt', 
        '.pptx',
        '.tif',
        '.TIF',
        '.svg',
        '.SVG',
        '.pdf',
        '.rtf'
    ].includes(ext.toLowerCase());
 }

//  function isNewOfficeDocument(ext) {
//      return [
//         // '.docx', 
        
//     ].includes(ext);
//  }

function getVideoMimeType(ext) {
    const types = {
        '.mp4': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.ogg': 'video/ogg',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo'
    };
    return types[ext] || 'video/mp4';
}

function getAudioMimeType(ext) {
    const mimeTypes = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.aac': 'audio/aac',
        '.flac': 'audio/flac',
        '.m4a': 'audio/mp4',
        '.wma': 'audio/x-ms-wma'
    };
    return mimeTypes[ext.toLowerCase()] || 'audio/mpeg';
}

function getOfficeIcon(ext) {
    const icons = {
        '.doc': '📄',
        '.docx': '📄',
        '.xls': '📊',
        '.xlsx': '📊',
        '.ppt': '📑',
        '.pptx': '📑',
        '.odt': '📄',
        '.ods': '📊',
        '.odp': '📑'
    };
    return icons[ext] || '📁';
}


function closeModal() {
    const modal = document.getElementById('contentModal');
    const modalContent = modal.querySelector('.modal-content');

    // Добавляем анимацию закрытия
    modalContent.style.animation = 'fadeOut 0.3s forwards';
    modal.style.backgroundColor = 'transparent';

    // Даем время для анимации перед полным закрытием
    setTimeout(() => {
        // 1. Скрываем модальное окно
        modal.style.display = 'none';

        // 2. Восстанавливаем прокрутку
        document.body.style.overflow = 'auto';

        // 3. Останавливаем медиа
        const media = modal.querySelectorAll('video', 'audio');
        media.forEach(media_item => {
            media_item.pause();
            media_item.currentTime = 0;
        });

        // 4. Сбрасываем анимацию
        modalContent.style.animation = '';
        modal.style.backgroundColor = 'rgba(0,0,0,0.8)';
    }, 300);
}

let sectionAdditionalCriteries = document.querySelector('.advanced-filters__section-additional-criteries');
let itemOpenAdditionalCriteries = document.querySelector('.section-main-criteries__item-open-additional-criteries');
if (sectionAdditionalCriteries && itemOpenAdditionalCriteries){
    itemOpenAdditionalCriteries.addEventListener('click', (e)=>{
        e.target.classList.toggle('collapse');
        sectionAdditionalCriteries.classList.toggle('advanced-filters__section_collapsed');
    })
}

async function openModalWhithGraph(buttonElement) {
    const fileId = buttonElement.getAttribute('data-file-id');

    const fileItem = buttonElement.closest('.result-item');

   

    const modal = document.querySelector('#contentModal');
    const modalHeader = modal.querySelector('#modal-header');
    modalHeader.innerHTML = '';
    // Закрываем модалку по клику за пределами modal-content 
    // непосредственно по элементу с id = 'contentModal'
    modal.addEventListener('click', (e)=>{
        if (e.target.id == 'contentModal') {
            closeModal()
        }
    })
    let modalBody = modal.querySelector('#modal-body');
    modal.style.display = 'block'; // 1. Сначала ПОКАЗЫВАЕМ модалку на экране!
    let contentContentModal = modal.querySelector('.modal-content')
    contentContentModal.style.height = '90vh';
    // Очищаем предыдущий контент
    modalBody.innerHTML = `
        <p>Загрузка графа ...</p>
    `;
    let response = await fetch(buttonElement.dataset.url_get_graph);
    if (response.ok){
        const htmlText = await response.text();
        modalBody.innerHTML = htmlText
        // 3. ПРИНУДИТЕЛЬНЫЙ ЗАПУСК СКРИПТА
        // Извлекаем тег <script> из полученного текста и выполняем его код
        const scriptElement = modalBody.querySelector('script');
        if (scriptElement) {
            const executeScript = new Function(scriptElement.innerHTML);
            executeScript(); // Запускает d3.js отрисовку внутри IIFE
        }
    } else {
         modalBody.innerHTML = `
        <p>Ошибка загрузки графа</p>
    `;
    }
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
}