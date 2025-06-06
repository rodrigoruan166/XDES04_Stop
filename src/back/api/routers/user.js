const { Router } = require("express");
const { con } = require("../database.js");
const HTTP_CODES = require("../helpers/codes.js");

const app = Router();

app.post("/cadastrar", (req, res) => {
	const { email, username, password } = req.body;

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
			console.log(results);
			answer.success = false;
			answer.message = err.code;
			answer.code = HTTP_CODES.BAD_REQUEST;
			res.status(HTTP_CODES.BAD_REQUEST);
		} else {
			res.status(HTTP_CODES.OK);
			answer.success = true;
			answer.message = "Usuário cadastrado com sucesso.";
		}

		res.json(answer);
	});
});

app.post("/logar", (req, res) => {
	const { email, password } = req.body;

	if (!email || !password) {
		return res.json({ success: false, message: "Campos não preenchidos." });
	}

	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(email)) {
		return res.json({ success: false, message: "E-mail inválido." });
	}

	const query =
		"SELECT username, email, passwd, private, avatar FROM users WHERE email = ?";
	const values = [email];

	con.query(query, values, (err, results) => {
		const answer = {};
		if (!results || results.length == 0) {
			answer.success = false;
			answer.message = "Usuário não encontrado";
			answer.code = HTTP_CODES.BAD_REQUEST;
		} else {
			const user = results[0];

			if (user.passwd == password && user.deleted != 1) {
				answer.success = true;
				answer.message = JSON.stringify({
					username: user.username,
					email: user.email,
					private: user.private,
					avatar: user.avatar
				});
				answer.code = HTTP_CODES.OK;
			} else if (user.deleted == 1) {
				answer.success = false;
				answer.message = "Usuário não encontrado";
				answer.code = HTTP_CODES.BAD_REQUEST;
			} else {
				answer.success = false;
				answer.message = "Senha incorreta";
				answer.code = HTTP_CODES.BAD_REQUEST;
			}
		}

		res.json(answer);
	});
});

app.post("/editar", (req, res) => {
	const { username, email, novoEmail, avatar, private, password, novoPassword } = req.body;

	if (!email || !password || !username) {
		return res.json({ success: false, message: "Campos não preenchidos." });
	}

	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(email)) {
		return res.json({ success: false, message: "E-mail inválido." });
	}

	const queryLook = "SELECT passwd FROM users WHERE email = ?";
	const valuesLook = [email];

	con.query(queryLook, valuesLook, (err, results) => {
		const answer = {};

		if (!results || results.length == 0) {
			answer.success = false;
			answer.message = 'Erro ao editar o usuário';
			answer.code = HTTP_CODES.BAD_REQUEST;
			res.json(answer);
			return;
		}

		const user = results[0];

		if (user.passwd != password) {
			answer.success = false;
			answer.message = 'Senha incorreta';
			answer.code = HTTP_CODES.BAD_REQUEST;
			res.json(answer);
			return;
		}

		const query =
		"UPDATE users SET username = ?, email = ?, avatar = ?, private = ?, passwd = ? WHERE email = ?";
		const values = [username, novoEmail, avatar, private, novoPassword, email];

		con.query(query, values, (err, results) => {
			const answer = {};

			if (err) {
				answer.success = false;
				answer.message = err.message;
				answer.code = HTTP_CODES.BAD_REQUEST;
			} else {
				answer.success = true;
				answer.message = "Dados alterados com sucesso";
				answer.code = HTTP_CODES.OK;
			}

			res.json(answer);
		});
	});
});

app.post("/delete", (req, res) => {
	const { email, password } = req.body;

	const query =
		"SELECT passwd, deleted FROM users WHERE email = ? AND deleted = 0";
	const values = [email];

	con.query(query, values, (err, results) => {
		const answer = {};

		if (results.length == 0) {
			answer.success = false;
			answer.message = "Usuário não encontrado";
			answer.code = HTTP_CODES.BAD_REQUEST;
			return res.json(answer);
		}

		const user = results[0];

		if (user.passwd != password) {
			answer.success = false;
			answer.message = "Senha incorreta";
			answer.code = HTTP_CODES.BAD_REQUEST;
			return res.json(answer);
		}

		const deleteQuery = "UPDATE users SET deleted = 1 WHERE email = ?";
		con.query(deleteQuery, values, (err, deleteResults) => {
			if (!err) {
				answer.success = true;
				answer.message = "Usuário deletado com sucesso";
				answer.code = HTTP_CODES.OK;
			} else {
				answer.success = false;
				answer.message = "Erro ao deletar o usuário";
				answer.code = HTTP_CODES.BAD_REQUEST;
			}

			res.json(answer);
		});
	});
});

module.exports = app;
