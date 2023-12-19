FROM webdevops/php-apache:7.0
WORKDIR /var/www/html
EXPOSE 80

COPY melomane.conf /etc/apache2/sites-available/melomane.conf
COPY docker-php-ext-disable-xdebug /usr/local/bin/docker-php-ext-disable-xdebug
RUN echo "ServerName root.localhost" >> /etc/apache2/apache2.conf
RUN a2enmod rewrite
RUN a2dissite 000-default
RUN a2ensite melomane
RUN service apache2 restart
RUN mkdir /var/www/html/melomane && chmod a+rw /var/www/html/melomane

RUN pecl install xdebug-2.7.2
RUN docker-php-ext-enable xdebug

RUN apt install nano