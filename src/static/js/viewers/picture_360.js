async function show_360_image(arrayBuffer) {
    const viewer = document.createElement('div');
    viewer.id = 'image-viewer';
    viewer.style.width = '100%';
    viewer.style.height = '70vh';
    viewer.style.backgroundColor = '#000000';
    viewer.style.position = 'relative';

    // ===== КНОПКА ПОЛНОЭКРАННОГО РЕЖИМА (слева) =====
    const fullscreenBtn = document.createElement('button');
    fullscreenBtn.textContent = '⛶';
    fullscreenBtn.style.position = 'absolute';
    fullscreenBtn.style.bottom = '24px';
    fullscreenBtn.style.right = '24px';
    fullscreenBtn.style.zIndex = '101';
    fullscreenBtn.style.fontSize = '24px';
    fullscreenBtn.style.background = 'rgba(50, 50, 50, 0.7)';
    fullscreenBtn.style.border = 'none';
    fullscreenBtn.style.borderRadius = '6px';
    fullscreenBtn.style.color = '#fff';
    fullscreenBtn.style.cursor = 'pointer';
    fullscreenBtn.style.padding = '8px 12px';
    fullscreenBtn.style.lineHeight = '1';
    fullscreenBtn.style.transition = 'background 0.2s';
    fullscreenBtn.title = 'Полноэкранный режим';
    viewer.appendChild(fullscreenBtn);

    // ===== УПРАВЛЕНИЕ ПОЛНОЭКРАННЫМ РЕЖИМОМ =====
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    function toggleFullscreen() {
        // Проверяем, находимся ли мы уже в полноэкранном режиме
       
        const fullscreenElement = document.fullscreenElement ;
         if (!fullscreenElement) {
            // Входим в полноэкранный режим
            viewer.requestFullscreen();
            
        } else {
            // Выходим из полноэкранного режима
            document.exitFullscreen();
            
        }
    }

    // Конвертируем ArrayBuffer в Blob
    const blob = new Blob([arrayBuffer]);
    const imageUrl = URL.createObjectURL(blob);

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
    viewer.appendChild(renderer.domElement);

    // Орбитальные контролы
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.screenSpacePanning = false;
    controls.maxPolarAngle = Math.PI;
    controls.minPolarAngle = 0;

    // Создаем изображение
    const img = new Image();
    img.src = imageUrl;

    let sphere;

    img.onload = function() {
        // Создаем текстуру из изображения
        const texture = new THREE.Texture(img);
        texture.needsUpdate = true;

        // Создаем сферу для изображения
        const geometry = new THREE.SphereGeometry(500, 60, 40);
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.BackSide
        });

        sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);
    };

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

    // window.addEventListener('resize', resizeViewer);

    // Очистка при удалении
    viewer.cleanup = function() {
        // window.removeEventListener('resize', resizeViewer);
        URL.revokeObjectURL(imageUrl);
        if (renderer) {
            renderer.dispose();
        }
    };
    // setTimeout(() => resizeViewer(), 1000);
    const resizeObserver = new ResizeObserver(() => {
        resizeViewer();
    });
    resizeObserver.observe(viewer);
    // ✅ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: обработчик fullscreenchange
    function onFullscreenChange() {
        const isFullscreen = document.fullscreenElement === viewer;
        fullscreenBtn.title = isFullscreen ? 'Выйти из полноэкранного режима' : 'Полноэкранный режим';
                
    }

    document.addEventListener('fullscreenchange', onFullscreenChange);

    return viewer;
}