const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

const userRoutes = require('./routes/users');
const authRoutes = require('./routes/auth');

app.use(express.json());
app.use('/api/users', userRoutes);
app.use('/api/auth', authRoutes);

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
