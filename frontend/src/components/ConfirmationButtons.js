// src/components/ConfirmationButtons.js
import React from 'react';
import './ConfirmationButtons.css';

const ConfirmationButtons = ({ onConfirm, onCancel, disabled }) => {
  return (
    <div className="confirmation-buttons">
      <p>This action may have consequences. Do you want to proceed?</p>
      <div className="button-group">
        <button 
          onClick={onConfirm} 
          disabled={disabled}
          className="confirm-btn"
        >
          Yes, Proceed
        </button>
        <button 
          onClick={onCancel} 
          disabled={disabled}
          className="cancel-btn"
        >
          No, Cancel
        </button>
      </div>
    </div>
  );
};

export default ConfirmationButtons;