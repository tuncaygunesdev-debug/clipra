const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const clipboardRoutes = require('./routes/clipboard');
const { verifySocketToken } = require('./middleware/auth');

const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: process.env.CLIENT_URL || 'http://localhost:3000',
    methods: ['GET', 'POST'],
    credentials: true,
  },
});

app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3000',
  credentials: true,
}));
app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/clipboard', clipboardRoutes);

// Make io accessible in routes
app.set('io', io);

// Socket.io authentication middleware
io.use(verifySocketToken);

io.on('connection', (socket) => {
  const userId = socket.userId;
  socket.join(`user:${userId}`);
  console.log(`User ${userId} connected via socket`);

  socket.on('disconnect', () => {
    console.log(`User ${userId} disconnected`);
  });
});

mongoose
  .connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/clipsync')
  .then(() => {
    console.log('MongoDB connected');
    const PORT = process.env.PORT || 5000;
    server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
  })
  .catch((err) => console.error('MongoDB connection error:', err));
