const mongoose = require('mongoose');

const clipboardSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true,
  },
  text: {
    type: String,
    required: true,
  },
  source: {
    type: String,
    enum: ['web', 'desktop-agent', 'mobile'],
    default: 'web',
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// Keep only last 100 entries per user
clipboardSchema.statics.addEntry = async function (userId, text, source = 'web') {
  const entry = await this.create({ userId, text, source });

  const count = await this.countDocuments({ userId });
  if (count > 100) {
    const oldest = await this.find({ userId })
      .sort({ createdAt: 1 })
      .limit(count - 100)
      .select('_id');
    await this.deleteMany({ _id: { $in: oldest.map((d) => d._id) } });
  }

  return entry;
};

module.exports = mongoose.model('Clipboard', clipboardSchema);
