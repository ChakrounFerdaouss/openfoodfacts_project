require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/food_db';

const app = express();
app.use(cors());
app.use(express.json());

// ----- Mongoose model -----
const productSchema = new mongoose.Schema({
  barcode: { type: String, unique: true, index: true },
  nom: String,
  marque: String,
  categorie: String, // stored as comma-separated
  nutriscore: String,
  labels: String,
  source_url: String
}, { timestamps: true });

// Utiliser la collection exacte "produits"
const Product = mongoose.model('Produit', productSchema, 'produits');

// ----- Connect MongoDB -----
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connecté à food_db'))
  .catch(err => { console.error('Mongo connect error', err); process.exit(1); });

// ----- Routes -----
// GET /api/products
// Query params: q (text search), nutri, brand, category, page, limit, sort
app.get('/api/products', async (req, res) => {
  try {
    const {
      q, nutri, brand, category,
      page = 1, limit = 20, sort = 'nom'
    } = req.query;

    const filter = {};
    if (q) {
      filter.$or = [
        { nom: new RegExp(q, 'i') },
        { marque: new RegExp(q, 'i') },
        { categorie: new RegExp(q, 'i') }
      ];
    }
    if (nutri) filter.nutriscore = nutri.toUpperCase();
    if (brand) filter.marque = new RegExp(brand, 'i');
    if (category) filter.categorie = new RegExp(category, 'i');

    const skip = (Math.max(1, parseInt(page)) - 1) * Math.max(1, parseInt(limit));
    const docs = await Product.find(filter)
      .sort(sort === 'nom' ? { nom: 1 } : { createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit))
      .lean();

    const total = await Product.countDocuments(filter);

    res.json({ data: docs, total, page: parseInt(page), limit: parseInt(limit) });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/stats/nutriscore
app.get('/api/stats/nutriscore', async (req, res) => {
  try {
    const agg = await Product.aggregate([
      { $group: { _id: { $ifNull: ['$nutriscore', 'UNKNOWN'] }, count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]);
    res.json(agg.map(x => ({ nutriscore: x._id, count: x.count })));
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/stats/categories (top N)
app.get('/api/stats/categories', async (req, res) => {
  try {
    const topN = parseInt(req.query.top) || 10;
    const agg = await Product.aggregate([
      { $project: { cats: { $split: [{ $ifNull: ['$categorie', ''] }, ', '] } } },
      { $unwind: '$cats' },
      { $match: { cats: { $ne: '' } } },
      { $group: { _id: '$cats', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: topN }
    ]);
    res.json(agg.map(x => ({ category: x._id, count: x.count })));
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET single product
app.get('/api/products/:barcode', async (req, res) => {
  try {
    const doc = await Product.findOne({ barcode: req.params.barcode }).lean();
    if (!doc) return res.status(404).json({ error: 'Not found' });
    res.json(doc);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health
app.get('/api/health', (req, res) => res.json({ ok: true }));

// Start
app.listen(PORT, () => console.log(`API running on http://localhost:${PORT}`));
