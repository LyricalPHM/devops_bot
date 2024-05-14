# Docker project with telegram bot and master-slave pgsql databases:

1. `git clone -b docker https://github.com/LyricalPHM/devops_bot.git`  
2. `cd devops_bot`  
3. `cat README.md`
4. `cd bot`
5. `nano .env`  
6. `docker-compose up -d`  

<br>
<br>

# Ansible project with telegram bot and master-slave pgsql databases:
  
1. `cd /home`
2. `git clone -b ansible https://github.com/LyricalPHM/devops_bot.git`
3. `cd devops_bot`
4. `cat README.md`
5. `nano hosts`
6. `nano .env`
7. `ansible-playbook playbook_tg_bot.yml`

