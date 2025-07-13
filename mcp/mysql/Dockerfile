# Use Bun as the base image
FROM oven/bun:latest

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json bun.lockb ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy all files
COPY . .

# Expose port (assuming the server runs on port 3000, adjust if different)
EXPOSE 3000

# Start the server
CMD ["bun", "run", "src/index.ts", "-t", "http"]
