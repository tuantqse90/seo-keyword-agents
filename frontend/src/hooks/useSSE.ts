"use client";

import { useState, useCallback, useRef } from "react";

interface UseSSEReturn {
  content: string;
  isStreaming: boolean;
  error: string | null;
  reportId: string | null;
  startStream: (streamUrl: string, reportId: string) => void;
  reset: () => void;
}

export function useSSE(): UseSSEReturn {
  const [content, setContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reportId, setReportId] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const reset = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setContent("");
    setIsStreaming(false);
    setError(null);
    setReportId(null);
  }, []);

  const startStream = useCallback((streamUrl: string, rid: string) => {
    reset();
    setIsStreaming(true);
    setReportId(rid);

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "";
    const es = new EventSource(`${apiBase}${streamUrl}`);
    eventSourceRef.current = es;

    es.addEventListener("chunk", (e) => {
      setContent((prev) => prev + e.data);
    });

    es.addEventListener("done", () => {
      setIsStreaming(false);
      es.close();
    });

    es.addEventListener("error", (e) => {
      const messageEvent = e as MessageEvent;
      setError(messageEvent.data || "Stream error");
      setIsStreaming(false);
      es.close();
    });

    es.onerror = () => {
      if (es.readyState === EventSource.CLOSED) {
        setIsStreaming(false);
      }
    };
  }, [reset]);

  return { content, isStreaming, error, reportId, startStream, reset };
}
