# 前端Dockerfile
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制包管理文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段 - 使用Nginx
FROM nginx:alpine

# 复制Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 从构建阶段复制构建文件
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]