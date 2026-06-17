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
    <div className="h-screen flex flex-col">
      <header className="shrink-0">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-lg font-semibold gradient-text tracking-tight">
              Hot Take Tracker
            </h1>
            <p className="text-xs text-secondary mt-0.5">
              Catch yourself contradicting your own opinions
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={userIdInput}
                onChange={(e) => setUserIdInput(e.target.value)}
                onKeyDown={handleUserIdKeyDown}
                placeholder="Enter your name..."
                className="w-56 glass rounded px-3.5 py-2 text-sm text-primary placeholder-glass-white outline-none transition-all duration-200 focus:shadow-glow focus:bg-glass-hover"
              />
              <Button variant="ghost" onClick={handleUserIdSubmit} disabled={!userIdInput.trim()}>
                Set
              </Button>
            </div>

            {userId && (
              <Button variant="ghost" onClick={() => setReceiptsOpen(true)}>
                Receipts
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-3xl mx-auto w-full px-4 pt-2 shrink-0">
        {error && error.type !== 'validation' && (
          <ErrorBanner error={error} onDismiss={clearError} />
        )}
      </div>

      {fetchingHistory && (
        <div className="max-w-3xl mx-auto w-full px-4 pt-3 shrink-0">
          <div className="flex items-center gap-2 text-xs text-secondary">
            <span className="w-1 h-1 rounded-full bg-accent-indigo animate-pulse" />
            Loading history...
          </div>
        </div>
      )}

      <ConversationFeed messages={messages} showSlowIndicator={showSlowIndicator} />

      <div className="max-w-3xl mx-auto w-full px-4 shrink-0">
        <StatementInput
          onSubmit={handleSubmitStatement}
          disabled={sendingStatement || !userId}
          error={error}
        />
        {!userId && (
          <p className="text-[11px] text-secondary text-center pb-4 -mt-2">
            Enter a name above to start tracking your takes
          </p>
        )}
      </div>

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
