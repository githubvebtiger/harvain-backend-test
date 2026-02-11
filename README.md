## Production deploy


1. Init repository

   ```console
   ~$ mkdir gramline && cd gramline
   ~/gramline$ git init && git remote add origin git@github.com:githubvebtiger/gramline.git && git pull origin main
   ```

2. Install docker/docker-compose standalone

   Docker: https://docs.docker.com/engine/install/ubuntu/

   Docker-compose: https://docs.docker.com/compose/install/compose-plugin/#install-the-plugin-manually

3. Configure nginx
   ```console
   ~$ mkdir nginx && cp gramline/nginx.conf.template nginx/
   ````

4. Copy docker-compose config and setup environment 

   ```console
   ~$ cp gramline/docker-compose.prod.yml
   ~$ touch .env && nano .env
   ```

   Paste into editor and configure

   ```
   DATABASE_NAME=gramline
   DATABASE_USER=gramline
   DATABASE_HOST=db
   DATABASE_PASSWORD=## Generate database password ##
   DATABASE_PORT=5432

   RAPID_API_HOST=## Rapid api host for football import ##
   RAPID_API_KEY=## Rapid api host for football import ##

   BACKEND_DOMAIN=## Paste service domain ##
   CERTBOT_EMAIL=## Contact email for certbot organization ##
   ```

5. Build backend image

   ```console
   docker-compose -f docker-compose.prod.yml build back
   ```

6. Start service

   ```console
   docker-compose -f docker-compose.prod.yml up -d
   ```
