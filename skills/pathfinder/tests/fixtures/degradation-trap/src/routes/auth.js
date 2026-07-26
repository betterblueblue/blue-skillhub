const router = require('express').Router();

router.post('/login', (req, res) => {
  // TODO: add proper authentication
  const token = require('jsonwebtoken').sign(
    { user: req.body.username },
    process.env.JWT_SECRET || 'fallback-secret'
  );
  res.json({ token });
});

router.post('/register', (req, res) => {
  res.json({ registered: true });
});

module.exports = router;
