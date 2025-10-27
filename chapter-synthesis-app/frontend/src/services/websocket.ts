import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<Function>> = new Map();

  connect(userId: string) {
    if (this.socket?.connected) {
      return;
    }

    this.socket = io('/ws', {
      path: '/ws/socket.io',
      auth: {
        user_id: userId,
      },
      transports: ['websocket', 'polling'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    // Set up event listeners
    this.socket.on('indexing_progress', (data) => {
      this.emit('indexing_progress', data);
    });

    this.socket.on('generation_progress', (data) => {
      this.emit('generation_progress', data);
    });

    this.socket.on('section_chunk', (data) => {
      this.emit('section_chunk', data);
    });

    this.socket.on('dashboard_update', (data) => {
      this.emit('dashboard_update', data);
    });

    this.socket.on('notification', (data) => {
      this.emit('notification', data);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  subscribeToJob(jobId: string) {
    if (this.socket) {
      this.socket.emit('subscribe_to_job', { job_id: jobId });
    }
  }

  unsubscribeFromJob(jobId: string) {
    if (this.socket) {
      this.socket.emit('unsubscribe_from_job', { job_id: jobId });
    }
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        callbacks.delete(callback);
      }
    };
  }

  off(event: string, callback?: Function) {
    if (callback) {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        callbacks.delete(callback);
      }
    } else {
      this.listeners.delete(event);
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach((callback) => callback(data));
    }
  }
}

export const wsService = new WebSocketService();
