import { tool } from "ai";
import { z } from "zod";
import { QUERY_DB_TOOL_DESCRIPTION } from "../prompts";
import { sql } from "@/providers/db";

export const queryDatabase = tool({
  description: QUERY_DB_TOOL_DESCRIPTION,
  parameters: z.object({
    query: z.string().describe("SQL query to execute."),
  }),
  execute: async ({ query }) => {
    console.log("QUERY:", query);

    try {
      // Execute the raw SQL query using sql.unsafe()
      const result = await sql.unsafe(query);
      return JSON.stringify({
        query: query,
        result: result, // returns an array of rows
      });
    } catch (error) {
      console.error("Error executing query:", error);
      throw new Error(String(error));
    }
  },
});