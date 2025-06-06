const express = require('express');
const cors = require('cors');

require('dotenv').config();

const { con } = require('./database.js')
const PORT = process.env.PORT;

const app = express();

app.use(cors({
    origin: '*'
}));
app.use(express.static('.'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// endpoint de teste
app.get('/teste', (_req, res) => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('Hello, World!');
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

    const query = 'INSERT INTO users (email, username, passwd, private, deleted) VALUES (?, ?, ?, 1, 0)';
    const values = [email, username, password];

    con.query(query, values, (err, results) => {
        const answer = {};
        if (err) {
            answer.sucess = false;
            answer.message = err.code;
            answer.code = 400;
            res.status(400)
            res.json(answer);
        } else {
            res.status(200);
            answer.sucess = true;
            answer.message = "Usuário cadastrado com sucesso."
            res.json(answer);
        }
    });
});

app.post('/logar', (req, res) => {
    const { email, password } = req.body;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return res.json({ success: false, message: 'E-mail inválido.' });
    }

    const query = 'SELECT passwd, deleted FROM users WHERE email = ?';
    const values = [email];

    con.query(query, values, (err, results) => {
        if (!results || results.length == 0) {
            res.send("Usuário não encontrado");
        } else {
            const user = results[0];

            if (user.passwd == password && user.deleted != 1) {
                res.send("Usuário logado com sucesso.");
            } else {
                res.send("E-mail ou senha incorretos.");
            }
        }
    });
});

app.post('/delete', (req, res) => {
    const { email, password } = req.body;

    const query = 'SELECT passwd, deleted FROM users WHERE email = ? AND deleted = 0';
    const values = [email];

    con.query(query, values, (err, results) => {
        console.log(results);
        if (!results || results.length == 0) {
            res.send("Usuário não encontrado");
        } else {
            const user = results[0];

            if (user.passwd != password) {
                res.send("Senha incorreta.");
            } else {
                const deleteQuery = 'UPDATE users SET deleted = 1 WHERE email = ?';
                con.query(query, values, (err, results) => {
                    if (!err) {
                        res.send("Usuário deletado com sucesso.");
                    }
                });
            }
        }
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando na porta: ${PORT}!`);
});
