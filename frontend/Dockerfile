FROM node:18-alpine

WORKDIR /app

# 1) Сначала только манифесты — для кеша
COPY package.json ./
COPY package-lock.json* ./

# 2) Детерминированная установка
RUN npm ci --no-audit --no-fund

# 3) Потом исходники
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
