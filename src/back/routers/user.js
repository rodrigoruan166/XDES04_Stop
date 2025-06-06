const { Router } = require('express');
const { con } = require("../database.js");
const HTTP_CODES = require("../../helpers/codes.js");

const app = Router();

app.post("/cadastrar", (req, res) => {
	const { email, username, password } = req.body;

    console.log(req.body);

	if (!email || !username || !password) {
		return res.json({
			success: false,
			message: "Todos os campos são obrigatórios.",
			code: HTTP_CODES.BAD_REQUEST,
		});
	}

	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(email)) {
		return res.json({
			success: false,
			message: "E-mail inválido.",
			code: HTTP_CODES.BAD_REQUEST,
		});
	}

	const query =
		"INSERT INTO users (email, username, passwd, private, deleted) VALUES (?, ?, ?, 1, 0)";
	const values = [email, username, password];

	con.query(query, values, (err, results) => {
		const answer = {};
		if (!results) {
			answer.success = false;
			answer.message = err.code;
			answer.code = HTTP_CODES.BAD_REQUEST;
			res.status(HTTP_CODES.BAD_REQUEST);
			res.json(answer);
		} else {
			res.status(HTTP_CODES.OK);
			answer.success = true;
			answer.message = "Usuário cadastrado com sucesso.";
			res.json(answer);
		}
	});
});

app.post("/logar", (req, res) => {
	const { email, password } = req.body;

	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(email)) {
		return res.json({ success: false, message: "E-mail inválido." });
	}

	const query = "SELECT passwd, deleted FROM users WHERE email = ?";
	const values = [email];

	con.query(query, values, (err, results) => {
        const answer = {};
		if (!results || results.length == 0) {
            answer.success = false;
            answer.message = "Usuário não encontrado";
            answer.code = HTTP_CODES.BAD_REQUEST;
			res.json(answer);
		} else {
			const user = results[0];

			if (user.passwd == password && user.deleted != 1) {
                answer.success = true;
                answer.message = "Usuário logado com sucesso";
                answer.code = HTTP_CODES.OK;
			} else {
                answer.success = false;
                answer.message = "Senha incorreta";
                answer.code = HTTP_CODES.BAD_REQUEST;
			}

            res.json(answer);
		}
	});
});

app.post("/delete", (req, res) => {
	const { email, password } = req.body;

	const query =
		"SELECT passwd, deleted FROM users WHERE email = ? AND deleted = 0";
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
				const deleteQuery = "UPDATE users SET deleted = 1 WHERE email = ?";
				con.query(query, values, (err, results) => {
					if (!err) {
						res.send("Usuário deletado com sucesso.");
					}
				});
			}
		}
	});
});

module.exports = app;