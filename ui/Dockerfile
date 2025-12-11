FROM node:24-alpine3.21

WORKDIR /app
COPY package*.json ./
EXPOSE 5173
COPY . .
RUN npm install
CMD ["npm", "run", "dev"]
