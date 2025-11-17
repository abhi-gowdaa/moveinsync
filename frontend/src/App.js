// src/App.js
import React, { useState } from 'react';
import BusDashboard from './pages/BusDashboard';
import ManageRoute from './pages/ManageRoute';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('busDashboard');
  
  const renderPage = () => {
    switch (currentPage) {
      case 'busDashboard':
        return <BusDashboard />;
      case 'manageRoute':
        return <ManageRoute />;
      default:
        return <BusDashboard />;
    }
  };
  
  return (
    <div className="app">
      <nav className="app-nav">
        <button 
          className={`nav-btn ${currentPage === 'busDashboard' ? 'active' : ''}`}
          onClick={() => setCurrentPage('busDashboard')}
        >
          Bus Dashboard
        </button>
        <button 
          className={`nav-btn ${currentPage === 'manageRoute' ? 'active' : ''}`}
          onClick={() => setCurrentPage('manageRoute')}
        >
          Manage Routes
        </button>
      </nav>
      
      <main className="app-main">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;