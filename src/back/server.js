const express = require("express");
const cors = require("cors");

require("dotenv").config();

const user = require("./routers/user.js");
const PORT = process.env.PORT;
const app = express();

app.use(cors({ origin: "*" }));
app.use(express.static("."));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(user);

// endpoint de teste
app.get("/teste", (_req, res) => {
	res.statusCode = HTTP_CODES.OK;
	res.setHeader("Content-Type", "text/plain");
	res.end("Hello, World!");
});

app.listen(PORT, () => {
	console.log(`Servidor rodando na porta: ${PORT}!`);
});
