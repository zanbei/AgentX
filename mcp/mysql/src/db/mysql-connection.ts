import mysql from "mysql2/promise";
import type {
  Connection,
  RowDataPacket,
  ResultSetHeader,
  ProcedureCallPacket,
  FieldPacket,
} from "mysql2";
import type { MySQLConfig } from "../config";

type QueryResult =
  | RowDataPacket[]
  | RowDataPacket[][]
  | ResultSetHeader
  | ResultSetHeader[]
  | ProcedureCallPacket<any>;

interface SlowQueryLogRecord {
  start_time: Date;
  user_host: string;
  query_time: string; // Typically HH:MM:SS string from TIME type
  lock_time: string; // Typically HH:MM:SS string from TIME type
  rows_sent: number;
  rows_examined: number;
  db: string | null; // Can be null if no default database was selected
  sql_text: string;
  thread_id: number;
}

export class MySQLConnection {
  private connection: mysql.Connection | null = null;
  private config: MySQLConfig;

  constructor(config: MySQLConfig) {
    this.config = config;
  }

  async connect(): Promise<mysql.Connection> {
    if (!this.connection) {
      this.connection = await mysql.createConnection({
        host: this.config.host,
        port: this.config.port,
        user: this.config.user,
        password: this.config.password,
        database: this.config.database,
      });
      console.log("Connected to MySQL database");
    }
    return this.connection;
  }

  async disconnect(): Promise<void> {
    if (this.connection) {
      await this.connection.end();
      this.connection = null;
      console.log("Disconnected from MySQL database");
    }
  }

  async query<T>(sql: string, params: any[] = []): Promise<T[]> {
    const conn = await this.connect();
    try {
      const [rows] = await conn.query(sql, params);
      return rows as T[];
    } catch (error) {
      console.error("Error executing query:", error);
      throw error;
    }
  }

  async queryAsString(sql: string, params: any[] = []): Promise<string> {
    const conn = await this.connect();
    try {
      const [results]: [QueryResult, FieldPacket[]] = await conn.query(
        sql,
        params,
      );
      return this.resultToString(results);
    } catch (error: any) {
      const err = { error: true, message: error.message };
      return JSON.stringify(err, null, 2);
    }
  }

  async getDatabases(): Promise<string[]> {
    const results = await this.query<{ Database: string }>("SHOW DATABASES");
    return results.map((row) => row.Database);
  }

  async getTables(database: string): Promise<string[]> {
    const results = await this.query<{ Tables_in_db: string }>(
      `SHOW TABLES FROM \`${database}\``,
    );
    return results.map((row) => Object.values(row)[0] as string);
  }

  async getTableDDL(database: string, table: string): Promise<string> {
    const results = await this.query<{ Table: string; "Create Table": string }>(
      `SHOW CREATE TABLE \`${database}\`.\`${table}\``,
    );

    if (results.length === 0) {
      throw new Error(`Table ${database}.${table} not found`);
    }

    return results[0]["Create Table"] as string;
  }

  async getTableCount(database?: string): Promise<number> {
    if (database) {
      const tables = await this.getTables(database);
      return tables.length;
    } else {
      // Count tables across all databases
      const databases = await this.getDatabases();
      let totalTables = 0;

      for (const db of databases) {
        // Skip system databases
        if (
          ["information_schema", "mysql", "performance_schema", "sys"].includes(
            db,
          )
        ) {
          continue;
        }

        const tables = await this.getTables(db);
        totalTables += tables.length;
      }

      return totalTables;
    }
  }

  async getTableRowCount(database: string, table: string): Promise<number> {
    const results = await this.query<{ count: number }>(
      `SELECT COUNT(*) as count FROM \`${database}\`.\`${table}\``,
    );
    return results[0].count;
  }

  async getTotalRowCount(database?: string): Promise<number> {
    let totalRows = 0;

    if (database) {
      const tables = await this.getTables(database);

      for (const table of tables) {
        try {
          const rowCount = await this.getTableRowCount(database, table);
          totalRows += rowCount;
        } catch (error) {
          console.error(`Error counting rows in ${database}.${table}:`, error);
        }
      }
    } else {
      const databases = await this.getDatabases();

      for (const db of databases) {
        // Skip system databases
        if (
          ["information_schema", "mysql", "performance_schema", "sys"].includes(
            db,
          )
        ) {
          continue;
        }

        try {
          const dbRowCount = await this.getTotalRowCount(db);
          totalRows += dbRowCount;
        } catch (error) {
          console.error(`Error counting rows in database ${db}:`, error);
        }
      }
    }

    return totalRows;
  }

  async getTopNTables(
    database: string,
    n: number = 10,
  ): Promise<Array<{ table: string; size: number; unit: string }>> {
    const query = `
      SELECT
        table_name AS \`table\`,
        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
      FROM
        information_schema.TABLES
      WHERE
        table_schema = ?
      ORDER BY
        size_mb DESC
      LIMIT ?
    `;

    const results = await this.query<{ table: string; size_mb: number }>(
      query,
      [database, n],
    );

    return results.map((row) => ({
      table: row.table,
      size: row.size_mb,
      unit: "MB",
    }));
  }

  async getSlowQueries(
    startTime?: string,
    endTime?: string,
    limit: number = 10,
  ): Promise<string> {
    let query = `
          SELECT
            start_time,
            user_host,
            query_time,
            lock_time,
            rows_sent,
            rows_examined,
            db,
            sql_text,
            thread_id
          FROM
            mysql.slow_log
          WHERE 1=1`;

    // The params array type needs to be updated to accept strings or numbers
    const params: (string | number)[] = [];

    if (startTime) {
      query += ` AND start_time >= ?`;
      params.push(startTime); // Push string directly
    }

    if (endTime) {
      query += ` AND start_time <= ?`;
      params.push(endTime); // Push string directly
    }

    // Default order by start time descending
    query += ` ORDER BY start_time DESC`;

    if (limit !== undefined && limit > 0) {
      query += ` LIMIT ?`;
      params.push(limit);
    }

    try {
      const results = await this.query<SlowQueryLogRecord>(query, params);
      return JSON.stringify(results, null, 2);
    } catch (error) {
      console.error("Error fetching slow queries:", error);
      throw error;
    }
  }

  private resultToString(result: QueryResult): string {
    try {
      if (Array.isArray(result)) {
        // 处理 RowDataPacket[] 或 RowDataPacket[][]
        if (result.length === 0) {
          return "[]"; // 空数组
        }
        if (Array.isArray(result[0])) {
          // 多语句查询或 rowsAsArray，返回 RowDataPacket[][]
          return JSON.stringify(result, null, 2);
        }
        // 单语句 SELECT，返回 RowDataPacket[]
        return JSON.stringify(result, null, 2);
      } else if ("affectedRows" in result) {
        // 处理 ResultSetHeader
        return JSON.stringify(
          {
            affectedRows: result.affectedRows,
            insertId: result.insertId,
            info: result.info,
            warningStatus: result.warningStatus,
            changedRows: result.changedRows,
          },
          null,
          2,
        );
      } else {
        // 其他类型（如 ProcedureCallPacket），直接序列化
        return JSON.stringify(result, null, 2);
      }
    } catch (error: any) {
      return `Error converting result to string: ${error.message}`;
    }
  }
}
