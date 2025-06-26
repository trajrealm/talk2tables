// webapp/src/pages/ConversePage.tsx

import React, { useState, useEffect } from 'react';
import {
  Box, Button, Container, TextField, Typography, Alert, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip, Legend } from 'recharts';
import ReactMarkdown from 'react-markdown';

import Header from '../components/Header';
import Footer from '../components/Footer';
import ConnectedDbInfo from '../components/ConnectedDbInfo';
import { BACKEND_URL } from '../utils/constants';
import { decodeToken } from '../utils/auth';

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
  const [userEmail, setUserEmail] = useState('');
  const [dbInfo, setDbInfo] = useState<any>(null);
  const [dbInfoLoading, setDbInfoLoading] = useState(true);

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
      const res = await fetch(`${BACKEND_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ query, history: conversation, db_id: dbId }),
      });

      const data: QueryResponse = await res.json();

      setConversation((prev) => [
        ...prev,
        { user: query, bot: data.ambiguity_msg || data.sql || data.error || 'No response' },
      ]);

      if (!res.ok || data.error) {
        throw new Error(data.error || 'Something went wrong');
      }

      setSql(data.sql || '');
      if (data.result) {
        setColumns(data.result.columns || []);
        setRows(data.result.rows || []);
        setPlot(data.result.plot || false);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch result.');
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
    fetch(`${BACKEND_URL}/get_user_database/${dbId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setDbInfo(data))
      .catch((err) => console.error('Failed to load DB info:', err))
      .finally(() => setDbInfoLoading(false));
  }, [dbId]);

  return (
    <>
      <Header
        userEmail={userEmail}
        centerButton={
          <Button variant="outlined" color="inherit" onClick={() => navigate("/dashboard")}>
            Back to Dashboard
          </Button>
        }
      />

      <Container sx={{ mt: 4, mb: 6 }}>
        {/* DB Info */}
        <ConnectedDbInfo dbInfo={dbInfo} loading={dbInfoLoading} />

        {/* Conversation History */}
        <Box mt={2} sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>Conversation History</Typography>
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
                <Typography sx={{ color: 'primary.main' }}>
                  <strong>User:</strong> 
                  <span style={{ color: '#333' }}>{entry.user}</span>
                </Typography>
                <Typography sx={{ color: 'secondary.main' }}>
                  <strong>genSQL:</strong> 
                  <span style={{ color: 'secondary.main' }}>{entry.bot}</span>                
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
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {/* {sql && (
          <Box mt={4}>
            <Typography variant="subtitle1">Generated SQL:</Typography>
            <Box sx={{ fontFamily: 'monospace', p: 2, backgroundColor: '#f0f0f0', borderRadius: 1 }}>
              {sql}
            </Box>
          </Box>
        )} */}

        {columns.length > 0 && (
          <Box mt={4}>
            <Typography variant="subtitle1">Query Results:</Typography>
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
            <Typography variant="subtitle1">Chart:</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={rows.map((row) => ({
                [columns[0]]: row[0],
                [columns[1]]: row[1],
              }))}>
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

      <Footer />
    </>
  );
};

export default ConversePage;
