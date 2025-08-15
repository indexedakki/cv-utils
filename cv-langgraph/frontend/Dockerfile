# 1. Base image
FROM node:20-alpine
# 3. Set working directory
WORKDIR /usr/src/app

# 2. Install dependencies
COPY package*.json ./
RUN npm install

# 4. Copy source
COPY . .

# 5. Expose port & run
EXPOSE 3000
CMD ["npm", "run", "dev"]
