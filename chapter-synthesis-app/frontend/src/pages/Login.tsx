import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
} from '@mui/material';
import { useAuthStore } from '@/store/authStore';

export default function Login() {
  const navigate = useNavigate();
  const { login, error } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(username, password);
      navigate('/');
    } catch (error) {
      // Error is handled by store
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h4" align="center" gutterBottom>
            📚 Chapter Synthesis Platform
          </Typography>
          <Typography variant="subtitle1" align="center" color="text.secondary" gutterBottom>
            Advanced AI-Powered Medical Knowledge Synthesis
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
              autoFocus
            />

            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{ mt: 3, mb: 2 }}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>

            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2">
                Don't have an account?{' '}
                <Link component={RouterLink} to="/register">
                  Register here
                </Link>
              </Typography>
            </Box>
          </Box>

          <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
            <Typography variant="caption" display="block" gutterBottom>
              🚀 Key Features:
            </Typography>
            <Typography variant="caption" display="block">
              • ⚡ Smart Caching (30-50% faster)
            </Typography>
            <Typography variant="caption" display="block">
              • 📡 Real-time Streaming Generation
            </Typography>
            <Typography variant="caption" display="block">
              • 🔄 Version Control & Rollback
            </Typography>
            <Typography variant="caption" display="block">
              • 🧠 AI-Powered Gap Detection
            </Typography>
            <Typography variant="caption" display="block">
              • 📊 Live Observability Dashboard
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
