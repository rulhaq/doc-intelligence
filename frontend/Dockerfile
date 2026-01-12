# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Install envsubst for runtime config
RUN apk add --no-cache gettext

# Copy build
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.main.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Runtime config template and entrypoint script
COPY config.template.js /usr/share/nginx/html/config.template.js
COPY docker-entrypoint.d/99-runtime-config.sh /docker-entrypoint.d/99-runtime-config.sh
RUN sed -i 's/\r$//' /docker-entrypoint.d/99-runtime-config.sh && \
    chmod +x /docker-entrypoint.d/99-runtime-config.sh && \
    mkdir -p /var/cache/nginx /var/run/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/run/nginx && \
    chmod -R 0777 /usr/share/nginx/html
USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]

