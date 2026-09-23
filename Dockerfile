FROM nginx:alpine

# Salin file situs ke folder default Nginx
COPY dist/ /usr/share/nginx/html/

# Nginx default mendengarkan di port 80
EXPOSE 8080
