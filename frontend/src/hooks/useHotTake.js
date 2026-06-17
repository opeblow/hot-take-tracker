import { useState, useCallback, useRef } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config.js';

function isNetworkError(error) {
  return !error.response && error.code === 'ERR_NETWORK';
}

export default function useHotTake() {
  const [messages, setMessages] = useState([]);
  const [sendingStatement, setSendingStatement] = useState(false);
  const [fetchingHistory, setFetchingHistory] = useState(false);
  const [fetchingContradictions, setFetchingContradictions] = useState(false);
  const [error, setError] = useState(null);
  const [contradictions, setContradictions] = useState([]);
  const [userId, setUserId] = useState('');
  const [showSlowIndicator, setShowSlowIndicator] = useState(false);
  const slowTimerRef = useRef(null);
  const cancelTokenRef = useRef(null);

  const clearError = useCallback(() => setError(null), []);

  const startSlowTimer = useCallback(() => {
    slowTimerRef.current = setTimeout(() => setShowSlowIndicator(true), 4000);
  }, []);

  const stopSlowTimer = useCallback(() => {
    if (slowTimerRef.current) {
      clearTimeout(slowTimerRef.current);
      slowTimerRef.current = null;
    }
    setShowSlowIndicator(false);
  }, []);

  const submitStatement = useCallback(async (statement) => {
    if (!userId.trim()) {
      setError({ type: 'validation', message: 'Enter a user ID before submitting.' });
      return false;
    }

    setSendingStatement(true);
    setError(null);
    startSlowTimer();

    const source = axios.CancelToken.source();
    cancelTokenRef.current = source;

    try {
      const res = await axios.post(
        `${API_BASE_URL}/api/statement`,
        { user_id: userId.trim(), statement: statement.trim() },
        { cancelToken: source.token, timeout: 15000 },
      );

      setMessages((prev) => [
        ...prev,
        { role: 'user', content: statement.trim(), timestamp: new Date().toISOString() },
        {
          role: 'agent',
          content: res.data.reply,
          contradiction_detected: res.data.contradiction_detected,
          contradicted_opinion: res.data.contradicted_opinion,
          new_opinion: res.data.new_opinion,
          confidence: res.data.confidence,
          timestamp: new Date().toISOString(),
        },
      ]);

      stopSlowTimer();
      setSendingStatement(false);
      return true;
    } catch (err) {
      stopSlowTimer();
      setSendingStatement(false);

      if (axios.isCancel(err)) return false;

      if (isNetworkError(err)) {
        setError({
          type: 'network',
          message: "Can't reach the server. Check your connection and try again.",
        });
      } else if (err.response) {
        const status = err.response.status;
        const detail =
          err.response.data?.detail?.error ||
          err.response.data?.error ||
          err.response.data?.detail ||
          'An unexpected error occurred.';

        if (status === 503) {
          setError({
            type: 'walrus',
            message: detail,
          });
        } else if (status === 502) {
          setError({
            type: 'openai',
            message: 'The agent had trouble thinking that through. Try rephrasing?',
          });
        } else if (status === 422) {
          const validationMsg =
            typeof detail === 'string' ? detail : 'Invalid input. Check your message and try again.';
          setError({
            type: 'validation',
            message: validationMsg,
          });
        } else {
          setError({
            type: 'server',
            message: detail,
          });
        }
      } else {
        setError({
          type: 'unknown',
          message: 'Something went wrong. Please try again.',
        });
      }
      return false;
    }
  }, [userId, startSlowTimer, stopSlowTimer]);

  const fetchHistory = useCallback(async (uid) => {
    if (!uid.trim()) return;
    setFetchingHistory(true);
    setError(null);

    try {
      const res = await axios.get(`${API_BASE_URL}/api/history/${encodeURIComponent(uid.trim())}`, {
        timeout: 10000,
      });

      const opinions = res.data.opinions || [];
      const reconstructed = [];

      for (const op of opinions) {
        reconstructed.push({ role: 'user', content: op.statement, timestamp: op.timestamp });
        reconstructed.push({
          role: 'agent',
          content: '(restored from memory)',
          contradiction_detected: false,
          timestamp: op.timestamp,
        });
      }

      setMessages(reconstructed);
    } catch (err) {
      if (isNetworkError(err)) {
        setError({
          type: 'network',
          message: "Can't reach the server. Check your connection and try again.",
        });
      } else if (err.response?.status === 503) {
        setError({
          type: 'walrus',
          message: err.response.data?.detail?.error || 'Memory service unavailable.',
        });
      } else {
        setError({
          type: 'server',
          message: 'Failed to load history. Please try again.',
        });
      }
    } finally {
      setFetchingHistory(false);
    }
  }, []);

  const fetchContradictions = useCallback(async (uid) => {
    if (!uid.trim()) return;
    setFetchingContradictions(true);
    setError(null);

    try {
      const res = await axios.get(
        `${API_BASE_URL}/api/contradictions/${encodeURIComponent(uid.trim())}`,
        { timeout: 10000 },
      );
      setContradictions(res.data.contradictions || []);
    } catch (err) {
      if (isNetworkError(err)) {
        setError({
          type: 'network',
          message: "Can't reach the server. Check your connection and try again.",
        });
      } else if (err.response?.status === 503) {
        setError({
          type: 'walrus',
          message: err.response.data?.detail?.error || 'Memory service unavailable.',
        });
      } else {
        setError({
          type: 'server',
          message: 'Failed to load contradictions. Please try again.',
        });
      }
    } finally {
      setFetchingContradictions(false);
    }
  }, []);

  return {
    messages,
    sendingStatement,
    fetchingHistory,
    fetchingContradictions,
    error,
    contradictions,
    userId,
    showSlowIndicator,
    setUserId,
    submitStatement,
    fetchHistory,
    fetchContradictions,
    clearError,
  };
}
