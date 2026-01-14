const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export class ChatWebSocket {
  private ws: WebSocket | null = null
  private conversationId: string
  private token: string
  private onMessage: (data: any) => void
  private onError: (error: Event) => void

  constructor(
    conversationId: string,
    token: string,
    onMessage: (data: any) => void,
    onError: (error: Event) => void
  ) {
    this.conversationId = conversationId
    this.token = token
    this.onMessage = onMessage
    this.onError = onError
  }

  connect() {
    const wsUrl = `${WS_URL}/api/v1/conversations/${this.conversationId}/ws?token=${this.token}`
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
    }

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.onMessage(data)
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.onError(error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
    }
  }

  sendMessage(text: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ text }))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

