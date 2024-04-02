# Use the official Node.js image as the base image
FROM node:lts-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the application's dependencies
RUN npm install

# Copy the rest of the application's code to the working directory
COPY . .

# Build the application
RUN npm run build

# Use the official Nginx image as the base image for the runtime stage
FROM nginx:stable-alpine

# Copy the build output to the Nginx image
COPY --from=0 /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 5173

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]