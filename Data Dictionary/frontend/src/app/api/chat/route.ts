// For streaming (we'll return a plain Response stream)
import { selectTable } from '../../api/chat/tools/selectTable';  // Import tool

async function fetchSchema(): Promise<any> {
  const requestBody = [
    {
      "type": "mysql",
      "url": "jdbc:mysql://localhost:3306/customers",
      "username": "root",
      "password": "vansh4542",
      "driverClassName": "com.mysql.cj.jdbc.Driver"
    },
    {
      "type": "postgres",
      "url": "jdbc:postgresql://localhost:5432/postgres",
      "username": "postgres",
      "password": "vansh4542",
      "driverClassName": "org.postgresql.Driver"
    }
  ];

  const response = await fetch('http://localhost:8081/api/metadata/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  console.log(response)

  return await response.json();
}

// ✅ ONLY HTTP methods here
export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    console.log('[CHAT-API] Incoming messages:', messages);

    // Fetch schema from metadata service
    let schemaData = null;
    try {
      schemaData = await fetchSchema();
      console.log('[CHAT-API] Schema fetched items=', Array.isArray(schemaData) ? schemaData.length : 'unknown');
    } catch (err) {
      console.error('[CHAT-API] fetchSchema error:', err);
    }

    const requestBody = {
      data: { messages, schema: schemaData },
      tools: { selectTable }
    };

    console.log('[CHAT-API] Sending AI backend request');
    const resp = await fetch(`http://localhost:8000/api/ai/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      throw new Error(`AI backend error: ${errText}`);
    }

    const json = await resp.json();
    const text = json.output || json.summary || '';

    // NEW: Send LLM output back to backend
    try {
      const backendResponse = await fetch('http://localhost:8081/api/metadata/llm-output', {  // Update endpoint as needed
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          llmOutput: text,
          metadata: schemaData,
          messages: messages,
          fullResponse: json  // Include full AI response if needed
        })
      });

      if (!backendResponse.ok) {
        console.error('[CHAT-API] Failed to save LLM output:', await backendResponse.text());
      } else {
        console.log(`[CHAT-API] LLM output saved to backend successfully ${requestBody.data.messages}`);
      }
    } catch (saveErr) {
      console.error('[CHAT-API] Error saving LLM output:', saveErr);
      // Don't fail the main flow - just log the error
    }

    // Stream ai-sdk compatible parts (code:json newline-separated)
    const encoder = new TextEncoder();
    const chunkSize = 256;
    const stream = new ReadableStream({
      start(controller) {
        for (let i = 0; i < text.length; i += chunkSize) {
          const chunk = text.slice(i, i + chunkSize);
          controller.enqueue(encoder.encode(`0:${JSON.stringify(chunk)}\n`));
        }
        controller.enqueue(encoder.encode(`d:${JSON.stringify({ finishReason: 'stop' })}\n`));
        controller.close();
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-transform',
        Connection: 'keep-alive'
      }
    });
  } catch (err) {
    console.error('Chat API error:', err);
    return Response.json({ error: 'Internal server error' }, { status: 500 });
  }
}
