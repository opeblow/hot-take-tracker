import { useState, useCallback } from 'react';
import useHotTake from './hooks/useHotTake.js';
import StatementInput from './components/StatementInput.jsx';
import ConversationFeed from './components/ConversationFeed.jsx';
import ReceiptsPanel from './components/ReceiptsPanel.jsx';
import ErrorBanner from './components/ui/ErrorBanner.jsx';
import Button from './components/ui/Button.jsx';

export default function App() {
  const {
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
  } = useHotTake();

  const [receiptsOpen, setReceiptsOpen] = useState(false);
  const [userIdInput, setUserIdInput] = useState('');

  const handleUserIdSubmit = useCallback(() => {
    const trimmed = userIdInput.trim();
    if (!trimmed) return;
    setUserId(trimmed);
    fetchHistory(trimmed).then(() => {});
  }, [userIdInput, setUserId, fetchHistory]);

  const handleUserIdKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleUserIdSubmit();
    }
  };

  const handleSubmitStatement = useCallback(
    async (text) => {
      return await submitStatement(text);
    },
    [submitStatement],
  );

  return (
    <div className="h-screen flex flex-col bg-[#09090B]">
      {/* Top bar */}
      <header className="border-b border-border shrink-0">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <h1 className="text-base font-semibold text-primary tracking-tight">
            Hot Take Tracker
          </h1>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={userIdInput}
                onChange={(e) => setUserIdInput(e.target.value)}
                onKeyDown={handleUserIdKeyDown}
                placeholder="Enter any name to start tracking your takes"
                className="w-64 bg-surface border border-border rounded px-3 py-1.5 text-sm text-primary placeholder-secondary outline-none transition-colors duration-150 focus:border-accent-indigo"
              />
              <Button variant="ghost" onClick={handleUserIdSubmit} disabled={!userIdInput.trim()}>
                Set
              </Button>
            </div>

            {userId && (
              <Button variant="ghost" onClick={() => setReceiptsOpen(true)}>
                View Receipts
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Error banner */}
      <div className="max-w-3xl mx-auto w-full px-4 pt-3 shrink-0">
        {error && error.type !== 'validation' && (
          <ErrorBanner error={error} onDismiss={clearError} />
        )}
      </div>

      {/* Loading indicator for history */}
      {fetchingHistory && (
        <div className="max-w-3xl mx-auto w-full px-4 pt-3 shrink-0">
          <div className="text-xs text-secondary animate-pulse">Loading history...</div>
        </div>
      )}

      {/* Conversation */}
      <ConversationFeed messages={messages} showSlowIndicator={showSlowIndicator} />

      {/* Input */}
      <div className="max-w-3xl mx-auto w-full px-4 shrink-0">
        <StatementInput
          onSubmit={handleSubmitStatement}
          disabled={sendingStatement || !userId}
          error={error}
        />
        {!userId && (
          <p className="text-[11px] text-secondary text-center pb-3 -mt-2">
            Enter a name above to start tracking your takes
          </p>
        )}
      </div>

      {/* Receipts panel */}
      <ReceiptsPanel
        open={receiptsOpen}
        onClose={() => setReceiptsOpen(false)}
        userId={userId}
        contradictions={contradictions}
        loading={fetchingContradictions}
        fetchContradictions={fetchContradictions}
      />
    </div>
  );
}
