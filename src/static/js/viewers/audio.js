function createAudioPlayer(fileData) {
    const container = document.createElement('div');
    container.className = 'audio-player';

    container.innerHTML = `
        <div class="audio-player-container">
            <div class="audio-info">
                <div class="audio-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                    </svg>
                </div>
                <div class="audio-details">
                    <div class="audio-name">${fileData.name}${fileData.ext}</div>
                </div>
            </div>

            <audio id="audio-element" preload="metadata">
                <source src="${fileData.url}" type="${getAudioMimeType(fileData.ext)}">
                Ваш браузер не поддерживает воспроизведение аудио.
            </audio>

            <div class="audio-controls">
                <button class="play-btn" title="Воспроизвести/Пауза">
                    <svg class="play-icon" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                    <svg class="pause-icon" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                        <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                    </svg>
                </button>

                <div class="progress-container">
                    <div class="time current-time">0:00</div>
                    <input type="range" class="progress-bar" min="0" max="100" value="0" step="0.1">
                    <div class="time duration">0:00</div>
                </div>

                <div class="volume-control">
                    <button class="volume-btn" title="Громкость">
                        <svg class="volume-high" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                        </svg>
                        <svg class="volume-medium" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                            <path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
                        </svg>
                        <svg class="volume-low" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                            <path d="M7 9v6h4l5 5V4l-5 5H7z"/>
                        </svg>
                        <svg class="volume-mute" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                        </svg>
                    </button>
                    <input type="range" class="volume-slider" min="0" max="100" value="100">
                </div>
            </div>
        </div>
    `;

    // Инициализируем элементы управления
    initAudioControls(container, fileData.url);

    return container;
}

function updateVolumeIcon(volumeBtn, volume) {
    const icons = {
        high: volumeBtn.querySelector('.volume-high'),
        medium: volumeBtn.querySelector('.volume-medium'),
        low: volumeBtn.querySelector('.volume-low'),
        mute: volumeBtn.querySelector('.volume-mute')
    };

    // Скрываем все иконки
    Object.values(icons).forEach(icon => {
        if (icon) icon.style.display = 'none';
    });

    // Показываем нужную иконку
    if (volume === 0) {
        if (icons.mute) icons.mute.style.display = 'block';
    } else if (volume < 0.3) {
        if (icons.low) icons.low.style.display = 'block';
    } else if (volume < 0.7) {
        if (icons.medium) icons.medium.style.display = 'block';
    } else {
        if (icons.high) icons.high.style.display = 'block';
    }
}

// Обновите функцию initAudioControls для использования новой функции иконок
function initAudioControls(container, audioUrl) {
    const audio = container.querySelector('#audio-element');
    const playBtn = container.querySelector('.play-btn');
    const playIcon = container.querySelector('.play-icon');
    const pauseIcon = container.querySelector('.pause-icon');
    const progressBar = container.querySelector('.progress-bar');
    const currentTimeEl = container.querySelector('.current-time');
    const durationEl = container.querySelector('.duration');
    const volumeBtn = container.querySelector('.volume-btn');
    const volumeSlider = container.querySelector('.volume-slider');

    let isPlaying = false;

    // Устанавливаем начальную громкость
    audio.volume = 1;
    volumeSlider.value = 100;

    // Воспроизведение/пауза
    playBtn.addEventListener('click', () => {
        if (isPlaying) {
            audio.pause();
            playIcon.style.display = 'block';
            pauseIcon.style.display = 'none';
        } else {
            audio.play().catch(error => {
                console.error('Ошибка воспроизведения:', error);
                showAudioError(container);
            });
            playIcon.style.display = 'none';
            pauseIcon.style.display = 'block';
        }
        isPlaying = !isPlaying;
    });

    // Обновление прогресса
    audio.addEventListener('timeupdate', () => {
        if (audio.duration) {
            const progress = (audio.currentTime / audio.duration) * 100;
            progressBar.value = progress;
            currentTimeEl.textContent = formatTime(audio.currentTime);
        }
    });

    // Загрузка метаданных
    audio.addEventListener('loadedmetadata', () => {
        durationEl.textContent = formatTime(audio.duration);
    });

    // Перемотка
    progressBar.addEventListener('input', () => {
        if (audio.duration) {
            audio.currentTime = (progressBar.value / 100) * audio.duration;
        }
    });

    /// Громкость
    volumeSlider.addEventListener('input', () => {
        const volumeValue = volumeSlider.value / 100;
        audio.volume = volumeValue;
        updateVolumeIcon(volumeBtn, volumeValue);
    });

    volumeBtn.addEventListener('click', () => {
        if (audio.volume > 0) {
            audio.dataset.prevVolume = audio.volume;
            audio.volume = 0;
            volumeSlider.value = 0;
            updateVolumeIcon(volumeBtn, 0);
        } else {
            const prevVolume = parseFloat(audio.dataset.prevVolume) || 1;
            audio.volume = prevVolume;
            volumeSlider.value = prevVolume * 100;
            updateVolumeIcon(volumeBtn, prevVolume);
        }
    });

    // Обработка окончания воспроизведения
    audio.addEventListener('ended', () => {
        isPlaying = false;
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        progressBar.value = 0;
        currentTimeEl.textContent = '0:00';
    });

    // Обработка ошибок
    audio.addEventListener('error', () => {
        showAudioError(container);
    });

    // Инициализация иконки громкости
    updateVolumeIcon(volumeBtn, 1);
}

function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function showAudioError(container) {
    container.classList.add('audio-error');
    const audioInfo = container.querySelector('.audio-info');
    audioInfo.innerHTML = `
        <div class="audio-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
        </div>
        <div class="audio-details">
            <div class="audio-name">Ошибка загрузки аудио</div>
            <div class="audio-format">Попробуйте обновить страницу</div>
        </div>
    `;
}