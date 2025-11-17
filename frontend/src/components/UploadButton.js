// src/components/UploadButton.js
import React, { useRef } from 'react';
import './UploadButton.css';
import AttachFileIcon from '@mui/icons-material/AttachFile';

const UploadButton = ({ onUpload, disabled }) => {
  const fileInputRef = useRef(null);
  
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      onUpload(file);
    }
    // Reset the input value to allow selecting the same file again
    event.target.value = '';
  };
  
  const handleClick = () => {
    fileInputRef.current.click();
  };
  
  return (
    <div className="upload-button-container">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      <button 
        onClick={handleClick}
        disabled={disabled}
        className="upload-btn"
        title="Upload image"
      >
        <AttachFileIcon />
      </button>
    </div>
  );
};

export default UploadButton;