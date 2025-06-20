async function cadastrar(e) {
	e.preventDefault();

	const email = document.getElementById("email").value.trim();
	const username = document.getElementById("username").value.trim();
	const password = document.getElementById("password").value;

	const data = {
		email: email,
		username: username,
		password: password,
	};

	await fetch("https://xdes-04-stop.vercel.app/cadastrar", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	})
		.then((res) => res.json())
		.then((data) => {
			console.log(data);
			if (data.success) {
				alert("Usuário cadastrado com sucesso.");
				window.location.href = "./login.html";
			} else {
				if (data.message == "ER_DUP_ENTRY") {
					alert("Email ou username já cadastrados");
				} else {
					alert(data.message);
				}
			}
		})
		.catch((err) => alert("Erro ao cadastrar."));
}

async function entrar(e) {
	e.preventDefault();

	const email = document.getElementById("email").value.trim();
	const password = document.getElementById("password").value;

	const data = {
		email: email,
		password: password,
	};

	await fetch("https://xdes-04-stop.vercel.app/logar", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	})
		.then((res) => res.json())
		.then((data) => {
			if (data.success) {
				const info = JSON.parse(data.message);
				localStorage.setItem("username", info.username);
				localStorage.setItem("email", info.email);
				localStorage.setItem("avatar", info.avatar);
				localStorage.setItem("privacidade", info.private == 1 ? 'publico' : 'privado');
				localStorage.setItem("admin", info.admin);
				alert("Logado com sucesso.");
				window.location.href = "./home.html";
			} else {
				alert(data.message);
			}
		})
		.catch((err) => alert(err));
}

async function deletar(e) {
	e.preventDefault();

	const confirmar = confirm(
		"Tem certeza que deseja deletar seu perfil? Esta ação não pode ser desfeita."
	);

	if (!confirmar) {
		return;
	}

	const password = prompt(
		"Digite sua senha para confirmar a exclusão do perfil:"
	);

	if (!password) {
		alert("Senha inválida");
		return;
	}

	const email = window.localStorage.getItem('email');

	const data = {
		email: email,
		password: password,
	};

	await fetch("https://xdes-04-stop.vercel.app/delete", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	})
		.then((res) => res.json())
		.then((data) => {
			if (data.success) {
				alert(data.message);
				window.location.href = "./../index.html";
			} else {
				alert(data.message);
			}
		})
		.catch((err) => alert(err));
}
