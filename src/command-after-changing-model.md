must run docker desktop + server using docker-compose up then open another terminal and paste these where drf_app is the name of container name

docker exec -it drf_app python manage.py makemigrations 
docker exec -it drf_app python manage.py migrate