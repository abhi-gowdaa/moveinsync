// src/components/AudioButton.js
import React, { useState, useRef } from 'react';
import MicIcon from '@mui/icons-material/Mic';

const AudioButton = ({ onTranscription, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Transcribe audio using Groq API
  const transcribeAudio = async (blob) => {
    try {
      // Convert blob to file
      const file = new File([blob], 'recording.webm', { type: 'audio/webm' });

      // Create form data
      const formData = new FormData(); 
      formData.append('file', file);
      formData.append('model', 'whisper-large-v3-turbo');
      formData.append('temperature', '0');
      formData.append('response_format', 'verbose_json');

      // Make API call to Groq
      const response = await fetch('https://api.groq.com/openai/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.REACT_APP_GROQ_API_KEY}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      if (data.text) {
        onTranscription(data.text);
      } else {
        console.error('No transcription text received:', data);
      }
    } catch (error) {
      console.error('Transcription error:', error);
      alert('Transcription failed. Please try again.');
    }
  };

  // Toggle recording
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <button
      className={`audio-btn ${isRecording ? 'recording' : ''}`}
      onClick={toggleRecording}
      disabled={disabled}
      title={isRecording ? 'Stop recording' : 'Start recording'}
    >
      {isRecording ? '🔴' : <MicIcon />}
    </button>
  );
};

export default AudioButton;