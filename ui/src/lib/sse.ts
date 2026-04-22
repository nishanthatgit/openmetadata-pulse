/**
 * SSE (Server-Sent Events) client utility.
 * Connects to the Pulse API SSE stream for real-time dashboard updates.
 */

export interface PulseEvent {
  eventType: string;
  entityType: string;
  entityFQN: string;
  timestamp: string;
  details?: Record<string, unknown>;
}

export function createSSEConnection(
  url: string,
  onEvent: (event: PulseEvent) => void,
  onError?: (error: Event) => void,
): EventSource {
  const source = new EventSource(url);

  source.onmessage = (e: MessageEvent) => {
    try {
      const data: PulseEvent = JSON.parse(e.data);
      onEvent(data);
    } catch {
      console.warn('Failed to parse SSE event:', e.data);
    }
  };

  source.onerror = (e: Event) => {
    console.error('SSE connection error:', e);
    onError?.(e);
  };

  return source;
}
