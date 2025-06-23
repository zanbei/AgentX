import { config } from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';

// Load environment variables from .env file
config();

export interface MySQLConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database?: string;
}

export interface ServerConfig {
  port: number;
  transport: 'stdio' | 'http';
}

export function loadMySQLConfig(): MySQLConfig {
  return {
    host: process.env.MYSQL_HOST || 'localhost',
    port: parseInt(process.env.MYSQL_PORT || '3306', 10),
    user: process.env.MYSQL_USER || 'root',
    password: process.env.MYSQL_PASSWORD || '',
    database: process.env.MYSQL_DATABASE,
  };
}

export function loadServerConfig(): ServerConfig {
  return {
    port: parseInt(process.env.SERVER_PORT || '3000', 10),
    transport: (process.env.TRANSPORT_TYPE || 'stdio') as 'stdio' | 'http',
  };
}

// Create a sample .env file if it doesn't exist
export function ensureConfigFile(): void {
  const envPath = path.join(process.cwd(), '.env');
  
  if (!fs.existsSync(envPath)) {
    const sampleEnv = `# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=

# Server Configuration
SERVER_PORT=3000
TRANSPORT_TYPE=stdio  # 'stdio' or 'http'
`;
    
    fs.writeFileSync(envPath, sampleEnv);
    console.log('Created sample .env file. Please update with your MySQL credentials.');
  }
}
