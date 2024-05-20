## Перед запуском playbook'а не забудьте настроить файл inventory.

<br>
<br>
  
1. Перед запуском `playbook_tg_bot.yml` необходимо настроить файл `inventory` расположенный в каталоге `devops_bot/` В этом файле содержатся важные переменные конфигурации, необходимые для корректного функционирования всего проекта.
  
<br> 
  
2. Выполнять `git clone -b ansible https://github.com/LyricalPHM/devops_bot.git` рекомендуется в `/home` директории, в противном случае придется отдельно указывать путь к файлу `inventory` в `ansible.cfg`
  
<br> 
  
3. Подробная инструкция по запуску проекта находится в `main` ветке данного репозитория. 
