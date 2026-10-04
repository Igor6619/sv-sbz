async function show_360_video(arrayBuffer) {
    const viewer = document.createElement('div');
    viewer.id = 'video-viewer';
    viewer.style.width = '100%';
    viewer.style.height = '70vh';
    viewer.style.backgroundColor = '#000000';
    viewer.style.position = 'relative';

    // Конвертируем ArrayBuffer в Blob
    const blob = new Blob([arrayBuffer]);
    const videoUrl = URL.createObjectURL(blob);

    // // Создаем элементы управления
    // const controlsPanel = document.createElement('div');
    // controlsPanel.style.position = 'absolute';
    // controlsPanel.style.bottom = '20px';
    // controlsPanel.style.left = '0';
    // controlsPanel.style.width = '100%';
    // controlsPanel.style.padding = '10px';
    // controlsPanel.style.backgroundColor = 'rgba(0,0,0,0.5)';
    // controlsPanel.style.display = 'flex';
    // controlsPanel.style.flexDirection = 'column';
    // controlsPanel.style.alignItems = 'center';
    // controlsPanel.style.zIndex = '100';

     // Создаем элементы управления
    const controlsPanel = document.createElement('div');
    controlsPanel.style.position = 'absolute';
    controlsPanel.style.bottom = '20px';
    controlsPanel.style.left = '0';
    controlsPanel.style.width = '100%';
    controlsPanel.style.padding = '10px';
    controlsPanel.style.backgroundColor = 'rgba(0,0,0,0.5)';
    controlsPanel.style.display = 'flex';
    controlsPanel.style.alignItems = 'center';
    controlsPanel.style.zIndex = '100';

    const playPauseBtn = document.createElement('button');
    playPauseBtn.textContent = '⏸';
    playPauseBtn.style.margin = '0 10px';

    const seekBar = document.createElement('input');
    seekBar.type = 'range';
    seekBar.style.width = '100%';
    seekBar.style.margin = '10px 0';

    const timeDisplay = document.createElement('div');
    timeDisplay.style.display = 'flex';
    timeDisplay.style.justifyContent = 'end';
    timeDisplay.style.columnGap = '12px';
    // timeDisplay.style.justifyContent = 'space-between';
    timeDisplay.style.width = '10%';
    timeDisplay.style.color = 'white';

    const currentTime = document.createElement('span');
    currentTime.textContent = '00:00';

    const duration = document.createElement('span');
    duration.textContent = '00:00';


    timeDisplay.appendChild(currentTime);
    timeDisplay.appendChild(duration);

    // ===== КНОПКА ПОЛНОЭКРАННОГО РЕЖИМА =====
    const fullscreenBtn = document.createElement('button');
    fullscreenBtn.textContent = '⛶';
    fullscreenBtn.style.margin = '0 10px';
    fullscreenBtn.style.fontSize = '20px';
    fullscreenBtn.style.background = 'transparent';
    fullscreenBtn.style.border = 'none';
    fullscreenBtn.style.color = 'white';
    fullscreenBtn.style.cursor = 'pointer';
    fullscreenBtn.title = 'Полноэкранный режим';

    controlsPanel.appendChild(playPauseBtn);
    controlsPanel.appendChild(seekBar);
    controlsPanel.appendChild(timeDisplay);
    controlsPanel.appendChild(fullscreenBtn);
    viewer.appendChild(controlsPanel);

    // Инициализация Three.js сцены
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);

    // Камера
    const camera = new THREE.PerspectiveCamera(
        75,
        viewer.clientWidth / viewer.clientHeight,
        0.1,
        1000
    );
    camera.position.z = 0.1;

    // Рендерер
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(viewer.clientWidth, viewer.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    viewer.insertBefore(renderer.domElement, controlsPanel);

    // Орбитальные контролы
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.screenSpacePanning = false;
    controls.maxPolarAngle = Math.PI;
    controls.minPolarAngle = 0;

    // Создаем видеоэлемент
    const video = document.createElement('video');
    video.src = videoUrl; // Используем URL из Blob
    video.loop = true;
    video.muted = true;
    video.playsInline = true;
    video.crossOrigin = 'anonymous';

    let videoSphere;
    let isPlaying = false;

    video.onloadedmetadata = () => {
        seekBar.max = video.duration;
        duration.textContent = formatTime(video.duration);
    };

    video.oncanplay = () => {
        video.play().then(() => {
            isPlaying = true;
            playPauseBtn.textContent = '⏸';

            // Создаем текстуру из видео
            const videoTexture = new THREE.VideoTexture(video);
            videoTexture.minFilter = THREE.LinearFilter;
            videoTexture.magFilter = THREE.LinearFilter;

            // Создаем сферу для видео
            const geometry = new THREE.SphereGeometry(500, 60, 40);
            const material = new THREE.MeshBasicMaterial({
                map: videoTexture,
                side: THREE.BackSide
            });

            videoSphere = new THREE.Mesh(geometry, material);
            scene.add(videoSphere);
        }).catch(error => {
            console.error('Autoplay failed:', error);
            // Показываем кнопку play, если autoplay не сработал
            isPlaying = false;
            playPauseBtn.textContent = '▶';
        });
    };

    // Управление воспроизведением
    playPauseBtn.addEventListener('click', () => {
        if (isPlaying) {
            video.pause();
            playPauseBtn.textContent = '▶';
        } else {
            video.play().then(() => {
                playPauseBtn.textContent = '⏸';
                isPlaying = true;
            });
        }
        isPlaying = !isPlaying;
    });

    // Обновление ползунка
    video.addEventListener('timeupdate', () => {
        if (!isNaN(video.duration)) {
            seekBar.value = video.currentTime;
            currentTime.textContent = formatTime(video.currentTime);
        }
    });

    // Перемотка
    seekBar.addEventListener('input', () => {
        if (!isNaN(video.duration)) {
            video.currentTime = seekBar.value;
        }
    });

    // Форматирование времени
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Анимация
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // Обработчик изменения размера
    function resizeViewer() {
        camera.aspect = viewer.clientWidth / viewer.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(viewer.clientWidth, viewer.clientHeight);
    }

    window.addEventListener('resize', resizeViewer);

    // Очистка при удалении
    viewer.cleanup = function() {
        window.removeEventListener('resize', resizeViewer);
        if (video) {
            video.pause();
            URL.revokeObjectURL(video.src);
        }
        if (renderer) {
            renderer.dispose();
        }
    };

    // ===== УПРАВЛЕНИЕ ПОЛНОЭКРАННЫМ РЕЖИМОМ =====
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    function toggleFullscreen() {
        // Проверяем, находимся ли мы уже в полноэкранном режиме
       
        const fullscreenElement = document.fullscreenElement ;
         if (!fullscreenElement) {
            // Входим в полноэкранный режим
            viewer.requestFullscreen();
            // if (viewer.requestFullscreen) {
            //     viewer.requestFullscreen();
            // } else if (viewer.webkitRequestFullscreen) {
            //     viewer.webkitRequestFullscreen(); // Safari
            // } else if (viewer.msRequestFullscreen) {
            //     viewer.msRequestFullscreen(); // IE11
            // } else if (viewer.mozRequestFullScreen) {
            //     viewer.mozRequestFullScreen(); // Firefox
            // }
        } else {
            // Выходим из полноэкранного режима
            document.exitFullscreen();
            // if (document.exitFullscreen) {
            //     document.exitFullscreen();
            // } else if (document.webkitExitFullscreen) {
            //     document.webkitExitFullscreen();
            // } else if (document.msExitFullscreen) {
            //     document.msExitFullscreen();
            // } else if (document.mozCancelFullScreen) {
            //     document.mozCancelFullScreen();
            // }
        }
    }

    

    // setTimeout(() => resizeViewer(), 1000);

    const resizeObserver = new ResizeObserver(() => {
        resizeViewer();
    });
    resizeObserver.observe(viewer);

     // КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: обработчик fullscreenchange
    function onFullscreenChange() {
        const isFullscreen = document.fullscreenElement === viewer;
        fullscreenBtn.title = isFullscreen ? 'Выйти из полноэкранного режима' : 'Полноэкранный режим';
        
    }

    document.addEventListener('fullscreenchange', onFullscreenChange);

    return viewer;
}