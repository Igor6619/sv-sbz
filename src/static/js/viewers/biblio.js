async function launchBiblioFile(body, fileData) {
    try {
        const generated_uuid = generateUUID();
        body.innerHTML = `
            <div class="unsupported-preview">
                <p>Файл "${fileData.name}" с расширением "${fileData.ext}" нельзя просмотреть онлайн</p>
                <p>Пожалуйста, дождитесь скачивания и открытия файла специализированной программой</p>
            </div>
        `;
        const response = await fetch(fileData.url);
        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status} ${response.statusText}`);
        }
        const blob = await response.blob();

        const objectUrl = URL.createObjectURL(blob);
        const downloadLink = document.createElement('a');
        downloadLink.href = objectUrl;
        downloadLink.download = generated_uuid + '.bdt';
        downloadLink.style.display = 'none';

        body.appendChild(downloadLink);
        downloadLink.click();

        // Очистка
        body.removeChild(downloadLink);
        URL.revokeObjectURL(objectUrl);

        setTimeout(() => {
            const launcherLink = document.createElement('a');
            launcherLink.href = 'biblio-launcher://' + generated_uuid;
            launcherLink.style.display = 'none';

            body.appendChild(launcherLink);
            launcherLink.click();
            body.removeChild(launcherLink);

//            modalElement.innerHTML = `
//                <div class="unsupported-preview">
//                    <p>Файл "${fileData.name}" сохранен.</p>
//                    <p>Запускаем специализированную программу...</p>
//                </div>
//            `;

        }, 1000);

    } catch (error) {
        console.error('Ошибка при скачивании:', error);
        body.innerHTML = `
            <div class="unsupported-preview" style="color: red;">
                <p>Не удалось загрузить файл: ${error.message}</p>
                <a href="${url}" download>Попробовать скачать вручную</a>
            </div>
        `;
    }
}