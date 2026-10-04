async function show_glb(file) {
    const viewer = document.createElement('div');
    viewer.id = 'model-viewer';
    viewer.style.width = '100%';
    viewer.style.height = '70vh';
    viewer.style.backgroundColor = '#222222';
    viewer.style.position = 'relative';

    // Создаем элемент для GUI (должен быть добавлен перед рендерером)
    const guiContainer = document.createElement('div');
    guiContainer.style.position = 'absolute';
    guiContainer.style.top = '0';
    guiContainer.style.right = '0';
    guiContainer.style.zIndex = '100';
    viewer.appendChild(guiContainer);

    // ===== КНОПКА ПОЛНОЭКРАННОГО РЕЖИМА =====
    const fullscreenBtn = document.createElement('button');
    fullscreenBtn.textContent = '⛶';
    fullscreenBtn.style.position = 'absolute';
    fullscreenBtn.style.bottom = '10px';
    fullscreenBtn.style.right = '10px';
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

    // ===== КНОПКА УПРАВЛЕНИЯ АНИМАЦИЕЙ =====
    const animationBtn = document.createElement('button');
    animationBtn.textContent = '▶';
    animationBtn.style.position = 'absolute';
    animationBtn.style.bottom = '10px';
    animationBtn.style.left = '200px';
    animationBtn.style.zIndex = '101';
    animationBtn.style.fontSize = '24px';
    animationBtn.style.background = 'rgba(50, 50, 50, 0.7)';
    animationBtn.style.border = 'none';
    animationBtn.style.borderRadius = '6px';
    animationBtn.style.color = '#fff';
    animationBtn.style.cursor = 'pointer';
    animationBtn.style.padding = '8px 12px';
    animationBtn.style.lineHeight = '1';
    animationBtn.style.transition = 'background 0.2s';
    animationBtn.title = 'Воспроизведение/Пауза анимации';

    animationBtn.addEventListener('mouseenter', () => {
        animationBtn.style.background = 'rgba(70, 70, 70, 0.9)';
    });
    animationBtn.addEventListener('mouseleave', () => {
        animationBtn.style.background = 'rgba(50, 50, 50, 0.7)';
    });

    viewer.appendChild(animationBtn);

    // ===== КОНТЕЙНЕР ДЛЯ УПРАВЛЕНИЯ СКОРОСТЬЮ И ВЫБОРОМ АНИМАЦИИ =====
    const controlsContainer = document.createElement('div');
    controlsContainer.style.position = 'absolute';
    controlsContainer.style.bottom = '10px';
    controlsContainer.style.left = '10px';
    controlsContainer.style.zIndex = '101';
    controlsContainer.style.background = 'rgba(50, 50, 50, 0.7)';
    controlsContainer.style.borderRadius = '6px';
    controlsContainer.style.padding = '10px';
    controlsContainer.style.display = 'flex';
    controlsContainer.style.flexDirection = 'column';
    controlsContainer.style.alignItems = 'center';
    controlsContainer.style.gap = '8px';
    controlsContainer.style.minWidth = '180px';
    viewer.appendChild(controlsContainer);

    // Заголовок контейнера
    const animationsTitle = document.createElement('label')
    animationsTitle.textContent = 'Выбор анимаций'
    animationsTitle.style.color = '#fff';
    controlsContainer.appendChild(animationsTitle)

    // Выпадающий список анимаций
    const animationSelect = document.createElement('select');
    animationSelect.style.width = '160px';
    animationSelect.style.padding = '5px';
    animationSelect.style.borderRadius = '4px';
    animationSelect.style.border = '1px solid #666';
    animationSelect.style.background = '#333';
    animationSelect.style.color = '#fff';
    animationSelect.style.fontSize = '12px';
    animationSelect.style.cursor = 'pointer';
    controlsContainer.appendChild(animationSelect);

    // Метка скорости
    const speedLabel = document.createElement('span');
    speedLabel.textContent = 'Скорость: 1.0x';
    speedLabel.style.color = '#fff';
    speedLabel.style.fontSize = '12px';
    speedLabel.style.fontFamily = 'Arial, sans-serif';
    controlsContainer.appendChild(speedLabel);

    // Слайдер скорости
    const speedSlider = document.createElement('input');
    speedSlider.type = 'range';
    speedSlider.min = '0';
    speedSlider.max = '3';
    speedSlider.step = '0.1';
    speedSlider.value = '1';
    speedSlider.style.width = '160px';
    speedSlider.style.cursor = 'pointer';
    controlsContainer.appendChild(speedSlider);

    // Инициализация Three.js сцены
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xCCCCCC);

    // Освещение
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 10, 7);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);

    const hemisphereLight = new THREE.HemisphereLight(0xffffbb, 0x080820, 0.5);
    scene.add(hemisphereLight);

    // Камера
    const camera = new THREE.PerspectiveCamera(
        75,
        viewer.clientWidth / viewer.clientHeight,
        0.1,
        1000
    );
    camera.position.set(5, 5, 5);

    // Рендерер
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(viewer.clientWidth, viewer.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.shadowMap.enabled = true;
    viewer.appendChild(renderer.domElement);

    // Орбитальные контролы
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.screenSpacePanning = false;
    controls.maxPolarAngle = Math.PI;

    // Часы для анимации
    const clock = new THREE.Clock();
    let mixer = null;
    let isAnimationPlaying = false;
    let animationActions = []; // Все созданные действия
    let activeAction = null; // Текущее активное действие
    let animationSpeed = 1.0;
    let animationClips = []; // Клипы анимации из GLTF

    // GUI интерфейс
    const gui = new dat.GUI({ autoPlace: false, width: 300 });
    guiContainer.appendChild(gui.domElement);

    const lightsFolder = gui.addFolder('Освещение');
    lightsFolder.add(directionalLight, 'intensity', 0, 2).name('Направленный свет');
    lightsFolder.add(ambientLight, 'intensity', 0, 2).name('Окружающий свет');
    lightsFolder.add(hemisphereLight, 'intensity', 0, 2).name('Полусферический свет');

    const sceneFolder = gui.addFolder('Сцена');
    sceneFolder.addColor({ color: 0x222222 }, 'color').onChange(val => {
        scene.background = new THREE.Color(val);
    }).name('Фон');

    const modelFolder = gui.addFolder('Модель');
    const wireframeCtrl = modelFolder.add({ wireframe: false }, 'wireframe').name('Каркасный режим');

    lightsFolder.open();
    sceneFolder.open();
    modelFolder.open();

    // Загрузка модели
    const loader = new THREE.GLTFLoader();
    const gltf = await new Promise((resolve, reject) => {
        loader.parse(
            file,
            '',
            resolve,
            reject
        );
    });

    const model = gltf.scene;
    scene.add(model);

    // Включение теней для всех мешей
    model.traverse(child => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });

    // Настройка анимации
    if (gltf.animations && gltf.animations.length) {
        mixer = new THREE.AnimationMixer(model);
        animationClips = gltf.animations;

        // Создаем действия для всех клипов, но не запускаем их сразу
        animationClips.forEach((clip, index) => {
            const action = mixer.clipAction(clip);
            action.timeScale = animationSpeed;
            animationActions.push(action);
        });

        // Заполняем выпадающий список
        populateAnimationSelect();

        // Выбираем первую анимацию по умолчанию
        if (animationActions.length > 0) {
            animationSelect.value = '0';
        }
    } else {
        // Если нет анимаций, скрываем элементы управления
        animationBtn.style.display = 'none';
        controlsContainer.style.display = 'none';
    }

    // Функция для заполнения выпадающего списка
    function populateAnimationSelect() {
        // Очищаем список
        animationSelect.innerHTML = '';

        // Добавляем опцию "Запустить все"
        const allOption = document.createElement('option');
        allOption.value = 'all';
        allOption.textContent = 'Запустить все анимации';
        animationSelect.appendChild(allOption);

        // Добавляем разделитель
        const separator = document.createElement('option');
        separator.disabled = true;
        separator.textContent = '─────────────';
        animationSelect.appendChild(separator);

        // Добавляем отдельные анимации
        animationClips.forEach((clip, index) => {
            const option = document.createElement('option');
            option.value = index.toString();
            // Используем имя клипа, если есть, иначе индекс
            option.textContent = clip.name || `Анимация ${index + 1}`;
            animationSelect.appendChild(option);
        });
    }

    // Функция для остановки всех анимаций
    function stopAllAnimations() {
        animationActions.forEach(action => {
            action.stop();
        });
        activeAction = null;
    }

    // Функция для воспроизведения выбранной анимации
    function playSelectedAnimation(indexOrAll) {
        // Останавливаем все текущие анимации
        stopAllAnimations();

        if (indexOrAll === 'all') {
            // Запускаем все анимации одновременно
            animationActions.forEach(action => {
                action.reset();
                action.play();
                action.paused = !isAnimationPlaying;
            });
            activeAction = null; // Нет единственной активной анимации
        } else {
            // Запускаем конкретную анимацию
            const index = parseInt(indexOrAll);
            if (index >= 0 && index < animationActions.length) {
                const action = animationActions[index];
                action.reset();
                action.play();
                action.paused = !isAnimationPlaying;
                activeAction = action;
            }
        }
    }

    // Центрирование модели
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);

    model.position.sub(center);
    controls.target.copy(center);

    // Автоматическая настройка камеры
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 * Math.tan(fov / 2));
    camera.position.z = cameraZ * 2;
    controls.update();

    // Обработчик изменения wireframe режима
    wireframeCtrl.onChange(val => {
        model.traverse(child => {
            if (child.isMesh) {
                child.material.wireframe = val;
            }
        });
    });

    // ===== ОБРАБОТЧИК ИЗМЕНЕНИЯ ВЫБРАННОЙ АНИМАЦИИ =====
    animationSelect.addEventListener('change', (e) => {
        playSelectedAnimation(e.target.value);
    });

    // ===== ОБРАБОТЧИК ИЗМЕНЕНИЯ СКОРОСТИ =====
    speedSlider.addEventListener('input', (e) => {
        animationSpeed = parseFloat(e.target.value);
        speedLabel.textContent = `Скорость: ${animationSpeed.toFixed(1)}x`;

        // Применяем скорость ко всем действиям анимации
        animationActions.forEach(action => {
            action.timeScale = animationSpeed;
        });
    });

    // ===== ОБРАБОТЧИК КЛИКА ПО КНОПКЕ АНИМАЦИИ =====
    animationBtn.addEventListener('click', () => {
        if (!mixer || animationActions.length === 0) return;

        if (isAnimationPlaying) {
            // Пауза
            if (animationSelect.value === 'all') {
                // Если выбрано "все", ставим на паузу все
                animationActions.forEach(action => {
                    action.paused = true;
                });
            } else if (activeAction) {
                // Иначе только активную
                activeAction.paused = true;
            }
            animationBtn.textContent = '▶';
            animationBtn.title = 'Воспроизвести анимацию';
            isAnimationPlaying = false;
        } else {
            // Воспроизведение
            if (animationSelect.value === 'all') {
                animationActions.forEach(action => {
                    action.paused = false;
                });
            } else if (activeAction) {
                activeAction.paused = false;
            }
            animationBtn.textContent = '⏸';
            animationBtn.title = 'Пауза анимации';
            isAnimationPlaying = true;
            playSelectedAnimation(animationSelect.value);
        }
    });

    // Анимация
    function animate() {
        requestAnimationFrame(animate);

        const delta = clock.getDelta();
        if (mixer && isAnimationPlaying) {
            mixer.update(delta);
        }

        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    function resize_model() {
        camera.aspect = viewer.clientWidth / viewer.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(viewer.clientWidth, viewer.clientHeight);
    }

    // ===== УПРАВЛЕНИЕ ПОЛНОЭКРАННЫМ РЕЖИМОМ =====
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    function toggleFullscreen() {
        const fullscreenElement = document.fullscreenElement;
        if (!fullscreenElement) {
            viewer.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    // Обработчик изменения размера
    const resizeObserver = new ResizeObserver(() => {
        resize_model();
    });
    resizeObserver.observe(viewer);

    // Сохраняем ссылки для последующей очистки
    viewer._scene = scene;
    viewer._renderer = renderer;
    viewer._controls = controls;
    viewer._gui = gui;
    viewer._mixer = mixer;
    viewer._animationBtn = animationBtn;
    viewer._speedSlider = speedSlider;
    viewer._controlsContainer = controlsContainer;
    viewer._animationSelect = animationSelect;

    return viewer;
}