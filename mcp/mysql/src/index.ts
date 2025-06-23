#!/usr/bin/env bun
import { program } from "commander";
import express from "express";
import { randomUUID } from "node:crypto";
import { MySQLMCPServer } from "./mcp/server";
import { ensureConfigFile } from "./config";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";

async function initServerWithStreamableHttpTransport(
  server: MySQLMCPServer,
  port: number = 3000,
): Promise<void> {
  const app = express();
  app.use(express.json());

  const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

  app.post("/mcp", async (req, res) => {
    // Check for existing session ID
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    let transport: StreamableHTTPServerTransport;

    if (sessionId && transports[sessionId]) {
      // Reuse existing transport
      transport = transports[sessionId];
    } else if (!sessionId && isInitializeRequest(req.body)) {
      // New initialization request
      //
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        onsessioninitialized: (sessionId) => {
          // Store the transport by session ID
          transports[sessionId] = transport;
        },
      });

      // Clean up transport when closed
      transport.onclose = () => {
        if (transport.sessionId) {
          delete transports[transport.sessionId];
        }
      };

      // Connect to the MCP server
      await server.connect(transport);
    } else {
      // Invalid request
      res.status(400).json({
        jsonrpc: "2.0",
        error: {
          code: -32000,
          message: "Bad Request: No valid session ID provided",
        },
        id: null,
      });
      return;
    }

    // Handle the request
    await transport.handleRequest(req, res, req.body);
  });

  // Reusable handler for GET and DELETE requests
  const handleSessionRequest = async (
    req: express.Request,
    res: express.Response,
  ) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId || !transports[sessionId]) {
      res.status(400).send("Invalid or missing session ID");
      return;
    }

    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
  };

  // Handle GET requests for server-to-client notifications via SSE
  app.get("/mcp", handleSessionRequest);

  // Handle DELETE requests for session termination
  app.delete("/mcp", handleSessionRequest);

  app.listen(port);
}

// Ensure config file exists
ensureConfigFile();

program
  .name("mysql-mcp-server")
  .description("MySQL MCP Server for interacting with MySQL databases")
  .version("1.0.0");

program
  .option("-t, --transport <type>", "Transport type (stdio or http)", "stdio")
  .option("-p, --port <port>", "HTTP server port (for http transport)", "3000")
  .action(async (options: { transport: string; port: string }) => {
    // Set environment variables based on command line options
    process.env.TRANSPORT_TYPE = options.transport;
    process.env.SERVER_PORT = options.port;

    console.log(
      `Starting MySQL MCP Server with ${options.transport} transport at ${options.port}`,
    );

    const server = new MySQLMCPServer();

    if (options.transport == "stdio") {
      const transport = new StdioServerTransport();
      server.connect(transport);
    } else if (options.transport == "http") {
      await initServerWithStreamableHttpTransport(server);
    }
  });

program.parse(process.argv);
