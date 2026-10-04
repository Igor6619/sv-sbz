from .user.admin import register_admin as user_admin
from .file.admin import register_admin as file_admin
from sqladmin import Admin


def register_all_admin_views(admin: Admin):
    """
    Глобальная функция для регистрации моделей из модулей
    :arg admin: Экземпляр Admin в sqladmin
    """
    user_admin(admin)
    file_admin(admin)
