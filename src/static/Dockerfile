FROM nginx:alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static files
COPY *.html /usr/share/nginx/html/
COPY *.jpg /usr/share/nginx/html/

# Expose port 80
EXPOSE 8000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
