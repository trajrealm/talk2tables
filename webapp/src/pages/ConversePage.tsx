import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Avatar,
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Menu,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip, Legend, ResponsiveContainer,
} from 'recharts';
import ReactMarkdown from 'react-markdown';
import StorageIcon from '@mui/icons-material/Storage';
import DnsIcon from '@mui/icons-material/Dns';
import PublicIcon from '@mui/icons-material/Public';
import PermIdentityIcon from '@mui/icons-material/PermIdentity';
import LanIcon from '@mui/icons-material/Lan';
import AccountTreeIcon from '@mui/icons-material/AccountTree';


interface QueryResponse {
  sql: string;
  result: {
    columns: string[];
    rows: any[][];
    types?: string[];
    plot?: boolean;
  } | null;
  ambiguity_msg: string;
  error?: string | null;
}

function decodeToken(token: string | null): string {
  if (!token) return '';
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub || '';
  } catch (e) {
    return '';
  }
}

const ConversePage = () => {
  const { id: dbId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [sql, setSql] = useState('');
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<any[][]>([]);
  const [error, setError] = useState('');
  const [ambiguityMsg, setAmbiguityMsg] = useState('');
  const [conversation, setConversation] = useState<{ user: string; bot: string }[]>([]);
  const [plot, setPlot] = useState(false);
  const [showAllRows, setShowAllRows] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [userEmail, setUserEmail] = useState('');
  const [dbInfo, setDbInfo] = useState<any>(null);
  const [dbInfoLoading, setDbInfoLoading] = useState(true);

  const handleAvatarClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleAvatarClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
  };

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a query.');
      return;
    }

    setLoading(true);
    setError('');
    setSql('');
    setColumns([]);
    setRows([]);
    setAmbiguityMsg('');
    setShowAllRows(false);

    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ query, history: conversation, db_id: dbId }),
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data: QueryResponse = await res.json();

      setConversation((prev) => [
        ...prev,
        { user: query, bot: data.ambiguity_msg || data.sql || data.error || 'No response' },
      ]);

      if (data.ambiguity_msg) {
        setAmbiguityMsg(data.ambiguity_msg);
        setLoading(false);
        return;
      }

      if (data.error) {
        setError(data.error);
        setLoading(false);
        return;
      }

      setSql(data.sql || '');
      if (data.result) {
        setColumns(data.result.columns || []);
        setRows(data.result.rows || []);
        setPlot(data.result.plot || false);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch result.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!dbId || !token) return;

    const email = decodeToken(token);
    setUserEmail(email);

    setDbInfoLoading(true);
    fetch(`http://localhost:8000/get_user_database/${dbId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setDbInfo(data))
      .catch((err) => console.error('Failed to load DB info:', err))
      .finally(() => setDbInfoLoading(false));
  }, [dbId]);

  return (
    <>
      {/* Header */}
      <AppBar position="static" sx={{ mb: 4 }}>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          {/* Logo */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <img src="/logo.svg" alt="Logo" style={{ height: 40, marginRight: 10 }} />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              {/* Table Converse */}
            </Typography>
          </Box>

          {/* Center: Back */}
          <Button variant="outlined" color="inherit" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>

          {/* Right: Nav + Avatar */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button color="inherit" onClick={() => navigate('/')}>Home</Button>
            <Button color="inherit" onClick={() => navigate('/about')}>About</Button>
            <Button color="inherit" onClick={() => navigate('/contact')}>Contact</Button>

            <Tooltip title="Account">
              <IconButton onClick={handleAvatarClick} sx={{ ml: 2 }}>
                <Avatar sx={{ bgcolor: '#00bfa5' }}>{userEmail.charAt(0).toUpperCase()}</Avatar>
              </IconButton>
            </Tooltip>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleAvatarClose}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
              <MenuItem disabled>{userEmail}</MenuItem>
              <MenuItem onClick={handleAvatarClose}>Profile</MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main */}
      <Container sx={{ mb: 6 }}>
        {/* DB Info */}
        {dbInfoLoading ? (
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={20} /> <Typography>Loading database info...</Typography>
          </Box>
        ) : dbInfo ? (
            <Box
            sx={{
              position: 'relative',
              border: '1px solid #ccc',
              borderRadius: 2,
              backgroundColor: '#fafafa',
              px: 2,
              py: 1.5,
              mb: 3,
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: '-10px',
                left: 16,
                backgroundColor: '#fafafa',
                px: 1,
                fontSize: '0.8rem',
                fontWeight: 'bold',
                color: 'text.secondary',
              }}
            >
              Connected DB
            </Box>
        
            <Box
              sx={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 2,
                alignItems: 'center',
                fontSize: '0.85rem',
                color: 'text.secondary',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <StorageIcon fontSize="small" sx={{ color: '#1976d2' }} /> <span><strong>Name:</strong> {dbInfo.name}</span>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <DnsIcon fontSize="small" sx={{ color: '#388e3c' }} /> <span><strong>Type:</strong> {dbInfo.db_type}</span>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <PublicIcon fontSize="small" sx={{ color: '#f57c00' }} /> <span><strong>Host:</strong> {dbInfo.host}</span>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <LanIcon fontSize="small" sx={{ color: '#d32f2f' }} /> <span><strong>Port:</strong> {dbInfo.port}</span>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <PermIdentityIcon fontSize="small" sx={{ color: '#7b1fa2' }} /> <span><strong>User:</strong> {dbInfo.username}</span>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <AccountTreeIcon fontSize="small"sx={{ color: '#00796f' }} /> <span><strong>Schema:</strong> {dbInfo.schema}</span>
              </Box>
            </Box>
          </Box>            
        
        ) : (
          <Alert severity="error">Failed to load database info.</Alert>
        )}

        {/* Conversation History */}
        <Box mt={2} sx={{ position: 'relative', mb: 3 }}>
          <Box
            sx={{
              position: 'absolute',
              top: '-8px',
              left: 16,
              backgroundColor: '#fff',
              px: 1,
              fontSize: '0.9rem',
              color: '#555',
            }}
          >
            Conversation History
          </Box>
          <Box
            sx={{
              maxHeight: 300,
              overflowY: 'auto',
              backgroundColor: '#f9f9f9',
              p: 2,
              border: '1px solid #ddd',
              borderRadius: 2,
            }}
          >
            {conversation.map((entry, index) => (
              <Box key={index} mb={2}>
                <Typography><strong>User:</strong> {entry.user}</Typography>
                <Typography>
                  <strong><Box component="span" sx={{ color: '#ff9100' }}>gAIndelf:</Box></strong>{' '}
                  <Box component="span" sx={{ color: '#00bfa5' }}>{entry.bot}</Box>
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>

        {/* Query input */}
        <TextField
          fullWidth
          label="Enter natural language query"
          variant="outlined"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !loading) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          disabled={loading}
        />
        <Box mt={2}>
          <Button variant="contained" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Running...' : 'Submit'}
          </Button>
        </Box>

        {loading && <CircularProgress sx={{ mt: 2 }} />}

        {ambiguityMsg && (
          <Alert severity="warning" sx={{ mt: 2, whiteSpace: 'pre-line' }}>
            <ReactMarkdown>{ambiguityMsg}</ReactMarkdown>
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {sql && (
          <Box mt={4}>
            <Typography variant="subtitle1" gutterBottom>Generated SQL:</Typography>
            <Box
              sx={{
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
                p: 2,
                backgroundColor: '#f0f0f0',
                borderRadius: 1,
              }}
            >
              {sql}
            </Box>
          </Box>
        )}

        {columns.length > 0 && (
          <Box mt={4}>
            <Typography variant="subtitle1" gutterBottom>Query Results:</Typography>
            <TableContainer component={Paper}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>{columns.map((col) => <TableCell key={col}>{col}</TableCell>)}</TableRow>
                </TableHead>
                <TableBody>
                  {(showAllRows ? rows : rows.slice(0, 8)).map((row, i) => (
                    <TableRow key={i}>
                      {row.map((cell, j) => <TableCell key={j}>{cell?.toString() ?? ''}</TableCell>)}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {rows.length > 8 && (
              <Box mt={1} textAlign="center">
                <Button onClick={() => setShowAllRows(!showAllRows)}>
                  {showAllRows ? 'Show Less ▲' : 'Show More ▼'}
                </Button>
              </Box>
            )}
          </Box>
        )}

        {columns.length >= 2 && rows.length > 0 && plot && (
          <Box mt={4}>
            <Typography variant="subtitle1" gutterBottom>Chart:</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={rows.map((row) => ({
                  [columns[0]]: row[0],
                  [columns[1]]: row[1],
                }))}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={columns[0]} />
                <YAxis />
                <ReTooltip />
                <Legend />
                <Line type="monotone" dataKey={columns[1]} stroke="#8884d8" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}
      </Container>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 2,
          px: 2,
          backgroundColor: (theme) =>
            theme.palette.mode === 'light' ? theme.palette.grey[200] : theme.palette.grey[800],
          textAlign: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          &copy; {new Date().getFullYear()} Table Converse. All rights reserved. {' '}
          | <Button size="small" onClick={() => navigate('/')}>Home</Button>
          <Button size="small" onClick={() => navigate('/about')}>About</Button>
          <Button size="small" onClick={() => navigate('/contact')}>Contact</Button>
        </Typography>
      </Box>
    </>
  );
};

export default ConversePage;
