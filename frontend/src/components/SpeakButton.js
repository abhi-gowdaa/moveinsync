import React from 'react';
import { useAudio } from '../hooks/useAudio';
import './SpeakButton.css';

const SpeakButton = ({ text, disabled }) => {
  const { speak, stopSpeaking, isSpeaking } = useAudio();

  const handleClick = () => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      speak(text);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || !text}
      className="speak-btn"
      title={isSpeaking ? "Stop speaking" : "Play text as speech"}
    >
      {isSpeaking ? '🔊' : '🔈'}
    </button>
  );
};

export default SpeakButton;