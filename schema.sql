DROP TABLE IF EXISTS chat_logs;
CREATE TABLE chat_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ia TEXT NOT NULL,
  mensagem TEXT NOT NULL,
  resposta TEXT NOT NULL,
  timestamp TEXT NOT NULL
);