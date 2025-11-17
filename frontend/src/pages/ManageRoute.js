// src/pages/ManageRoute.js
import React, { useState, useEffect } from 'react';
import ChatDrawer from '../components/ChatDrawer';
import { useChat } from '../hooks/useChat';
import apiService from '../services/api';
import './ManageRoute.css';

const ManageRoute = () => {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [activeTab, setActiveTab] = useState('Active Routes');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const { isDrawerOpen, setIsDrawerOpen } = useChat();
  
  useEffect(() => {
    const fetchRoutes = async () => {
      try {
        const data = await apiService.getRoutes();
        setRoutes(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching routes:', error);
        setLoading(false);
      }
    };
    
    fetchRoutes();
  }, []);
  
  // Filter routes based on search and filter
  const filteredRoutes = routes.filter(route => {
    const matchesSearch = route.route_display_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          route.route_id.toString().includes(searchTerm);
    const matchesStatus = filterStatus === 'all' || 
                         (filterStatus === 'active' && route.status === 'ACTIVE') ||
                         (filterStatus === 'deactivated' && route.status === 'DEACTIVATED');
    return matchesSearch && matchesStatus;
  });
  
  // Handle row click
  const handleRouteClick = (route) => {
    setSelectedRoute(route);
  };
  
  // Get status class for styling
  const getStatusClass = (status) => {
    if (status === 'ACTIVE') return 'status-active';
    if (status === 'DEACTIVATED') return 'status-deactivated';
    return 'status-pending';
  };
  
  return (
    <div className="manage-route">
      {/* Header with navigation */}
      <div className="page-header">
        <h1>Manage Routes</h1>
        <div className="header-actions">
          <button className="btn-history">History</button>
          <button className="btn-download">Download</button>
          <button className="btn-routes">+ Routes</button>
        </div>
      </div>
      
      {/* Search and filters */}
      <div className="search-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search route name or ID"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <i className="search-icon">🔍</i>
        </div>
        <div className="filter-btn">
          <i className="filter-icon">⚙️</i>
          Filters
        </div>
      </div>
      
      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'Active Routes' ? 'active' : ''}`}
          onClick={() => setActiveTab('Active Routes')}
        >
          Active Routes
        </button>
        <button 
          className={`tab ${activeTab === 'Deactivated Routes' ? 'active' : ''}`}
          onClick={() => setActiveTab('Deactivated Routes')}
        >
          Deactivated Routes
        </button>
      </div>
      
      {/* Main content - Table */}
      <div className="routes-table-container">
        <table className="routes-table">
          <thead>
            <tr>
              <th>Route ID</th>
              <th>Route Name</th>
              <th>Direction</th>
              <th>Shift Time</th>
              <th>Route Start Point</th>
              <th>Route End Point</th>
              <th>Capacity</th>
              <th>Allowed Waitlist</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="9" className="loading-row">Loading routes...</td>
              </tr>
            ) : filteredRoutes.length > 0 ? (
              filteredRoutes.map(route => (
                <tr 
                  key={route.route_id} 
                  className={`route-row ${selectedRoute?.route_id === route.route_id ? 'selected' : ''}`}
                  onClick={() => handleRouteClick(route)}
                >
                  <td>{route.route_id}</td>
                  <td>{route.route_display_name}</td>
                  <td>{route.direction}</td>
                  <td>{route.shift_time}</td>
                  <td>{route.start_point}</td>
                  <td>{route.end_point}</td>
                  <td>
                    {route.capacity} 
                    <i className="edit-icon">✏️</i>
                  </td>
                  <td>
                    {route.allowed_waitlist} 
                    <i className="edit-icon">✏️</i>
                  </td>
                  <td>
                    <div className="action-menu">
                      <i className="more-icon">⋮</i>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="9" className="no-data">No routes found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Pagination */}
      <div className="pagination">
        <div className="rows-per-page">
          Rows per page: 
          <select>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
        <div className="page-info">
          Showing 1-25 of {filteredRoutes.length} items
        </div>
        <div className="page-navigation">
          <button className="page-btn">{'<'}</button>
          <button className="page-btn active">1</button>
          <button className="page-btn">2</button>
          <button className="page-btn">3</button>
          <button className="page-btn">{'>'}</button>
        </div>
      </div>
      
      {/* Floating Chat Button */}
      <button 
        className="floating-chat-btn"
        onClick={() => setIsDrawerOpen(true)}
        aria-label="Open chat"
      >
        💬
      </button>
      
      {/* Chat Drawer */}
      <ChatDrawer isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} currentPage="manageRoute" />
    </div>
  );
};

export default ManageRoute;