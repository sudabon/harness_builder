FROM node:22-alpine

WORKDIR /app

RUN corepack enable

COPY package.json ./
RUN pnpm install

COPY . .

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "5173"]
