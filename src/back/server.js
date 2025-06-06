const express = require('express');
const cors = require('cors');
const { con } = require('./database.js')

const app = express();
const PORT = 3000;

app.use(cors({
    origin: '*'
}));
app.use(express.static('.'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get('/teste', (req, res) => {
    console.log("HELLO");
});

app.post('/cadastrar', (req, res) => {
    const { email, username, password } = req.body;

    if (!email || !username || !password) {
        return res.json({ success: false, message: 'Todos os campos são obrigatórios.' });
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return res.json({ success: false, message: 'E-mail inválido.' });
    }
});

app.listen(PORT, () => {
    console.log(`Servidor rodando!`);
});
