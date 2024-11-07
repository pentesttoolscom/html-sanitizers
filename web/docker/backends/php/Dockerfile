FROM composer

WORKDIR /app
COPY composer.json ./
COPY index.php ./

RUN composer install

ENTRYPOINT php -S 0.0.0.0:8000 -t /app
