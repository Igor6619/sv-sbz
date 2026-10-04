1. Скопировать файл biblio-launcher.desktop в папку /home/user/.local/share/applications/

2. Сделать его исполняемым:
chmod +x /home/user/.local/share/applications/biblio-launcher.desktop

3. Скопировать biblio_launcher.run в папку с СПО Библио (в нашем случае в папку /opt/rio/spo/biblio/beditor/) она указана в файле biblio-launcher.desktop)

4. Сделать его исполняемым
chmod +x /opt/rio/spo/biblio/beditor/biblio_launcher.run

5. Обновить информацию о MIME-типах и схемах
update-desktop-database ~/.local/share/applications/

6. Проверить, что схема зарегистрирована:
xdg-mime query default x-scheme-handler/biblio-launcher
(должно вернуться: "biblio-launcher.desktop")

6.1. Если нет, то выполнить:
xdg-mime default x-scheme-handler/biblio-launcher

7. Перезагрузить браузер (операционную систему)
