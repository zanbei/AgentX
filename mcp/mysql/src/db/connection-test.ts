import { loadMySQLConfig } from "../config";
import { MySQLConnection } from "./mysql-connection";
import type { QueryResult } from "mysql2";

const mysql_conf = loadMySQLConfig();
console.log(mysql_conf);
const my_conn = new MySQLConnection(mysql_conf);

const catalog_ddl = await my_conn.getTableDDL("mydata", "catalog");
console.log(catalog_ddl);

const tables = await my_conn.getTables("mydata");
console.log(tables);

const databases = await my_conn.getDatabases();
console.log(databases);

const data = await my_conn.queryAsString(
  "SELECT count(*) total_num FROM mydata.catalog",
);
console.log(data);

const tableCount = await my_conn.getTableCount("mydata");
console.log(`database: mydata table count: ${tableCount}`);

const rowCount = await my_conn.getTotalRowCount();
console.log(`database: mydata total row count: ${rowCount}`);

const topNTables = await my_conn.getTopNTables("mydata");
console.log(
  `database: mydata topN tables: ${JSON.stringify(topNTables, null, 2)}`,
);

const slowLog = await my_conn.getSlowQueries(
  "2025-06-11 00:00:00",
  "2025-06-13 00:00:00",
  10,
);
console.log(slowLog);
