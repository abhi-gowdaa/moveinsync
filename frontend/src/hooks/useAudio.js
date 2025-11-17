import { useState, useRef, useCallback } from 'react';
import { useInterval } from 'react-use';

export const useAudio = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const speechRef = useRef(null);

  // Check for browser support on mount
  useState(() => {
    const hasMediaRecorder = navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
    const hasSpeechSynthesis = 'speechSynthesis' in window;
    if (hasMediaRecorder && hasSpeechSynthesis) {
      setIsSupported(true);
    }
  }, []);

  // Timer for recording duration
  useInterval(
    () => {
      setRecordingTime(s => s + 1);
    },
    isRecording ? 1000 : null
  );

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        streamRef.current.getTracks().forEach(track => track.stop());
        setIsProcessing(true);
        
        // This is where you would send the blob to your backend
        // For now, we'll just return it via a callback
        if (mediaRecorder.onAudioReady) {
          mediaRecorder.onAudioReady(audioBlob);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check your permissions.');
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const speak = useCallback((text) => {
    if (!('speechSynthesis' in window) || !text) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    speechRef.current = utterance;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return {
    isRecording,
    recordingTime,
    isProcessing,
    isSpeaking,
    isSupported,
    startRecording,
    stopRecording,
    speak,
    stopSpeaking,
    formatTime,
    // Expose a way to set the callback
    setAudioCallback: (callback) => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.onAudioReady = callback;
      }
    }
  };
};