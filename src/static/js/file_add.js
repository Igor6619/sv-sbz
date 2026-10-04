// Функция для переключения отображения дочерних элементов
function toggleChildren(element) {
    const container = element.nextElementSibling;
    if (container.classList.contains('expanded')) {
        container.classList.remove('expanded');
        element.textContent = '+';
    } else {
        container.classList.add('expanded');
        element.textContent = '-';
    }
}

// Инициализация обработчиков событий для чекбоксов
document.addEventListener('DOMContentLoaded', function() {
    // Обработчик изменения состояния чекбокса
    function handleCheckboxChange(checkbox) {
        // Обновляем все дочерние чекбоксы
        const container = checkbox.closest('li').querySelector('.children-container');
        if (container) {
            container.querySelectorAll('.tree-checkbox').forEach(childCheckbox => {
                childCheckbox.checked = checkbox.checked;
                childCheckbox.indeterminate = false;
                // Рекурсивно вызываем для обновления вложенных чекбоксов
                handleCheckboxChange(childCheckbox);
            });
        }

        // Обновляем состояние родительских чекбоксов
        updateParentCheckboxes(checkbox);
    }

    // Функция для обновления состояния родительских чекбоксов
    function updateParentCheckboxes(checkbox) {
        let parentLi = checkbox.closest('li').parentNode.closest('li');
        while (parentLi) {
            const parentCheckbox = parentLi.querySelector('.tree-checkbox');
            const childCheckboxes = parentLi.querySelectorAll('.children-container .tree-checkbox');

            const checkedCount = Array.from(childCheckboxes).filter(cb => cb.checked).length;
            const indeterminateCount = Array.from(childCheckboxes).filter(cb => cb.indeterminate).length;

            if (checkedCount === childCheckboxes.length) {
                parentCheckbox.checked = true;
                parentCheckbox.indeterminate = false;
            } else if (checkedCount > 0 || indeterminateCount > 0) {
                parentCheckbox.checked = false;
                parentCheckbox.indeterminate = true;
            } else {
                parentCheckbox.checked = false;
                parentCheckbox.indeterminate = false;
            }

            parentLi = parentLi.parentNode.closest('li');
        }
    }

    // Назначаем обработчики событий для всех чекбоксов
    document.querySelectorAll('.tree-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            handleCheckboxChange(this);
        });
    });

    // Убедимся, что все узлы свернуты при загрузке
    document.querySelectorAll('.children-container').forEach(container => {
        container.classList.remove('expanded');
    });

    document.querySelectorAll('.toggle-children').forEach(toggle => {
        toggle.textContent = '+';
    });
});