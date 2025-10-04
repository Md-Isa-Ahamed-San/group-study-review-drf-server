Here is a list of the essential commands for managing your Dockerized Django application, each with a brief description.

# !Open the docker Desktop first and activate virtual environment

- `.\venv-drf\Scripts\activate`

### Docker Compose Commands

- `docker-compose up --build -d`
  This command builds your Docker images for the first time or after changes to your `Dockerfile` or dependencies. It then starts the containers in the background (`-d`).

- `docker-compose up -d`
  Use this command to start your containers when you've only made changes to your application code. It's faster as it doesn't rebuild the images.

- `docker-compose down`
  This command stops and removes the containers, networks, and volumes created by `docker-compose up`.

### Django Management Commands (via Docker)

- `docker exec drf_app python manage.py makemigrations`
  This command creates new migration files inside the `web` container (`drf_app`) based on changes to your Django models.

- `docker exec drf_app python manage.py migrate`
  This applies the pending migration files to the PostgreSQL database, updating the database schema.

### Interactive Shell Commands

- `docker exec -it postgres_db psql -U your_user -d your_db_name`
- `docker exec -it postgres_db psql -U isaahamed -d group_study_review`
  This command opens an interactive command-line shell (`psql`) to your PostgreSQL database running in the `postgres_db` container.

- `docker exec -it drf_app python manage.py shell`
  This starts an interactive Django shell inside your `web` container, allowing you to run Python code in the context of your Django project.
