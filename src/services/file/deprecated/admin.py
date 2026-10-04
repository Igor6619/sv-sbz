from sqladmin import ModelView


def register_admin(admin):
    from .models import FileTypeOrmModel, FileOrmModel, TagOrmModel #Ленивый импорт моделей

    class FileTypeAdmin(ModelView, model=FileTypeOrmModel):
        name = "Тип файла"
        name_plural = "Типы файлов"
        column_list = [column.name for column in FileTypeOrmModel.__table__.columns]

    class FileAdmin(ModelView, model=FileOrmModel):
        name = "Файл"
        name_plural = "Файлы"
        column_list = [column.name for column in FileOrmModel.__table__.columns]

    class TagAdmin(ModelView, model=TagOrmModel):
        name = "Тег"
        name_plural = "Теги"
        column_list = [column.name for column in TagOrmModel.__table__.columns]

    admin.add_view(FileTypeAdmin)
    admin.add_view(FileAdmin)
    admin.add_view(TagAdmin)
