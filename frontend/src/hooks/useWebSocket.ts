'use client'

import { useEffect, useRef, useCallback, useState } from 'react'
import { WSMessage } from '@/types'

interface UseWebSocketOptions {
  onMessage?: (message: WSMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  reconnect?: boolean
  reconnectInterval?: number
  maxRetries?: number
}

interface UseWebSocketReturn {
  isConnected: boolean
  lastMessage: WSMessage | null
  send: (data: unknown) => void
  connect: () => void
  disconnect: () => void
}

export function useWebSocket(
  projectId: string | null,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnect = true,
    reconnectInterval = 3000,
    maxRetries = 5,
  } = options

  const ws = useRef<WebSocket | null>(null)
  const retryCount = useRef(0)
  const reconnectTimeout = useRef<NodeJS.Timeout>()

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)

  const connect = useCallback(() => {
    if (!projectId) return
    
    // Clean up existing connection
    if (ws.current) {
      ws.current.close()
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    ws.current = new WebSocket(`${wsUrl}/api/v1/ws/${projectId}`)

    ws.current.onopen = () => {
      setIsConnected(true)
      retryCount.current = 0
      onOpen?.()
    }

    ws.current.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data)
        setLastMessage(message)
        onMessage?.(message)
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }

    ws.current.onclose = () => {
      setIsConnected(false)
      onClose?.()

      // Attempt reconnection
      if (reconnect && retryCount.current < maxRetries) {
        retryCount.current++
        reconnectTimeout.current = setTimeout(connect, reconnectInterval)
      }
    }

    ws.current.onerror = (error) => {
      onError?.(error)
    }
  }, [projectId, onMessage, onOpen, onClose, onError, reconnect, reconnectInterval, maxRetries])

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current)
    }
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
    setIsConnected(false)
  }, [])

  const send = useCallback((data: unknown) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket not connected')
    }
  }, [])

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    if (projectId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [projectId, connect, disconnect])

  return {
    isConnected,
    lastMessage,
    send,
    connect,
    disconnect,
  }
}
