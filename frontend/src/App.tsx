// frontend/src/App.tsx
import React, { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  Typography,
  AppBar,
  Toolbar,
  Box,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface QueryResponse {
  sql: string;
  result: {
    columns: string[];
    rows: any[][];
    types?: string[];
    plot?: boolean;
  } | null;
  ambiguity?: string | null;
  error?: string | null;
}
const App = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [sql, setSql] = useState('');
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<any[][]>([]);
  const [error, setError] = useState('');
  const [ambiguity, setAmbiguity] = useState('');
  const [plot, setPlot] = useState(false);

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
    setAmbiguity('');
    setPlot(false);

    try {
      const res = await fetch('http://localhost:7861/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data: QueryResponse = await res.json();
      console.log("data", data)
      console.log("data.result", data.result)      


      if (data.ambiguity) {
        setAmbiguity(data.ambiguity);
        setLoading(false);
        return;
      }

      if (data.error) {
        setError(data.error);
        setLoading(false);
        return;
      }

      setSql(data.sql || '');

      if (data.result && Array.isArray(data.result.columns) && Array.isArray(data.result.rows)) {
        setColumns(data.result.columns);
        setRows(data.result.rows);
        setPlot(data.result.plot || false);
      } else {
        setColumns([]);
        setRows([]);
      }
    } catch (err: any) {
      setError('Failed to fetch result. See console.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">Talkt to Tables</Typography>
        </Toolbar>
      </AppBar>

      <Container sx={{ mt: 4, mb: 4 }}>
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
            Submit
          </Button>
        </Box>

        {loading && <CircularProgress sx={{ mt: 2 }} />}

        {ambiguity && (
          <Alert severity="warning" sx={{ mt: 2, whiteSpace: 'pre-line' }}>
            {ambiguity}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {sql && (
          <Box mt={4}>
            <Typography variant="subtitle1" gutterBottom>
              Generated SQL:
            </Typography>
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
            <Typography variant="subtitle1" gutterBottom>
              Query Results:
            </Typography>

            <TableContainer component={Paper}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {columns.map((col) => (
                      <TableCell key={col}>{col}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rows.map((row, i) => (
                    <TableRow key={i}>
                      {row.map((cell, j) => (
                        <TableCell key={j}>{cell?.toString() ?? ''}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {columns.length >= 2 && rows.length > 0 && plot && (
        <Box mt={4}>
          <Typography variant="subtitle1" gutterBottom>
            Chart:
          </Typography>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={rows.map((row) => ({
                [columns[0]]: row[0],
                [columns[1]]: row[1],
              }))}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={columns[0]} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey={columns[1]}
                stroke="#8884d8"
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      )}
        
      </Container>
    </>
  );
};

export default App;
