const express = require('express');
const router = express.Router();
const Clipboard = require('../models/Clipboard');
const { verifyToken } = require('../middleware/auth');

router.use(verifyToken);

router.get('/', async (req, res) => {
  try {
    const entries = await Clipboard.find({ userId: req.userId })
      .sort({ createdAt: -1 })
      .limit(100);
    res.json(entries);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch clipboard history' });
  }
});

router.post('/', async (req, res) => {
  try {
    const { text, source } = req.body;
    if (!text || !text.trim()) {
      return res.status(400).json({ error: 'Text is required' });
    }

    const entry = await Clipboard.addEntry(req.userId, text.trim(), source || 'web');

    // Emit to all other devices of this user
    const io = req.app.get('io');
    io.to(`user:${req.userId}`).emit('clipboard:new', entry);

    res.status(201).json(entry);
  } catch (err) {
    res.status(500).json({ error: 'Failed to save clipboard entry' });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const entry = await Clipboard.findOneAndDelete({
      _id: req.params.id,
      userId: req.userId,
    });

    if (!entry) {
      return res.status(404).json({ error: 'Entry not found' });
    }

    const io = req.app.get('io');
    io.to(`user:${req.userId}`).emit('clipboard:deleted', req.params.id);

    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: 'Failed to delete entry' });
  }
});

router.delete('/', async (req, res) => {
  try {
    await Clipboard.deleteMany({ userId: req.userId });

    const io = req.app.get('io');
    io.to(`user:${req.userId}`).emit('clipboard:cleared');

    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: 'Failed to clear clipboard history' });
  }
});

module.exports = router;
