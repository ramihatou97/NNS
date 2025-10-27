import { create } from 'zustand';
import { authAPI } from '@/services/api';
import { wsService } from '@/services/websocket';

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  preferences: any;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  updatePreferences: (preferences: any) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.login(username, password);
      const { access_token, user } = response.data;

      localStorage.setItem('access_token', access_token);
      set({
        token: access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
      });

      // Connect WebSocket
      wsService.connect(user.id.toString());
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      });
      throw error;
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await authAPI.register(data);
      set({ isLoading: false });
      // Auto-login after registration
      await get().login(data.username, data.password);
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    wsService.disconnect();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  fetchCurrentUser: async () => {
    if (!get().token) return;

    set({ isLoading: true });
    try {
      const response = await authAPI.getCurrentUser();
      set({ user: response.data, isLoading: false });

      // Connect WebSocket
      wsService.connect(response.data.id.toString());
    } catch (error) {
      set({ isLoading: false });
      get().logout();
    }
  },

  updatePreferences: async (preferences) => {
    try {
      await authAPI.updatePreferences(preferences);
      set((state) => ({
        user: state.user ? { ...state.user, preferences } : null,
      }));
    } catch (error) {
      console.error('Failed to update preferences:', error);
      throw error;
    }
  },
}));
