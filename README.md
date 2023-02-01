Для запуска приложения нужно скачать и установить Docker-compose 


Запуск проекта командой 
____________
docker-compose -f docker-compose.yml build
____________
 docker-compose -f docker-compose.yml up 



Если у вас появляется ошибка "FATAL:  could not open directory "pg_notify": No such file or directory"   Удалите папку "pg_db" в папке с приложением. 

После этого снова запустите команду " docker-compose -f docker-compose.yml up "
