// src/pages/BusDashboard.js
import React, { useState, useEffect } from 'react';
import ChatDrawer from '../components/ChatDrawer';
import { useChat } from '../hooks/useChat';
import apiService from '../services/api';
import './BusDashboard.css';

const BusDashboard = () => {
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [date, setDate] = useState('16/11/2025');
  const [routeFilter, setRouteFilter] = useState('');
  const { isDrawerOpen, setIsDrawerOpen } = useChat();
  
  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const data = await apiService.getTrips();
        setTrips(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching trips:', error);
        setLoading(false);
      }
    };
    
    fetchTrips();
  }, []);
  
  // Filter trips based on search
  const filteredTrips = trips.filter(trip => {
    return trip.display_name.toLowerCase().includes(routeFilter.toLowerCase());
  });
  
  // Handle trip selection
  const handleTripClick = (trip) => {
    setSelectedTrip(trip);
  };
  
  // Calculate statistics
  const stats = {
    vehiclesNotAssigned: trips.filter(t => !t.deployment).length,
    tripsNotGenerated: trips.filter(t => t.booking_status_percentage === 0).length,
    employeesScheduled: trips.reduce((sum, trip) => sum + (trip.employee_count || 0), 0),
    ongoingTrips: trips.filter(t => t.live_status === 'ON_GOING').length
  };
  
  return (
    <div className="bus-dashboard">
      {/* Top Navigation */}
      <div className="top-nav">
        
        
        <div className="action-bar">
          <div className="date-selector">
            <input 
              type="text" 
              value={date} 
              onChange={(e) => setDate(e.target.value)}
              placeholder="Select date"
            />
          </div>
          
          <div className="route-selector">
            <select>
              <option value="">All Routes</option>
              <option value="route1">Route 1</option>
              <option value="route2">Route 2</option>
            </select>
          </div>
          
          <div className="search-box">
            <input 
              type="text" 
              placeholder="Search Name/Id" 
              value={routeFilter}
              onChange={(e) => setRouteFilter(e.target.value)}
            />
            <i className="search-icon">🔍</i>
          </div>
         

          <button className="btn-filters">Filters</button>
          <button className="btn-pause">Pause Operations</button>
          <button className="btn-download">Download</button>
          <button className="btn-switch">Switch to Old UI</button>
        
          </div>
      </div>
      
      {/* Statistics Cards */}
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-header">
            <span>Vehicles Not Assigned</span>
          </div>
          <div className="stat-value">{stats.vehiclesNotAssigned}</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <span>Trips Not Generated</span>
          </div>
          <div className="stat-value">{stats.tripsNotGenerated}</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <span>Employees Scheduled</span>
          </div>
          <div className="stat-value">{stats.employeesScheduled}</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <span>Ongoing Trips</span>
          </div>
          <div className="stat-value">{stats.ongoingTrips}</div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="dashboard-content">
        {/* Left Panel - Trip List */}
        <div className="trips-panel">
          <div className="panel-actions">
            <button className="action-btn">Track Route</button>
            <button className="action-btn">Generate Tripsheet</button>
            <button className="action-btn">Merge Route</button>
          </div>
          
          <div className="trips-list">
            {loading ? (
              <div className="loading">Loading trips...</div>
            ) : filteredTrips.length > 0 ? (
              filteredTrips.map(trip => (
                <div 
                  key={trip.trip_id} 
                  className={`trip-item ${selectedTrip?.trip_id === trip.trip_id ? 'selected' : ''}`}
                  onClick={() => handleTripClick(trip)}
                >
                  <div className="trip-checkbox">
                    <input type="checkbox" />
                  </div>
                  <div className="trip-info">
                    <div className="trip-name">{trip.display_name}</div>
                    <div className="trip-booking">
                      <span className={`booking-percentage ${trip.booking_status_percentage > 0 ? 'booked' : 'not-booked'}`}>
                        {trip.booking_status_percentage}% booked
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">No trips found</div>
            )}
          </div>
        </div>
        
        {/* Right Panel - Trip Details */}
        <div className="trip-details">
          {selectedTrip ? (
            <div className="trip-details-content">
              <div className="details-header">
                <h2>{selectedTrip.display_name}</h2>
                <div className="trip-duration">
                  Duration: {selectedTrip.duration || 'N/A'}
                </div>
              </div>
              
              <div className="details-stats">
                <div className="stat-badge">Planned Capacity: N/A</div>
                <div className="stat-badge">W/L: 0</div>
              </div>
              
              <div className="details-actions">
                <button className="btn-manage-vehicles">Manage Vehicles</button>
                <button className="btn-manage-bookings">Manage Bookings</button>
              </div>
              
              <div className="vehicle-section">
                <div className="section-header">
                  <h3>Add Vendor</h3>
                  <button className="btn-add-edit">Add/Edit Vehicle</button>
                </div>
                
                {selectedTrip.deployment ? (
                  <div className="vehicle-assigned">
                    <div className="vehicle-info">
                      <div className="vehicle-plate">{selectedTrip.deployment.vehicle.license_plate}</div>
                      <div className="driver-name">Driver: {selectedTrip.deployment.driver.name}</div>
                    </div>
                  </div>
                ) : (
                  <div className="vehicle-not-assigned">
                    <div className="vehicle-text">Vehicle not assigned yet</div>
                  </div>
                )}
              </div>
              
            </div>
          ) : (
            <div className="no-selection">
              <div className="no-selection-content">
                <p>Select a trip to view details</p>
              </div>
            </div>
          )}
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
      <ChatDrawer isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} currentPage="busDashboard" />
    </div>
  );
};

export default BusDashboard;