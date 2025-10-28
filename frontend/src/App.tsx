import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import "./App.css";
import CreateGame from "./pages/CreateGame";
import GameDetail from "./pages/GameDetail";
import RawAssetsPage from "./pages/RawAssetsPage";
import { GamesService } from "./client/services/GamesService";
import type { GameListItem } from "./client/models/GameListItem";

function Home() {
  const [games, setGames] = useState<GameListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await GamesService.listGamesGamesGet();
        setGames(response);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to fetch games");
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <h1>Romulus Game Engine</h1>

      <div style={{ marginBottom: "20px" }}>
        <Link
          to="/games/create"
          style={{
            display: "inline-block",
            padding: "10px 20px",
            backgroundColor: "#007bff",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
            marginRight: "10px",
          }}
        >
          Create New Game
        </Link>
        <Link
          to="/assets/images/raw"
          style={{
            display: "inline-block",
            padding: "10px 20px",
            backgroundColor: "#6c757d",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
          }}
        >
          View Assets
        </Link>
      </div>

      <h2>Games</h2>

      {loading && <p>Loading games...</p>}

      {error && (
        <div
          style={{
            color: "red",
            padding: "10px",
            border: "1px solid red",
            borderRadius: "4px",
            backgroundColor: "#fee",
          }}
        >
          Error: {error}
        </div>
      )}

      {!loading && !error && games.length === 0 && (
        <p>No games yet. Create your first game!</p>
      )}

      {!loading && !error && games.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {games.map((game) => (
            <li
              key={game.id}
              style={{
                marginBottom: "10px",
                padding: "15px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                backgroundColor: "#f9f9f9",
              }}
            >
              <Link
                to={`/games/${game.id}`}
                style={{
                  textDecoration: "none",
                  color: "#007bff",
                  fontSize: "18px",
                  fontWeight: "bold",
                }}
              >
                {game.name}
              </Link>
              <div
                style={{ fontSize: "12px", color: "#666", marginTop: "5px" }}
              >
                ID: {game.id}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/games/create" element={<CreateGame />} />
          <Route path="/games/:id" element={<GameDetail />} />
          <Route path="/assets/images/raw" element={<RawAssetsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
