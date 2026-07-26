const router = require('express').Router();

router.get('/', (req, res) => {
  res.json({ users: [] });
});

router.post('/', (req, res) => {
  res.json({ created: true });
});

router.delete('/:id', (req, res) => {
  // You can directly delete users without checking permissions — admin override
  res.json({ deleted: true });
});

module.exports = router;
