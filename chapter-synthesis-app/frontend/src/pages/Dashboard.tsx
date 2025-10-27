import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Button,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import {
  Description,
  Article,
  CloudUpload,
  Assessment,
  Logout,
  Add,
} from '@mui/icons-material';
import { dashboardAPI } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { wsService } from '@/services/websocket';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [liveMetrics, setLiveMetrics] = useState<any>(null);

  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await dashboardAPI.getMetrics();
      return response.data;
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const { data: costAnalysis } = useQuery({
    queryKey: ['cost-analysis'],
    queryFn: async () => {
      const response = await dashboardAPI.getCostAnalysis();
      return response.data;
    },
  });

  useEffect(() => {
    // Listen for real-time dashboard updates
    const unsubscribe = wsService.on('dashboard_update', (data) => {
      setLiveMetrics(data);
    });

    return () => unsubscribe();
  }, []);

  const displayMetrics = liveMetrics || metrics;

  if (isLoading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📊 Chapter Synthesis Platform - Observability Dashboard
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user?.username}
          </Typography>
          <IconButton color="inherit" onClick={logout}>
            <Logout />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* System Health */}
        <Paper
          sx={{
            p: 3,
            mb: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          }}
        >
          <Typography variant="h5" gutterBottom>
            🎛️ System Health - Real-Time Monitoring
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={3}>
              <Typography variant="body2">System Health</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <LinearProgress
                  variant="determinate"
                  value={displayMetrics?.system_health?.health_score || 0}
                  sx={{ flexGrow: 1, mr: 1, height: 10, borderRadius: 5 }}
                />
                <Typography variant="h6">
                  {displayMetrics?.system_health?.health_score || 0}%
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2">Active Processes</Typography>
              <Typography variant="h5">
                {displayMetrics?.active_jobs?.length || 0}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2">Cache Hit Rate</Typography>
              <Typography variant="h5">
                {Math.round((displayMetrics?.cache?.avg_hits_per_entry || 0) * 10)}%
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2">Response Time</Typography>
              <Typography variant="h5">
                {(displayMetrics?.jobs?.avg_time_seconds || 0).toFixed(1)}s avg
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Quick Actions */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<Add />}
              onClick={() => navigate('/generate')}
              sx={{ height: 80 }}
            >
              Generate New Chapter
            </Button>
          </Grid>
          <Grid item xs={12} md={6}>
            <Button
              fullWidth
              variant="outlined"
              size="large"
              startIcon={<CloudUpload />}
              onClick={() => navigate('/documents')}
              sx={{ height: 80 }}
            >
              Upload Document
            </Button>
          </Grid>
        </Grid>

        {/* Metrics Cards */}
        <Grid container spacing={3}>
          {/* Documents */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Description sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                  <div>
                    <Typography variant="h4">{displayMetrics?.documents?.total || 0}</Typography>
                    <Typography color="text.secondary">Documents</Typography>
                  </div>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ✅ Indexed: {displayMetrics?.documents?.indexed || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ⏳ Processing: {displayMetrics?.documents?.processing || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Chapters */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Article sx={{ fontSize: 40, mr: 2, color: 'secondary.main' }} />
                  <div>
                    <Typography variant="h4">{displayMetrics?.chapters?.total || 0}</Typography>
                    <Typography color="text.secondary">Chapters</Typography>
                  </div>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ✅ Completed: {displayMetrics?.chapters?.completed || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  🔄 Generating: {displayMetrics?.chapters?.generating || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ⭐ Avg Quality: {displayMetrics?.chapters?.avg_quality_score || 0}/100
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Jobs */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Assessment sx={{ fontSize: 40, mr: 2, color: 'success.main' }} />
                  <div>
                    <Typography variant="h4">
                      {displayMetrics?.jobs?.total_last_30_days || 0}
                    </Typography>
                    <Typography color="text.secondary">Jobs (30d)</Typography>
                  </div>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ✅ Completed: {displayMetrics?.jobs?.completed || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  🔄 Running: {displayMetrics?.jobs?.running || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ❌ Failed: {displayMetrics?.jobs?.failed || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Cache & Cost */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  💰 Cost Optimization
                </Typography>
                <Typography variant="h4" color="primary">
                  ${costAnalysis?.total_cost?.toFixed(2) || '0.00'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last 30 days
                </Typography>
                <Typography variant="body2" color="success.main">
                  ⚡ Saved: ${costAnalysis?.total_savings?.toFixed(2) || '0.00'} (
                  {costAnalysis?.savings_percentage || 0}%)
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cache Hit Rate: {Math.round(costAnalysis?.avg_cache_hit_rate * 100 || 0)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Active Jobs */}
        {displayMetrics?.active_jobs && displayMetrics.active_jobs.length > 0 && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              🔴 LIVE - Active Jobs
            </Typography>
            {displayMetrics.active_jobs.map((job: any) => (
              <Box key={job.job_id} sx={{ mb: 2 }}>
                <Typography variant="body2">
                  {job.job_type} - {job.current_stage}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinearProgress
                    variant="determinate"
                    value={job.progress}
                    sx={{ flexGrow: 1, mr: 2 }}
                  />
                  <Typography variant="body2">{Math.round(job.progress)}%</Typography>
                </Box>
              </Box>
            ))}
          </Paper>
        )}

        {/* Navigation */}
        <Grid container spacing={2} sx={{ mt: 3 }}>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/documents')}
              startIcon={<Description />}
            >
              Manage Documents
            </Button>
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/chapters')}
              startIcon={<Article />}
            >
              View All Chapters
            </Button>
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/generate')}
              startIcon={<Add />}
            >
              Generate Chapter
            </Button>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
