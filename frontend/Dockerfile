# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files và cài đặt
COPY package*.json ./
RUN npm ci

# Copy toàn bộ source
COPY . .

# Build Next.js app
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]