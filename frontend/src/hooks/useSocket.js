import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

export const useSocket = (token, onNew, onDeleted, onCleared) => {
  const socketRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    const socket = io(process.env.REACT_APP_API_URL || 'http://localhost:5000', {
      auth: { token },
    });

    socket.on('connect', () => console.log('Socket connected'));
    socket.on('disconnect', () => console.log('Socket disconnected'));

    socket.on('clipboard:new', (entry) => {
      if (onNew) onNew(entry);
    });

    socket.on('clipboard:deleted', (id) => {
      if (onDeleted) onDeleted(id);
    });

    socket.on('clipboard:cleared', () => {
      if (onCleared) onCleared();
    });

    socketRef.current = socket;

    return () => socket.disconnect();
  }, [token]); // eslint-disable-line

  return socketRef;
};
